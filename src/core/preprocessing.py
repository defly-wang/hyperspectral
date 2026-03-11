import numpy as np
from scipy import signal
from scipy.ndimage import uniform_filter1d
from typing import Callable, Tuple


def smooth_savitzky_golay(intensities: np.ndarray, window_length: int = 11, polyorder: int = 3) -> np.ndarray:
    if window_length % 2 == 0:
        window_length += 1
    if window_length > len(intensities):
        window_length = len(intensities) if len(intensities) % 2 == 1 else len(intensities) - 1
    if window_length < polyorder + 2:
        polyorder = window_length - 2
    if polyorder < 0:
        polyorder = 0
    return signal.savgol_filter(intensities, window_length, polyorder)


def smooth_moving_average(intensities: np.ndarray, window_size: int = 5) -> np.ndarray:
    if window_size > len(intensities):
        window_size = len(intensities)
    return uniform_filter1d(intensities, size=window_size)


def baseline_airpls(intensities: np.ndarray, lambda_: int = 10000, p: float = 0.01, niter: int = 10) -> np.ndarray:
    baseline = intensities.copy()
    for _ in range(niter):
        baseline = baseline + (intensities - baseline) * p * lambda_ / (lambda_ + np.abs(intensities - baseline))
    return baseline


def normalize_minmax(intensities: np.ndarray) -> np.ndarray:
    min_val = np.min(intensities)
    max_val = np.max(intensities)
    if max_val - min_val == 0:
        return intensities
    return (intensities - min_val) / (max_val - min_val)


def normalize_zscore(intensities: np.ndarray) -> np.ndarray:
    mean_val = np.mean(intensities)
    std_val = np.std(intensities)
    if std_val == 0:
        return intensities - mean_val
    return (intensities - mean_val) / std_val


def subtract_baseline(intensities: np.ndarray) -> np.ndarray:
    return intensities - baseline_airpls(intensities)


class Preprocessor:
    SMOOTH_SG = "Savitzky-Golay"
    SMOOTH_MA = "Moving Average"
    NORM_MINMAX = "Min-Max"
    NORM_ZSCORE = "Z-Score"
    BASELINE_AIRPLS = "AirPLS"
    BASELINE_SUB = "Subtract Baseline"

    @staticmethod
    def get_methods() -> dict:
        return {
            "smoothing": [Preprocessor.SMOOTH_SG, Preprocessor.SMOOTH_MA],
            "normalization": [Preprocessor.NORM_MINMAX, Preprocessor.NORM_ZSCORE],
            "baseline": [Preprocessor.BASELINE_AIRPLS, Preprocessor.BASELINE_SUB]
        }

    @staticmethod
    def apply(intensities: np.ndarray, method: str, **params) -> np.ndarray:
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
