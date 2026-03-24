"""
光谱分类模型训练模块
Spectrum Classification Model Training Module
提供模型训练、预测、保存和加载功能
支持Random Forest、SVM、Gradient Boosting三种模型
"""

import os
import numpy as np
from typing import List, Tuple, Optional, Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
import joblib
import time


def _load_single_file(args: Tuple[str, float, int]) -> Tuple[np.ndarray, str]:
    """加载单个文件（独立函数，用于多进程）"""
    filepath, min_wavelength, min_wl = args
    try:
        from .xlsx_reader import load_xlsx_spectrum
        
        wavelengths, intensities = load_xlsx_spectrum(filepath, min_wavelength)
        
        if len(intensities) < 10:
            return None, None
        
        features = np.zeros(2501 - min_wl, dtype=np.float32)
        for wl, intensity in zip(wavelengths, intensities):
            idx = int(wl) - min_wl
            if 0 <= idx < len(features):
                features[idx] = intensity
        
        category = os.path.basename(os.path.dirname(filepath))
        return features, category
    except Exception as e:
        return None, None


class SpectrumClassifier:
    """
    光谱分类器
    
    用于训练和预测光谱数据所属类别
    支持Random Forest、SVM、Gradient Boosting三种模型
    特征提取：将光谱数据按波长转换为固定长度的特征向量
    """
    
    def __init__(self, min_wavelength: int = 350, max_wavelength: int = 2500):
        """
        初始化分类器
        
        Args:
            min_wavelength: 最小波长（默认350nm）
            max_wavelength: 最大波长（默认2500nm）
        """
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None
        self.is_trained = False
        self.min_wavelength = min_wavelength
        self.max_wavelength = max_wavelength
        self.feature_length = max_wavelength - min_wavelength + 1
        self.load_progress = 0  # 加载进度 (0-100)
        self.total_files = 0     # 总文件数
        self.loaded_files = 0    # 已加载文件数
    
    def load_data_from_directory(self, data_dir: str, min_wavelength: float = 350,
                                 use_split_dirs: bool = False,
                                 progress_callback: Optional[Callable[[int], None]] = None) -> Tuple[np.ndarray, np.ndarray, 
                                                                       Optional[np.ndarray], Optional[np.ndarray],
                                                                       Optional[np.ndarray], Optional[np.ndarray]]:
        """
        从目录加载训练数据
        
        支持两种数据组织形式：
        1. 未分割：data_dir/category/file.xlsx
        2. 已分割：data_dir/train/category/file.xlsx, data_dir/val/category, data_dir/test/category
        
        Args:
            data_dir: 数据目录路径
            min_wavelength: 最小波长
            use_split_dirs: 是否使用已分割的目录结构
            progress_callback: 进度回调函数
            
        Returns:
            (X, y, X_val, y_val, X_test, y_test) 元组
        """
        X = []
        y = []
        X_val = None
        y_val = None
        X_test = None
        y_test = None
        
        if not os.path.isdir(data_dir):
            raise ValueError(f"Directory not found: {data_dir}")
        
        categories = sorted([d for d in os.listdir(data_dir) 
                           if os.path.isdir(os.path.join(data_dir, d))])
        
        if not categories:
            raise ValueError(f"No category directories found in {data_dir}")
        
        if use_split_dirs and 'train' in categories:
            return self._load_from_split_dirs(data_dir, min_wavelength, progress_callback)
        
        print(f"Found {len(categories)} categories: {categories}")
        
        for category in categories:
            category_dir = os.path.join(data_dir, category)
            files = [f for f in os.listdir(category_dir) 
                    if f.lower().endswith(('.xlsx', '.xls'))]
            
            print(f"Processing category '{category}' with {len(files)} files...")
            
            for filename in files:
                filepath = os.path.join(category_dir, filename)
                try:
                    from .xlsx_reader import parse_xlsx_file
                    data = parse_xlsx_file(filepath)
                    
                    mask = data.wavelengths >= min_wavelength
                    wavelengths = data.wavelengths[mask]
                    intensities = data.intensities[mask]
                    
                    if len(intensities) < 10:
                        continue
                    
                    features = self._extract_features(wavelengths, intensities)
                    X.append(features)
                    y.append(category)
                    
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    continue
        
        if not X:
            raise ValueError("No valid data loaded")
        
        return np.array(X), np.array(y), None, None, None, None
    
    def _load_from_split_dirs(self, data_dir: str, min_wavelength: float,
                              progress_callback: Optional[Callable[[int], None]] = None) -> Tuple:
        categories = sorted([d for d in os.listdir(os.path.join(data_dir, 'train'))
                           if os.path.isdir(os.path.join(data_dir, 'train', d))])
        
        print(f"Loading from split directories, found {len(categories)} categories")
        
        all_files = []
        for category in categories:
            for split_type in ['train', 'val', 'test']:
                split_dir = os.path.join(data_dir, split_type, category)
                if not os.path.exists(split_dir):
                    continue
                files = [f for f in os.listdir(split_dir)
                        if f.lower().endswith(('.xlsx', '.xls'))]
                for f in files:
                    all_files.append((os.path.join(split_dir, f), split_type, category))
        
        print(f"Total files to load: {len(all_files)}")
        
        X_train, y_train = [], []
        X_val, y_val = [], []
        X_test, y_test = [], []
        
        min_wl = self.min_wavelength
        
        self.total_files = len(all_files)
        self.loaded_files = 0
        
        start_time = time.time()
        
        with ProcessPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as executor:
            futures = {
                executor.submit(_load_single_file, (filepath, min_wavelength, min_wl)): (filepath, split_type, category)
                for filepath, split_type, category in all_files
            }
            
            completed = 0
            for future in as_completed(futures):
                filepath, split_type, category = futures[future]
                try:
                    features, _ = future.result()
                    if features is not None:
                        if split_type == 'train':
                            X_train.append(features)
                            y_train.append(category)
                        elif split_type == 'val':
                            X_val.append(features)
                            y_val.append(category)
                        else:
                            X_test.append(features)
                            y_test.append(category)
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")
                
                completed += 1
                self.loaded_files = completed
                self.load_progress = int(completed / len(all_files) * 50)
                
                if completed % 100 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / completed
                    print(f"Loaded {completed}/{len(all_files)} files... ({elapsed:.1f}s elapsed, {avg_time*1000:.1f}ms/file)")
        
        X_train = np.array(X_train) if X_train else np.array([])
        y_train = np.array(y_train) if y_train else np.array([])
        X_val = np.array(X_val) if X_val else None
        y_val = np.array(y_val) if y_val else None
        X_test = np.array(X_test) if X_test else None
        y_test = np.array(y_test) if y_test else None
        
        return X_train, y_train, X_val, y_val, X_test, y_test
    
    def detect_split_dirs(self, data_dir: str) -> bool:
        """
        检测是否为已分割的目录结构
        
        检查data_dir下是否存在train子目录
        
        Args:
            data_dir: 数据目录路径
            
        Returns:
            True表示是已分割结构
        """
        if not os.path.isdir(data_dir):
            return False
        subdirs = set(os.listdir(data_dir))
        return 'train' in subdirs and len(subdirs) >= 2
    
    def _extract_features(self, wavelengths: np.ndarray, intensities: np.ndarray) -> np.ndarray:
        """
        提取特征向量
        
        将光谱数据转换为固定长度的特征向量，使用插值处理不同波长间隔
        
        Args:
            wavelengths: 波长数组
            intensities: 强度数组
            
        Returns:
            特征向量
        """
        from scipy.interpolate import interp1d
        
        features = np.zeros(self.feature_length, dtype=np.float32)
        
        if len(wavelengths) < 2:
            return features
        
        try:
            interp_func = interp1d(
                wavelengths, intensities, 
                kind='linear', 
                bounds_error=False, 
                fill_value=0.0
            )
            
            feature_wavelengths = np.arange(self.min_wavelength, self.max_wavelength + 1)
            features = interp_func(feature_wavelengths)
            features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
        except Exception:
            for wl, intensity in zip(wavelengths, intensities):
                idx = int(round(wl)) - self.min_wavelength
                if 0 <= idx < self.feature_length:
                    features[idx] = intensity
        
        return features.astype(np.float32)
    
    def train(self, X: np.ndarray, y: np.ndarray, model_type: str = 'rf', 
              test_size: float = 0.2, random_state: int = 42,
              X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None,
              X_test: Optional[np.ndarray] = None, y_test: Optional[np.ndarray] = None) -> dict:
        """
        训练模型
        
        支持Random Forest、SVM、Gradient Boosting三种模型
        自动进行数据标准化、标签编码和训练/验证/测试集分割
        
        Args:
            X: 特征矩阵
            y: 标签数组
            model_type: 模型类型，"rf"、"svm"或"gb"
            test_size: 测试集比例（当未提供测试集时）
            random_state: 随机种子
            X_val: 验证集特征（可选）
            y_val: 验证集标签（可选）
            X_test: 测试集特征（可选）
            y_test: 测试集标签（可选）
            
        Returns:
            包含准确率、分类报告等训练结果的字典
        """
        if X is None or y is None:
            raise ValueError("X and y cannot be None")
        
        self.label_encoder = LabelEncoder()
        
        y_train_encoded = None
        y_val_encoded = None
        y_test_encoded = None
        X_train = None
        X_test = None
        
        if X_val is not None and y_val is not None and X_test is not None and y_test is not None:
            y_encoded = self.label_encoder.fit_transform(np.concatenate([y, y_val, y_test]))
            y_train_encoded = self.label_encoder.transform(y)
            y_val_encoded = self.label_encoder.transform(y_val)
            y_test_encoded = self.label_encoder.transform(y_test)
            X_train = X
        else:
            y_encoded = self.label_encoder.fit_transform(y)
            
            if X_val is not None and y_val is not None:
                y_val_encoded = self.label_encoder.transform(y_val)
            
            if X_test is not None and y_test is not None:
                y_test_encoded = self.label_encoder.transform(y_test)
            else:
                X_train, X_test, y_train_encoded, y_test_encoded = train_test_split(
                    X, y_encoded, test_size=test_size, random_state=random_state, stratify=y_encoded
                )
            
            if X_train is None:
                X_train = X
            
            if y_train_encoded is None:
                y_train_encoded = y_encoded
            
            if X_val is None and y_val is None:
                if len(np.unique(y_train_encoded)) >= 2:
                    X_train, X_val, y_train_encoded, y_val_encoded = train_test_split(
                        X_train, y_train_encoded, test_size=0.25, random_state=random_state, stratify=y_train_encoded
                    )
                else:
                    X_val = None
                    y_val_encoded = None
        
        if X_train is None:
            raise ValueError("X_train is None after processing")
        if X_test is None:
            raise ValueError("X_test is None after processing")
        
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        if X_val is not None and y_val is not None:
            X_val_scaled = self.scaler.transform(X_val)
        else:
            X_val_scaled = None
        X_test_scaled = self.scaler.transform(X_test)
        
        if model_type == 'rf':
            self.model = RandomForestClassifier(n_estimators=100, random_state=random_state, n_jobs=-1)
        elif model_type == 'svm':
            self.model = SVC(kernel='rbf', random_state=random_state)
        elif model_type == 'gb':
            self.model = GradientBoostingClassifier(n_estimators=100, random_state=random_state)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        print(f"Training {model_type} model...")
        self.model.fit(X_train_scaled, y_train_encoded)
        
        y_pred_test = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test_encoded, y_pred_test)
        report = classification_report(
            y_test_encoded, y_pred_test, 
            target_names=self.label_encoder.classes_,
            output_dict=True
        )
        
        result = {
            'accuracy': accuracy,
            'report': report,
            'train_size': len(X_train),
            'test_size': len(X_test),
            'val_size': len(X_val) if X_val is not None and y_val is not None else 0,
            'n_classes': len(self.label_encoder.classes_),
            'classes': self.label_encoder.classes_.tolist(),
            'has_validation': X_val is not None and y_val is not None
        }
        
        if X_val is not None and y_val is not None:
            y_pred_val = self.model.predict(X_val_scaled)
            val_accuracy = accuracy_score(y_val_encoded, y_pred_val)
            val_report = classification_report(
                y_val_encoded, y_pred_val,
                target_names=self.label_encoder.classes_,
                output_dict=True
            )
            result['val_accuracy'] = val_accuracy
            result['val_report'] = val_report
        
        self.is_trained = True
        self.feature_names = [f"nm_{i + self.min_wavelength}" for i in range(X.shape[1])]
        
        return result
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        预测类别
        
        Args:
            X: 特征矩阵
            
        Returns:
            预测的类别标签（编码后）
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        预测类别概率
        
        Args:
            X: 特征矩阵
            
        Returns:
            各类别的概率矩阵
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        X_scaled = self.scaler.transform(X)
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X_scaled)
        return None
    
    def get_class_names(self) -> List[str]:
        """
        获取类别名称列表
        
        Returns:
            类别名称列表
        """
        if self.label_encoder is None:
            return []
        return self.label_encoder.classes_.tolist()
    
    def save(self, filepath: str):
        """
        保存模型到文件
        
        保存模型、标准化器、标签编码器等
        
        Args:
            filepath: 保存路径
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load(self, filepath: str):
        """
        从文件加载模型
        
        Args:
            filepath: 模型文件路径
        """
        data = joblib.load(filepath)
        self.model = data['model']
        self.scaler = data['scaler']
        self.label_encoder = data['label_encoder']
        self.feature_names = data.get('feature_names', [])
        self.is_trained = True
        print(f"Model loaded from {filepath}")
