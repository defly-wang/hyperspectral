"""
Excel文件读取模块 - 用于解析xlsx/xls格式的光谱数据文件
Excel File Reader Module
支持解析Excel格式的光谱数据文件
使用python-calamine库（Rust编写，性能更好）
"""

import os
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
from python_calamine import load_workbook


@dataclass
class XLSXMetadata:
    """
    Excel文件元数据数据结构
    """
    filename: str = ""                      # 文件名
    sheet_name: str = ""                    # 工作表名称


@dataclass
class SpectrumData:
    """
    光谱数据结构
    与ISF格式兼容的数据结构
    """
    wavelengths: np.ndarray                 # 波长数组 (nm)
    intensities: np.ndarray                 # 强度/反射率数组
    metadata: XLSXMetadata                  # 元数据


def parse_xlsx_file(filepath: str, wavelength_col: int = 0, intensity_col: int = 4) -> SpectrumData:
    """
    解析Excel光谱数据文件
    
    参数:
        filepath: Excel文件路径
        wavelength_col: 波长所在列索引 (默认第0列，即A列)
        intensity_col: 强度所在列索引 (默认第4列，即E列)
        
    返回:
        SpectrumData: 包含波长、强度和元数据的光谱数据对象
    """
    wb = load_workbook(filepath)
    ws = wb.get_sheet()
    sheet_name = ws.name()
    
    wavelengths = []
    intensities = []
    
    for row in ws.iter_rows():
        if row is None:
            continue
        
        try:
            wl_cell = row[wavelength_col]
            int_cell = row[intensity_col]
            
            if wl_cell.value is None or int_cell.value is None:
                continue
            
            wl = float(wl_cell.value)
            intensity = float(int_cell.value)
            
            if not (np.isnan(wl) or np.isnan(intensity)):
                wavelengths.append(wl)
                intensities.append(intensity)
        except (ValueError, TypeError, IndexError):
            continue
    
    metadata = XLSXMetadata(
        filename=os.path.basename(filepath),
        sheet_name=sheet_name
    )
    
    return SpectrumData(
        wavelengths=np.array(wavelengths),
        intensities=np.array(intensities),
        metadata=metadata
    )


def load_xlsx_spectrum(filepath: str, min_wavelength: float = 400) -> Tuple[np.ndarray, np.ndarray]:
    """
    快速加载xlsx文件中的光谱数据（用于多进程）
    
    参数:
        filepath: Excel文件路径
        min_wavelength: 最小波长过滤值
        
    返回:
        (wavelengths, intensities) 元组
    """
    wb = load_workbook(filepath)
    ws = wb.get_sheet()
    
    wavelengths = []
    intensities = []
    
    for row in ws.iter_rows():
        if row is None:
            continue
        
        try:
            wl_cell = row[0]
            int_cell = row[4]
            
            if wl_cell.value is None or int_cell.value is None:
                continue
            
            wl = float(wl_cell.value)
            intensity = float(int_cell.value)
            
            if not (np.isnan(wl) or np.isnan(intensity)):
                wavelengths.append(wl)
                intensities.append(intensity)
        except (ValueError, TypeError, IndexError):
            continue
    
    if len(intensities) < 10:
        return np.array([]), np.array([])
    
    wavelengths = np.array(wavelengths)
    intensities = np.array(intensities)
    
    mask = wavelengths >= min_wavelength
    return wavelengths[mask], intensities[mask]


def load_xlsx_files(folder_path: str) -> List[Tuple[str, SpectrumData]]:
    """
    批量加载文件夹中的Excel文件
    
    参数:
        folder_path: 文件夹路径
        
    返回:
        List[Tuple[str, SpectrumData]]: 文件名和光谱数据的元组列表
    """
    results = []
    if not os.path.isdir(folder_path):
        return results
    
    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith(('.xlsx', '.xls')):
            filepath = os.path.join(folder_path, filename)
            try:
                data = parse_xlsx_file(filepath)
                results.append((filename, data))
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return results
