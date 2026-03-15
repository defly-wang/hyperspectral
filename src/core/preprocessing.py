"""
光谱数据预处理模块 - 提供各种光谱数据预处理方法
Spectrum Data Preprocessing Module
包含平滑、归一化、基线校正等功能
"""

import numpy as np
from scipy import signal
from scipy.ndimage import uniform_filter1d
from typing import Callable, Tuple


def smooth_savitzky_golay(intensities: np.ndarray, window_length: int = 11, polyorder: int = 3) -> np.ndarray:
    """
    Savitzky-Golay平滑滤波
    保持峰形特征的同时平滑噪声
    
    参数:
        intensities: 原始强度数组
        window_length: 窗口大小 (必须是奇数)
        polyorder: 多项式阶数
        
    返回:
        平滑后的强度数组
    """
    # 窗口大小必须是奇数
    if window_length % 2 == 0:
        window_length += 1
    # 窗口大小不能超过数据长度
    if window_length > len(intensities):
        window_length = len(intensities) if len(intensities) % 2 == 1 else len(intensities) - 1
    # 多项式阶数必须小于窗口大小
    if window_length < polyorder + 2:
        polyorder = window_length - 2
    if polyorder < 0:
        polyorder = 0
    return signal.savgol_filter(intensities, window_length, polyorder)


def smooth_moving_average(intensities: np.ndarray, window_size: int = 5) -> np.ndarray:
    """
    移动平均平滑
    简单的滑动窗口平滑方法
    
    参数:
        intensities: 原始强度数组
        window_size: 窗口大小
        
    返回:
        平滑后的强度数组
    """
    if window_size > len(intensities):
        window_size = len(intensities)
    return uniform_filter1d(intensities, size=window_size)


def baseline_airpls(intensities: np.ndarray, lambda_: int = 10000, p: float = 0.01, niter: int = 10) -> np.ndarray:
    """
    AirPLS基线校正算法 (Adaptive Iterative Reweighted Penalized Least Squares)
    自动估计并去除背景基线
    
    参数:
        intensities: 原始强度数组
        lambda_: 平滑参数 (值越大基线越平滑)
        p: 权重参数
        niter: 迭代次数
        
    返回:
        估计的基线数组
    """
    baseline = intensities.copy()
    for _ in range(niter):
        baseline = baseline + (intensities - baseline) * p * lambda_ / (lambda_ + np.abs(intensities - baseline))
    return baseline


def normalize_minmax(intensities: np.ndarray) -> np.ndarray:
    """
    Min-Max归一化
    将数据缩放到[0, 1]范围
    
    参数:
        intensities: 原始强度数组
        
    返回:
        归一化后的强度数组
    """
    min_val = np.min(intensities)
    max_val = np.max(intensities)
    if max_val - min_val == 0:
        return intensities
    return (intensities - min_val) / (max_val - min_val)


def normalize_zscore(intensities: np.ndarray) -> np.ndarray:
    """
    Z-Score标准化
    将数据转换为均值为0、标准差为1的分布
    
    参数:
        intensities: 原始强度数组
        
    返回:
        标准化后的强度数组
    """
    mean_val = np.mean(intensities)
    std_val = np.std(intensities)
    if std_val == 0:
        return intensities - mean_val
    return (intensities - mean_val) / std_val


def subtract_baseline(intensities: np.ndarray) -> np.ndarray:
    """
    基线扣除
    从原始数据中减去估计的基线
    
    参数:
        intensities: 原始强度数组
        
    返回:
        基线校正后的强度数组
    """
    return intensities - baseline_airpls(intensities)


class Preprocessor:
    """
    光谱数据预处理器
    整合各种预处理方法，提供统一的接口
    """
    # 预处理方法常量
    SMOOTH_SG = "Savitzky-Golay"           # Savitzky-Golay平滑
    SMOOTH_MA = "Moving Average"           # 移动平均平滑
    NORM_MINMAX = "Min-Max"                 # Min-Max归一化
    NORM_ZSCORE = "Z-Score"                 # Z-Score标准化
    BASELINE_AIRPLS = "AirPLS"             # AirPLS基线校正
    BASELINE_SUB = "Subtract Baseline"     # 基线扣除

    @staticmethod
    def get_methods() -> dict:
        """
        获取所有可用的预处理方法
        
        返回:
            包含各类预处理方法的字典
        """
        return {
            "smoothing": [Preprocessor.SMOOTH_SG, Preprocessor.SMOOTH_MA],
            "normalization": [Preprocessor.NORM_MINMAX, Preprocessor.NORM_ZSCORE],
            "baseline": [Preprocessor.BASELINE_AIRPLS, Preprocessor.BASELINE_SUB]
        }

    @staticmethod
    def apply(intensities: np.ndarray, method: str, **params) -> np.ndarray:
        """
        应用预处理方法
        
        参数:
            intensities: 原始强度数组
            method: 预处理方法名称
            **params: 方法对应的参数
            
        返回:
            处理后的强度数组
        """
        if method == Preprocessor.SMOOTH_SG:
            window = params.get('window', 11)
            order = params.get('order', 3)
            return smooth_savitzky_golay(intensities, window, order)
        elif method == Preprocessor.SMOOTH_MA:
            window = params.get('window', 5)
            return smooth_moving_average(intensities, window)
        elif method == Preprocessor.NORM_MINMAX:
            return normalize_minmax(intensities)
        elif method == Preprocessor.NORM_ZSCORE:
            return normalize_zscore(intensities)
        elif method == Preprocessor.BASELINE_AIRPLS:
            return subtract_baseline(intensities)
        elif method == Preprocessor.BASELINE_SUB:
            return subtract_baseline(intensities)
        return intensities
