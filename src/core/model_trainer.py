import os
import numpy as np
from typing import List, Tuple, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
import joblib


def _load_single_file(filepath: str, min_wavelength: float, min_wl: int) -> Tuple[np.ndarray, str]:
    try:
        from .xlsx_reader import parse_xlsx_file
        data = parse_xlsx_file(filepath)
        
        mask = data.wavelengths >= min_wavelength
        wavelengths = data.wavelengths[mask]
        intensities = data.intensities[mask]
        
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
        print(f"Error loading {filepath}: {e}")
        return None, None


class SpectrumClassifier:
    def __init__(self, min_wavelength: int = 400, max_wavelength: int = 2500):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None
        self.is_trained = False
        self.min_wavelength = min_wavelength
        self.max_wavelength = max_wavelength
        self.feature_length = max_wavelength - min_wavelength + 1
    
    def load_data_from_directory(self, data_dir: str, min_wavelength: float = 400,
                                 use_split_dirs: bool = False,
                                 progress_callback: Optional[Callable[[int, str], None]] = None) -> Tuple[np.ndarray, np.ndarray, 
                                                                       Optional[np.ndarray], Optional[np.ndarray],
                                                                       Optional[np.ndarray], Optional[np.ndarray]]:
        """
        从目录加载训练数据
        
        参数:
            data_dir: 数据目录路径
            min_wavelength: 最小波长过滤值
            use_split_dirs: 是否使用已分割的目录结构 (train/val/test)
            progress_callback: 进度回调函数，参数为 (进度百分比, 当前状态描述)
            
        返回:
            (X_train, y_train, X_val, y_val, X_test, y_test) 元组
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
        
        # 计算总文件数用于进度显示
        total_files = 0
        for category in categories:
            category_dir = os.path.join(data_dir, category)
            files = [f for f in os.listdir(category_dir) 
                    if f.lower().endswith(('.xlsx', '.xls'))]
            total_files += len(files)
        
        loaded_files = 0
        
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
                        loaded_files += 1
                        continue
                    
                    features = self._extract_features(wavelengths, intensities)
                    X.append(features)
                    y.append(category)
                    
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                
                loaded_files += 1
                # 每10%进度或完成时更新，避免频繁回调
                if progress_callback and loaded_files == total_files or loaded_files % max(1, total_files // 10) == 0:
                    progress_callback(int(loaded_files / total_files * 50), f"Loading: {loaded_files}/{total_files}")
        
        if not X:
            raise ValueError("No valid data loaded")
        
        return np.array(X), np.array(y), None, None, None, None
    
    def _load_from_split_dirs(self, data_dir: str, min_wavelength: float,
                              progress_callback: Optional[Callable[[int, str], None]] = None) -> Tuple:
        """
        从已分割的目录加载数据 (train/val/test)
        
        参数:
            data_dir: 数据根目录
            min_wavelength: 最小波长
            progress_callback: 进度回调函数
            
        返回:
            (X_train, y_train, X_val, y_val, X_test, y_test) 元组
        """
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
        
        print(f"Starting ThreadPoolExecutor with {min(8, os.cpu_count() or 4)} workers...")
        
        with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as executor:
            futures = {
                executor.submit(_load_single_file, filepath, min_wavelength, min_wl): (filepath, split_type, category)
                for filepath, split_type, category in all_files
            }
            
            print(f"Submitted {len(futures)} tasks to executor")
            
            completed = 0
            total_files = len(all_files)
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
                # 每10%进度或完成时更新，避免频繁回调
                if progress_callback and completed == total_files or completed % max(1, total_files // 10) == 0:
                    progress_callback(int(completed / total_files * 50), f"Loading: {completed}/{total_files}")
        
        X_train = np.array(X_train) if X_train else np.array([])
        y_train = np.array(y_train) if y_train else np.array([])
        X_val = np.array(X_val) if X_val else None
        y_val = np.array(y_val) if y_val else None
        X_test = np.array(X_test) if X_test else None
        y_test = np.array(y_test) if y_test else None
        
        print(f"Loading complete! Train: {len(X_train)}, Val: {len(X_val) if X_val is not None else 0}, Test: {len(X_test) if X_test is not None else 0}")
        
        return X_train, y_train, X_val, y_val, X_test, y_test
    
    def detect_split_dirs(self, data_dir: str) -> bool:
        if not os.path.isdir(data_dir):
            return False
        subdirs = set(os.listdir(data_dir))
        return 'train' in subdirs and len(subdirs) >= 2
    
    def _extract_features(self, wavelengths: np.ndarray, intensities: np.ndarray) -> np.ndarray:
        features = np.zeros(self.feature_length, dtype=np.float32)
        
        for wl, intensity in zip(wavelengths, intensities):
            idx = int(wl) - self.min_wavelength
            if 0 <= idx < self.feature_length:
                features[idx] = intensity
        
        return features
    
    def train(self, X: np.ndarray, y: np.ndarray, model_type: str = 'rf', 
              test_size: float = 0.2, random_state: int = 42,
              X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None,
              X_test: Optional[np.ndarray] = None, y_test: Optional[np.ndarray] = None) -> dict:
        self.label_encoder = LabelEncoder()
        
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
            else:
                y_val_encoded = None
            
            if X_test is not None and y_test is not None:
                y_test_encoded = self.label_encoder.transform(y_test)
            else:
                y_test_encoded = None
                X_train, X_test, y_train_encoded, y_test_encoded = train_test_split(
                    X, y_encoded, test_size=test_size, random_state=random_state, stratify=y_encoded
                )
            
            if X_val is None and y_val is None and X_test is None and y_test is None:
                X_train, X_val, y_train_encoded, y_val_encoded = train_test_split(
                    X_train, y_train_encoded, test_size=0.25, random_state=random_state, stratify=y_train_encoded
                )
        
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
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        X_scaled = self.scaler.transform(X)
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X_scaled)
        return None
    
    def get_class_names(self) -> List[str]:
        if self.label_encoder is None:
            return []
        return self.label_encoder.classes_.tolist()
    
    def save(self, filepath: str):
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
        data = joblib.load(filepath)
        self.model = data['model']
        self.scaler = data['scaler']
        self.label_encoder = data['label_encoder']
        self.feature_names = data.get('feature_names', [])
        self.is_trained = True
        print(f"Model loaded from {filepath}")
