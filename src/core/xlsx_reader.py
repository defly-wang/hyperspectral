"""
Excel文件读取模块 - 用于解析xlsx/xls格式的光谱数据文件
Excel File Reader Module
支持解析Excel格式的光谱数据文件
"""

import os
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
import openpyxl


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
    # 使用openpyxl加载工作簿，data_only=True表示读取单元格的值而非公式
    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb.active                          # 获取活动工作表
    
    wavelengths = []                         # 波长列表
    intensities = []                         # 强度列表
    
    # 遍历所有行
    for row in ws.iter_rows(min_row=1, values_only=True):
        if row is None:
            continue
        
        try:
            # 提取波长和强度值
            wl = float(row[wavelength_col])
            intensity = float(row[intensity_col])
            # 过滤无效值（None和NaN）
            if wl is not None and intensity is not None and not (np.isnan(wl) or np.isnan(intensity)):
                wavelengths.append(wl)
                intensities.append(intensity)
        except (ValueError, TypeError, IndexError):
            continue
    
    # 关闭工作簿
    wb.close()
    
    # 创建元数据
    metadata = XLSXMetadata(
        filename=os.path.basename(filepath),
        sheet_name=ws.title
    )
    
    return SpectrumData(
        wavelengths=np.array(wavelengths),
        intensities=np.array(intensities),
        metadata=metadata
    )


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
    
    # 遍历文件夹中的所有Excel文件
    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith(('.xlsx', '.xls')):
            filepath = os.path.join(folder_path, filename)
            try:
                data = parse_xlsx_file(filepath)
                results.append((filename, data))
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return results
