"""
USGS光谱数据库读取模块 - 用于解析USGS光谱库ASCIIdata_splib07a数据
USGS Spectral Library Reader Module
支持解析NASA/USGS光谱库的光谱数据
"""

import os
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from pathlib import Path


@dataclass
class USGSSpectrumMetadata:
    """
    USGS光谱数据元数据结构
    """
    filename: str = ""
    record_id: str = ""
    name: str = ""
    sample_id: str = ""
    category: str = ""
    sub_category: str = ""
    instrument: str = ""
    processing: str = ""


@dataclass
class USGSSpectrumData:
    """
    USGS光谱数据结构
    """
    wavelengths: np.ndarray
    intensities: np.ndarray
    metadata: USGSSpectrumMetadata


class USGSSpectralLibrary:
    """
    USGS光谱库管理类
    
    支持功能:
        - 扫描并索引光谱库文件
        - 按类别过滤光谱
        - 搜索光谱
        - 加载光谱数据
    """
    
    CHAPTERS = {
        "ChapterA_ArtificialMaterials": "人工材料",
        "ChapterC_Coatings": "涂层",
        "ChapterL_Liquids": "液体",
        "ChapterM_Minerals": "矿物",
        "ChapterO_OrganicCompounds": "有机化合物",
        "ChapterS_SoilsAndMixtures": "土壤和混合物",
        "ChapterV_Vegetation": "植被",
    }
    
    def __init__(self, library_path: str):
        """
        初始化光谱库
        
        参数:
            library_path: 光谱库根目录路径
        """
        self.library_path = Path(library_path)
        self.spectrum_index: Dict[str, USGSSpectrumMetadata] = {}
        self._scan_library()
    
    def _scan_library(self):
        """扫描光谱库目录，建立索引"""
        self.spectrum_index.clear()
        
        for chapter in self.CHAPTERS.keys():
            chapter_dir = self.library_path / chapter
            if not chapter_dir.exists():
                continue
            
            for file_path in chapter_dir.glob("*.txt"):
                metadata = self._parse_metadata(file_path)
                if metadata:
                    self.spectrum_index[str(file_path)] = metadata
    
    def _parse_metadata(self, filepath: Path) -> Optional[USGSSpectrumMetadata]:
        """
        解析文件头的元数据
        
        参数:
            filepath: 文件路径
            
        返回:
            USGSSpectrumMetadata或None
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                header = f.readline().strip()
            
            parts = header.split(':')
            if len(parts) < 2:
                return None
            
            record_part = parts[0].strip()
            info_part = parts[1].strip() if len(parts) > 1 else ""
            
            record_id = record_part.replace("splib07a Record", "").strip()
            
            name = info_part.strip()
            category = filepath.parent.name
            
            filename_parts = filepath.stem.replace("splib07a_", "").split("_")
            sub_category = filename_parts[0] if filename_parts else ""
            
            metadata = USGSSpectrumMetadata(
                filename=filepath.name,
                record_id=record_id,
                name=name,
                category=category,
                sub_category=sub_category,
            )
            
            return metadata
        except Exception:
            return None
    
    def load_spectrum(self, filepath: str) -> Optional[USGSSpectrumData]:
        """
        加载单个光谱文件
        
        参数:
            filepath: 光谱文件路径
            
        返回:
            USGSSpectrumData或None
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            return None
        
        metadata = self._parse_metadata(filepath)
        if not metadata:
            metadata = USGSSpectrumMetadata(filename=filepath.name)
        
        try:
            intensities = []
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                try:
                    value = float(line)
                    if np.isnan(value) or np.isinf(value) or abs(value) > 1e30:
                        continue
                    intensities.append(value)
                except ValueError:
                    continue
            
            if len(intensities) < 10:
                return None
            
            wavelengths = self._get_wavelengths(len(intensities))
            
            return USGSSpectrumData(
                wavelengths=wavelengths,
                intensities=np.array(intensities),
                metadata=metadata
            )
        except Exception:
            return None
    
    def _get_wavelengths(self, num_points: int) -> np.ndarray:
        """
        根据数据点数生成标准波长数组
        
        参数:
            num_points: 数据点数量
            
        返回:
            波长数组 (微米)
        """
        wavelengths_file = self.library_path / "splib07a_Wavelengths_ASD_0.35-2.5_microns_2151_ch.txt"
        
        if wavelengths_file.exists():
            try:
                wavelengths = []
                with open(wavelengths_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                wavelengths.append(float(line))
                            except ValueError:
                                continue
                if len(wavelengths) >= num_points:
                    return np.array(wavelengths[:num_points])
            except Exception:
                pass
        
        return np.linspace(0.35, 2.5, num_points)
    
    def get_categories(self) -> List[Tuple[str, str]]:
        """
        获取所有类别
        
        返回:
            List[Tuple[str, str]]: (英文名称, 中文名称)列表
        """
        return list(self.CHAPTERS.items())
    
    def get_spectra_by_category(self, category: str) -> List[Tuple[str, USGSSpectrumMetadata]]:
        """
        按类别获取光谱列表
        
        参数:
            category: 类别名称(英文)
            
        返回:
            List[Tuple[str, USGSSpectrumMetadata]]: (文件路径, 元数据)列表
        """
        results = []
        for filepath, metadata in self.spectrum_index.items():
            if metadata.category == category:
                results.append((filepath, metadata))
        return results
    
    def get_sub_categories(self, category: str) -> List[str]:
        """
        获取某个类别下的子类别
        
        参数:
            category: 类别名称(英文)
            
        返回:
            List[str]: 子类别列表
        """
        sub_cats = set()
        for filepath, metadata in self.spectrum_index.items():
            if metadata.category == category and metadata.sub_category:
                sub_cats.add(metadata.sub_category)
        return sorted(list(sub_cats))
    
    def get_spectra_by_sub_category(self, category: str, sub_category: str) -> List[Tuple[str, USGSSpectrumMetadata]]:
        """
        按子类别获取光谱列表
        
        参数:
            category: 类别名称(英文)
            sub_category: 子类别名称
            
        返回:
            List[Tuple[str, USGSSpectrumMetadata]]: (文件路径, 元数据)列表
        """
        results = []
        for filepath, metadata in self.spectrum_index.items():
            if metadata.category == category and metadata.sub_category == sub_category:
                results.append((filepath, metadata))
        return results
    
    def search(self, query: str) -> List[Tuple[str, USGSSpectrumMetadata]]:
        """
        搜索光谱
        
        参数:
            query: 搜索关键词
            
        返回:
            List[Tuple[str, USGSSpectrumMetadata]]: 匹配的光谱列表
        """
        query = query.lower()
        results = []
        for filepath, metadata in self.spectrum_index.items():
            if query in metadata.name.lower() or query in metadata.filename.lower():
                results.append((filepath, metadata))
        return results
    
    def get_all_spectra(self) -> List[Tuple[str, USGSSpectrumMetadata]]:
        """
        获取所有光谱
        
        返回:
            List[Tuple[str, USGSSpectrumMetadata]]: 所有光谱列表
        """
        return list(self.spectrum_index.items())
    
    def get_total_count(self) -> int:
        """
        获取光谱总数
        
        返回:
            光谱数量
        """
        return len(self.spectrum_index)


def load_usgs_spectrum(filepath: str, library_path: Optional[str] = None) -> Optional[USGSSpectrumData]:
    """
    快速加载USGS光谱文件
    
    参数:
        filepath: 光谱文件路径
        library_path: 光谱库根目录(可选)
        
    返回:
        USGSSpectrumData或None
    """
    if library_path:
        lib = USGSSpectralLibrary(library_path)
        return lib.load_spectrum(filepath)
    
    filepath = Path(filepath)
    if not filepath.exists():
        return None
    
    try:
        intensities = []
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        for line in lines[1:]:
            line = line.strip()
            if line:
                try:
                    intensities.append(float(line))
                except ValueError:
                    continue
        
        num_points = len(intensities)
        if library_path:
            lib_path = Path(library_path)
        else:
            lib_path = filepath.parent.parent.parent
        
        lib = USGSSpectralLibrary(str(lib_path))
        wavelengths = lib._get_wavelengths(num_points)
        
        header = lines[0].strip()
        parts = header.split(':')
        name = parts[1].strip() if len(parts) > 1 else filepath.stem
        record_id = parts[0].strip().replace("splib07a Record", "").strip()
        
        metadata = USGSSpectrumMetadata(
            filename=filepath.name,
            name=name,
            record_id=record_id,
            category=filepath.parent.name,
        )
        
        return USGSSpectrumData(
            wavelengths=wavelengths,
            intensities=np.array(intensities),
            metadata=metadata
        )
    except Exception:
        return None