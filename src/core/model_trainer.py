import os
import numpy as np
from typing import List, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
import joblib


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
    
    def load_data_from_directory(self, data_dir: str, min_wavelength: float = 500) -> Tuple[np.ndarray, np.ndarray]:
        X = []
        y = []
        
        if not os.path.isdir(data_dir):
            raise ValueError(f"Directory not found: {data_dir}")
        
        categories = sorted([d for d in os.listdir(data_dir) 
                           if os.path.isdir(os.path.join(data_dir, d))])
        
        if not categories:
            raise ValueError(f"No category directories found in {data_dir}")
        
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
        
        return np.array(X), np.array(y)
    
    def _extract_features(self, wavelengths: np.ndarray, intensities: np.ndarray) -> np.ndarray:
        features = np.zeros(self.feature_length, dtype=np.float32)
        
        for wl, intensity in zip(wavelengths, intensities):
            idx = int(wl) - self.min_wavelength
            if 0 <= idx < self.feature_length:
                features[idx] = intensity
        
        return features
    
    def train(self, X: np.ndarray, y: np.ndarray, model_type: str = 'rf', 
              test_size: float = 0.2, random_state: int = 42) -> dict:
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=random_state, stratify=y_encoded
        )
        
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
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
        self.model.fit(X_train_scaled, y_train)
        
        y_pred = self.model.predict(X_test_scaled)
        
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(
            y_test, y_pred, 
            target_names=self.label_encoder.classes_,
            output_dict=True
        )
        
        self.is_trained = True
        self.feature_names = [f"nm_{i + self.min_wavelength}" for i in range(X.shape[1])]
        
        return {
            'accuracy': accuracy,
            'report': report,
            'train_size': len(X_train),
            'test_size': len(X_test),
            'n_classes': len(self.label_encoder.classes_),
            'classes': self.label_encoder.classes_.tolist()
        }
    
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
