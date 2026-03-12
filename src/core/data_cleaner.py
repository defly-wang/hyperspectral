import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import os


@dataclass
class DataIssue:
    issue_type: str
    file_path: str
    description: str
    severity: str
    indices: Optional[List[int]] = None


class DataCleaner:
    def __init__(self, min_wavelength: float = 400, max_wavelength: float = 2500):
        self.min_wavelength = min_wavelength
        self.max_wavelength = max_wavelength
    
    def check_invalid_data(self, wavelengths: np.ndarray, intensities: np.ndarray, 
                          file_path: str) -> List[DataIssue]:
        issues = []
        
        if len(wavelengths) == 0:
            issues.append(DataIssue(
                issue_type="empty",
                file_path=file_path,
                description="数据为空",
                severity="high"
            ))
            return issues
        
        if len(intensities) == 0:
            issues.append(DataIssue(
                issue_type="empty",
                file_path=file_path,
                description="强度数据为空",
                severity="high"
            ))
            return issues
        
        if len(wavelengths) != len(intensities):
            issues.append(DataIssue(
                issue_type="mismatch",
                file_path=file_path,
                description=f"波长与强度数据长度不匹配: {len(wavelengths)} vs {len(intensities)}",
                severity="high"
            ))
            return issues
        
        if np.any(np.isnan(intensities)):
            nan_count = np.sum(np.isnan(intensities))
            nan_indices = np.where(np.isnan(intensities))[0].tolist()
            issues.append(DataIssue(
                issue_type="nan",
                file_path=file_path,
                description=f"存在 {nan_count} 个NaN值",
                severity="high",
                indices=nan_indices
            ))
        
        if np.any(np.isinf(intensities)):
            inf_count = np.sum(np.isinf(intensities))
            issues.append(DataIssue(
                issue_type="inf",
                file_path=file_path,
                description=f"存在 {inf_count} 个无穷值",
                severity="high"
            ))
        
        if np.any(intensities < 0):
            neg_count = np.sum(intensities < 0)
            issues.append(DataIssue(
                issue_type="negative",
                file_path=file_path,
                description=f"存在 {neg_count} 个负值 (反射率应为正值)",
                severity="medium",
                indices=np.where(intensities < 0)[0].tolist()
            ))
        
        if np.any(intensities > 200):
            over_count = np.sum(intensities > 200)
            issues.append(DataIssue(
                issue_type="overflow",
                file_path=file_path,
                description=f"存在 {over_count} 个超过200的值 (可能为异常高值)",
                severity="medium",
                indices=np.where(intensities > 200)[0].tolist()
            ))
        
        valid_wl = (wavelengths >= self.min_wavelength) & (wavelengths <= self.max_wavelength)
        invalid_count = np.sum(~valid_wl)
        if invalid_count > 0:
            issues.append(DataIssue(
                issue_type="invalid_wavelength",
                file_path=file_path,
                description=f"存在 {invalid_count} 个超出有效范围({self.min_wavelength}-{self.max_wavelength}nm)的波长",
                severity="low"
            ))
        
        if np.std(intensities) < 0.01:
            issues.append(DataIssue(
                issue_type="flat",
                file_path=file_path,
                description="数据方差过小，可能是无效数据",
                severity="medium"
            ))
        
        return issues
    
    def detect_anomalies(self, intensities: np.ndarray, method: str = "iqr", 
                        threshold: float = 3.0) -> Tuple[np.ndarray, List[int]]:
        if method == "iqr":
            q1 = np.percentile(intensities, 25)
            q3 = np.percentile(intensities, 75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            anomalies = (intensities < lower) | (intensities > upper)
        elif method == "zscore":
            mean = np.mean(intensities)
            std = np.std(intensities)
            if std == 0:
                return np.zeros(len(intensities), dtype=bool), []
            z_scores = np.abs((intensities - mean) / std)
            anomalies = z_scores > threshold
        else:
            return np.zeros(len(intensities), dtype=bool), []
        
        anomaly_indices = np.where(anomalies)[0].tolist()
        return anomalies, anomaly_indices
    
    def detect_duplicates(self, spectra: List[Tuple[np.ndarray, np.ndarray]], 
                         file_paths: List[str], 
                         similarity_threshold: float = 0.99) -> List[DataIssue]:
        issues = []
        
        n = len(spectra)
        checked = set()
        
        for i in range(n):
            if file_paths[i] in checked:
                continue
            
            for j in range(i + 1, n):
                if file_paths[j] in checked:
                    continue
                
                wl1, int1 = spectra[i]
                wl2, int2 = spectra[j]
                
                if len(wl1) != len(wl2):
                    continue
                
                if not np.allclose(wl1, wl2):
                    continue
                
                correlation = np.corrcoef(int1, int2)[0, 1]
                
                if correlation >= similarity_threshold:
                    diff = np.abs(int1 - int2)
                    max_diff = np.max(diff)
                    mean_diff = np.mean(diff)
                    
                    issues.append(DataIssue(
                        issue_type="duplicate",
                        file_path=file_paths[j],
                        description=f"与 {os.path.basename(file_paths[i])} 高度相似 (相关系数: {correlation:.4f}, 最大差异: {max_diff:.4f}, 平均差异: {mean_diff:.4f})",
                        severity="high"
                    ))
                    checked.add(file_paths[j])
        
        return issues
    
    def clean_data(self, wavelengths: np.ndarray, intensities: np.ndarray,
                   remove_nan: bool = True, remove_inf: bool = True,
                   interpolate: bool = False) -> Tuple[np.ndarray, np.ndarray]:
        mask = np.ones(len(intensities), dtype=bool)
        
        if remove_nan:
            mask &= ~np.isnan(intensities)
        
        if remove_inf:
            mask &= ~np.isinf(intensities)
        
        valid_wl = (wavelengths >= self.min_wavelength) & (wavelengths <= self.max_wavelength)
        mask &= valid_wl
        
        clean_wl = wavelengths[mask]
        clean_int = intensities[mask]
        
        if interpolate and np.sum(~mask) > 0:
            try:
                clean_int = np.interp(wavelengths, clean_wl, clean_int)
                clean_wl = wavelengths
            except:
                pass
        
        return clean_wl, clean_int
    
    def get_data_statistics(self, wavelengths: np.ndarray, intensities: np.ndarray) -> Dict:
        return {
            "total_points": len(intensities),
            "valid_points": np.sum(~np.isnan(intensities) & ~np.isinf(intensities)),
            "nan_count": np.sum(np.isnan(intensities)),
            "inf_count": np.sum(np.isinf(intensities)),
            "min_intensity": np.min(intensities),
            "max_intensity": np.max(intensities),
            "mean_intensity": np.mean(intensities),
            "std_intensity": np.std(intensities),
            "min_wavelength": np.min(wavelengths),
            "max_wavelength": np.max(wavelengths),
            "wavelength_range": np.max(wavelengths) - np.min(wavelengths)
        }
