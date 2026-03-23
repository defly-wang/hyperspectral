"""
数据清洗模块 - 用于检测和处理光谱数据中的问题
Data Cleaning Module
提供数据质量检测、异常检测、重复检测等功能
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import os


@dataclass
class DataIssue:
    """
    数据问题数据结构
    
    用于表示检测到的数据问题，包含问题类型、文件路径、描述和严重程度
    """
    issue_type: str      # 问题类型
    file_path: str       # 文件路径
    description: str     # 问题描述
    severity: str        # 严重程度: high/medium/low
    indices: Optional[List[int]] = None  # 相关数据点索引


class DataCleaner:
    """
    光谱数据清洗器
    
    提供多种数据质量检测功能：
    - 无效数据检测（空值、无穷值、负值等）
    - 异常点检测（IQR、Z-Score方法）
    - 重复文件检测（基于相关系数）
    - 离群光谱检测（与整体趋势比较）
    - 趋势异常检测
    """
    
    def __init__(self, min_wavelength: float = 350, max_wavelength: float = 2500):
        """
        初始化数据清洗器
        
        Args:
            min_wavelength: 最小有效波长（默认350nm）
            max_wavelength: 最大有效波长（默认2500nm）
        """
        self.min_wavelength = min_wavelength
        self.max_wavelength = max_wavelength
    
    def check_invalid_data(self, wavelengths: np.ndarray, intensities: np.ndarray, 
                          file_path: str) -> List[DataIssue]:
        """
        检测无效数据
        
        检查以下问题：
        - 空数据
        - 波长与强度长度不匹配
        - NaN值
        - 无穷值
        - 负值（反射率应为正）
        - 超过100的值（异常高值）
        - 超出有效波长范围的数据
        - 数据方差过小
        
        Args:
            wavelengths: 波长数组
            intensities: 强度数组
            file_path: 文件路径
            
        Returns:
            DataIssue列表
        """
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
        
        if np.any(intensities > 100):
            over_count = np.sum(intensities > 100)
            issues.append(DataIssue(
                issue_type="overflow",
                file_path=file_path,
                description=f"存在 {over_count} 个超过100的值 (可能为异常高值)",
                severity="medium",
                indices=np.where(intensities > 100)[0].tolist()
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
        """
        检测异常数据点
        
        使用IQR或Z-Score方法检测光谱中的异常点
        
        Args:
            intensities: 强度数组
            method: 检测方法，"iqr"或"zscore"
            threshold: 阈值，IQR方法中为倍数，Z-Score中为标准差倍数
            
        Returns:
            (异常点布尔数组, 异常点索引列表)
        """
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
        """
        检测重复文件
        
        基于光谱相关系数检测高度相似的文件
        
        Args:
            spectra: 光谱列表，每项为(波长, 强度)元组
            file_paths: 文件路径列表
            similarity_threshold: 相似度阈值，默认0.99
            
        Returns:
            DataIssue列表
        """
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
        """
        清洗数据
        
        移除无效数据点，可选择插值填补
        
        Args:
            wavelengths: 波长数组
            intensities: 强度数组
            remove_nan: 是否移除NaN值
            remove_inf: 是否移除无穷值
            interpolate: 是否插值填补缺失值
            
        Returns:
            (清洗后的波长, 清洗后的强度)
        """
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
        """
        获取数据统计信息
        
        Args:
            wavelengths: 波长数组
            intensities: 强度数组
            
        Returns:
            包含各项统计指标的字典
        """
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

    def detect_outlier_spectra(self, spectra: List[Tuple[np.ndarray, np.ndarray]],
                              file_paths: List[str],
                              similarity_threshold: float = 0.85) -> List[DataIssue]:
        """
        检测离群光谱
        
        检测与整体平均光谱趋势显著不同的光谱，可能表示错误分类或异常样本
        
        Args:
            spectra: 光谱列表
            file_paths: 文件路径列表
            similarity_threshold: 相似度阈值，默认0.85
            
        Returns:
            DataIssue列表
        """
        issues = []
        
        if len(spectra) < 3:
            return issues
        
        normalized_spectra = []
        valid_indices = []
        
        for i, (wl, intensity) in enumerate(spectra):
            if len(wl) < 10 or len(wl) != len(intensity):
                continue
            
            norm = (intensity - np.min(intensity)) / (np.max(intensity) - np.min(intensity) + 1e-10)
            normalized_spectra.append(norm)
            valid_indices.append(i)
        
        if len(normalized_spectra) < 3:
            return issues
        
        reference = np.mean(normalized_spectra, axis=0)
        
        correlations = []
        for i, norm in enumerate(normalized_spectra):
            if len(norm) != len(reference):
                continue
            corr = np.corrcoef(norm, reference)[0, 1]
            if np.isnan(corr):
                corr = 0
            correlations.append((valid_indices[i], corr))
        
        correlations.sort(key=lambda x: x[1])
        
        for idx, corr in correlations:
            if corr < similarity_threshold:
                issues.append(DataIssue(
                    issue_type="outlier_spectrum",
                    file_path=file_paths[idx],
                    description=f"光谱趋势异常，与整体平均谱相关系数仅 {corr:.4f}",
                    severity="medium"
                ))
        
        return issues

    def calculate_spectrum_similarity(self, intensities: np.ndarray, 
                                     reference: np.ndarray) -> Dict:
        """
        计算光谱相似度
        
        计算待测光谱与参考光谱的多种相似度指标
        
        Args:
            intensities: 待测光谱强度数组
            reference: 参考光谱强度数组
            
        Returns:
            包含相关系数、欧氏距离、余弦相似度的字典
        """
        if len(intensities) != len(reference):
            return {"correlation": 0, "euclidean_dist": float('inf'), "cosine_sim": 0}
        
        correlation = np.corrcoef(intensities, reference)[0, 1]
        if np.isnan(correlation):
            correlation = 0
        
        euclidean_dist = np.sqrt(np.sum((intensities - reference) ** 2))
        
        cosine_sim = np.dot(intensities, reference) / (
            np.linalg.norm(intensities) * np.linalg.norm(reference) + 1e-10
        )
        
        return {
            "correlation": correlation,
            "euclidean_dist": euclidean_dist,
            "cosine_sim": cosine_sim
        }

    def detect_trend_anomalies(self, wavelengths: np.ndarray, intensities: np.ndarray,
                               reference_wl: np.ndarray, reference_int: np.ndarray,
                               threshold: float = 0.7) -> Tuple[bool, Dict]:
        """
        检测趋势异常
        
        比较光谱与参考光谱的趋势相似度
        
        Args:
            wavelengths: 波长数组
            intensities: 强度数组
            reference_wl: 参考波长数组
            reference_int: 参考强度数组
            threshold: 相似度阈值
            
        Returns:
            (是否异常, 详细信息字典)
        """
        if len(wavelengths) < 5 or len(reference_wl) < 5:
            return False, {}
        
        common_wl_min = max(wavelengths[0], reference_wl[0])
        common_wl_max = min(wavelengths[-1], reference_wl[-1])
        
        mask1 = (wavelengths >= common_wl_min) & (wavelengths <= common_wl_max)
        mask2 = (reference_wl >= common_wl_min) & (reference_wl <= common_wl_max)
        
        wl_interp = wavelengths[mask1]
        int_interp = intensities[mask1]
        ref_interp = np.interp(wl_interp, reference_wl, reference_int)
        
        if len(wl_interp) < 5:
            return False, {}
        
        int_norm = (int_interp - np.min(int_interp)) / (np.max(int_interp) - np.min(int_interp) + 1e-10)
        ref_norm = (ref_interp - np.min(ref_interp)) / (np.max(ref_interp) - np.min(ref_interp) + 1e-10)
        
        correlation = np.corrcoef(int_norm, ref_norm)[0, 1]
        if np.isnan(correlation):
            correlation = 0
        
        diff = np.abs(int_norm - ref_norm)
        mean_diff = np.mean(diff)
        max_diff = np.max(diff)
        
        trend_similar = correlation >= threshold
        
        return trend_similar, {
            "correlation": correlation,
            "mean_difference": mean_diff,
            "max_difference": max_diff,
            "is_outlier": not trend_similar
        }

    def analyze_spectrum_trend(self, intensities: np.ndarray) -> Dict:
        """
        分析光谱趋势
        
        使用线性回归分析光谱的整体趋势方向和强度
        
        Args:
            intensities: 强度数组
            
        Returns:
            包含斜率、趋势方向、趋势强度、变化量、波动性的字典
        """
        if len(intensities) < 3:
            return {}
        
        x = np.arange(len(intensities))
        
        coeffs = np.polyfit(x, intensities, 1)
        slope = coeffs[0]
        
        trend_direction = "increasing" if slope > 0.001 else "decreasing" if slope < -0.001 else "stable"
        
        residuals = intensities - np.polyval(coeffs, x)
        r_squared = 1 - (np.var(residuals) / np.var(intensities))
        
        first_half = intensities[:len(intensities)//2]
        second_half = intensities[len(intensities)//2:]
        first_mean = np.mean(first_half)
        second_mean = np.mean(second_half)
        trend_change = second_mean - first_mean
        
        return {
            "slope": slope,
            "trend_direction": trend_direction,
            "trend_strength": abs(r_squared),
            "trend_change": trend_change,
            "volatility": np.std(intensities) / (np.mean(intensities) + 1e-10)
        }

    def detect_anomalous_trend(self, spectra: List[Tuple[np.ndarray, np.ndarray]],
                               file_paths: List[str],
                               trend_threshold: float = 0.5) -> List[DataIssue]:
        """
        检测趋势异常光谱
        
        检测光谱趋势与整体平均值差异较大的样本
        
        Args:
            spectra: 光谱列表
            file_paths: 文件路径列表
            trend_threshold: 趋势差异阈值
            
        Returns:
            DataIssue列表
        """
        issues = []
        
        if len(spectra) < 3:
            return issues
        
        trends = []
        for wl, intensity in spectra:
            if len(wl) >= 3:
                trend = self.analyze_spectrum_trend(intensity)
                if trend:
                    trends.append(trend)
        
        if len(trends) < 3:
            return issues
        
        avg_slope = np.mean([t["slope"] for t in trends])
        avg_volatility = np.mean([t["volatility"] for t in trends])
        
        for i, (wl, intensity) in enumerate(spectra):
            trend = self.analyze_spectrum_trend(intensity)
            if not trend:
                continue
            
            slope_diff = abs(trend["slope"] - avg_slope) / (abs(avg_slope) + 1e-10)
            volatility_ratio = trend["volatility"] / (avg_volatility + 1e-10)
            
            if slope_diff > 2.0 or volatility_ratio > 2.0:
                issues.append(DataIssue(
                    issue_type="anomalous_trend",
                    file_path=file_paths[i],
                    description=f"趋势异常: 斜率差异 {slope_diff:.2f}倍, 波动性 {volatility_ratio:.2f}倍",
                    severity="medium"
                ))
        
        return issues
