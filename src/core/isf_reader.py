"""
ISF文件读取模块 - 用于解析iSpecField光谱仪数据文件
ISF (iSpecField) File Reader Module
支持解析ISF格式的光谱数据文件和元数据
"""

import re
import numpy as np
from dataclasses import dataclass
from typing import Optional, List, Tuple
import os


@dataclass
class ISFMetadata:
    """
    ISF文件元数据数据结构
    包含测量时间、设备参数、环境参数等信息
    """
    date: str = ""                          # 测量日期 (YYYY-MM-DD)
    time: str = ""                          # 测量时间 (HH:MM:SS)
    nrof_specs: int = 2                     # 光谱数量
    meas_number: int = 1                    # 测量编号
    meas_start_time: float = 10.0           # 测量开始时间 (分钟)
    meas_interval: float = 1.0              # 测量间隔 (秒)
    wavelength_start: float = 0.0           # 起始波长 (nm)
    wavelength_end: float = 0.0             # 结束波长 (nm)
    int_time: float = 0.0                   # 积分时间 (毫秒)
    latitude: float = 0.0                    # 纬度
    longitude: float = 0.0                   # 经度
    azimuth_angle: float = 0.0              # 方位角
    elevation_angle: float = 0.0            # 仰角
    temperature: float = 0.0                # 温度 (摄氏度)
    humidity: float = 0.0                   # 湿度 (百分比)
    data_number: int = 0                    # 数据点数量


@dataclass
class SpectrumData:
    """
    光谱数据结构
    包含波长数组、强度数组和元数据
    """
    wavelengths: np.ndarray                 # 波长数组 (nm)
    intensities: np.ndarray                 # 强度/反射率数组
    metadata: ISFMetadata                   # 元数据


def parse_isf_file(filepath: str) -> SpectrumData:
    """
    解析ISF光谱数据文件
    
    参数:
        filepath: ISF文件路径
        
    返回:
        SpectrumData: 包含波长、强度和元数据的光谱数据对象
    """
    # 打开文件并读取内容，忽略编码错误
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # 初始化元数据对象
    metadata = ISFMetadata()

    # ========== 解析日期和时间 ==========
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', content)
    time_match = re.search(r'(\d{2}:\d{2}:\d{2})', content)
    if date_match:
        metadata.date = date_match.group(1)
    if time_match:
        metadata.time = time_match.group(1)

    # ========== 解析测量参数 ==========
    nrof_specs_match = re.search(r'NrofSpecs=(\d+)', content)
    if nrof_specs_match:
        metadata.nrof_specs = int(nrof_specs_match.group(1))

    meas_number_match = re.search(r'MeasNumber=(\d+)', content)
    if meas_number_match:
        metadata.meas_number = int(meas_number_match.group(1))

    meas_start_time_match = re.search(r'StartTime\[min\]=(\d+\.?\d*)', content)
    if meas_start_time_match:
        metadata.meas_start_time = float(meas_start_time_match.group(1))

    meas_interval_match = re.search(r'Interval\[s\]=(\d+\.?\d*)', content)
    if meas_interval_match:
        metadata.meas_interval = float(meas_interval_match.group(1))

    int_time_match = re.search(r'IntTime\[ms\]=(\d+\.?\d*)', content)
    if int_time_match:
        metadata.int_time = float(int_time_match.group(1))

    # ========== 解析地理坐标 ==========
    lat_match = re.search(r'Latitude=([-\d.]+)', content)
    if lat_match:
        metadata.latitude = float(lat_match.group(1))

    lon_match = re.search(r'Longitude=([-\d.]+)', content)
    if lon_match:
        metadata.longitude = float(lon_match.group(1))

    # ========== 解析角度参数 ==========
    azimuth_match = re.search(r'AzimuthAngle\[.*?\]=([-\d.]+)', content)
    if azimuth_match:
        metadata.azimuth_angle = float(azimuth_match.group(1))

    elevation_match = re.search(r'ElevationAngle\[.*?\]=([-\d.]+)', content)
    if elevation_match:
        metadata.elevation_angle = float(elevation_match.group(1))

    # ========== 解析环境参数 ==========
    temp_match = re.search(r'Temperature1\[.*?\]=([-\d.]+)', content)
    if temp_match:
        metadata.temperature = float(temp_match.group(1))

    humidity_match = re.search(r'Humidity1\[%\]=([-\d.]+)', content)
    if humidity_match:
        metadata.humidity = float(humidity_match.group(1))

    data_number_match = re.search(r'dataNumber=(\d+)', content)
    if data_number_match:
        metadata.data_number = int(data_number_match.group(1))

    # ========== 解析光谱数据 ==========
    lines = content.split('\n')
    in_spectrum_section = False              # 标记是否进入光谱数据区
    wavelengths = []                         # 波长列表
    intensities = []                         # 强度列表

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 检测光谱数据区域开始
        if line.startswith('[Spectrum]'):
            in_spectrum_section = True
            continue
        
        if in_spectrum_section:
            # 跳过注释行和节头
            if line.startswith('*') or line.startswith('=') or line.startswith('['):
                if not line.startswith('[Spectrum]'):
                    continue
            
            # ISF格式: 波长; 某值; 某值; 某值; 强度; ...
            parts = line.split(';')
            if len(parts) >= 5:
                try:
                    wl = float(parts[0])           # 第1列: 波长
                    sample = float(parts[4])       # 第5列: 强度/反射率
                    wavelengths.append(wl)
                    intensities.append(sample)
                except (ValueError, IndexError):
                    continue

    # 转换为numpy数组
    wavelengths = np.array(wavelengths)
    intensities = np.array(intensities)

    # 设置波长范围
    if len(wavelengths) > 0:
        metadata.wavelength_start = wavelengths[0]
        metadata.wavelength_end = wavelengths[-1]

    return SpectrumData(wavelengths, intensities, metadata)


def load_isf_files(folder_path: str) -> List[Tuple[str, SpectrumData]]:
    """
    批量加载文件夹中的ISF文件
    
    参数:
        folder_path: 文件夹路径
        
    返回:
        List[Tuple[str, SpectrumData]]: 文件名和光谱数据的元组列表
    """
    results = []
    if not os.path.isdir(folder_path):
        return results
    
    # 遍历文件夹中的所有文件
    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith('.isf'):
            filepath = os.path.join(folder_path, filename)
            try:
                data = parse_isf_file(filepath)
                results.append((filename, data))
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return results
