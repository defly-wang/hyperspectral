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
    
    SUB_CATEGORIES = {
        "Acmite": "霓石",
        "Actinolite": "阳起石",
        "Adularia": "冰长石",
        "Albite": "钠长石",
        "Allanite": "榍石",
        "Almandine": "铁铝榴石",
        "Alunite": "明矾石",
        "Amphibole": "角闪石",
        "Analcime": "方沸石",
        "Andalusite": "红柱石",
        "Andradite": "钙铁榴石",
        "Anhydrite": "硬石膏",
        "Annite": "高铁云母",
        "Anorthite": "钙长石",
        "Anthophyllite": "直闪石",
        "Antigorite": "叶蛇纹石",
        "Aragonite": "文石",
        "Arsenopyrite": "毒砂",
        "Augite": "普通辉石",
        "Axinite": "斧石",
        "Azurite": "蓝铜矿",
        "Barite": "重晶石",
        "Bassanite": "半水石膏",
        "Bastnaesite": "氟碳铈矿",
        "Beidellite": "贝得石",
        "Biotite": "黑云母",
        "Bronzite": "古铜辉石",
        "Brookite": "板钛矿",
        "Brucite": "氢氧镁石",
        "Calcite": "方解石",
        "Carnallite": "光卤石",
        "Cassiterite": "锡石",
        "Celestite": "天青石",
        "Cerulean": "天蓝石",
        "Chalcedony": "玉髓",
        "Chalcopyrite": "黄铜矿",
        "Chlorite": "绿泥石",
        "Chromite": "铬铁矿",
        "Chrysocolla": "硅孔雀石",
        "Chrysotile": "纤蛇纹石",
        "Cinnabar": "朱砂",
        "Clinoptilolite": "斜发沸石",
        "Clinozoisite": "斜黝帘石",
        "Clintonite": "脆云母",
        "Colemanite": "硼砂",
        "Cookeite": "锂绿泥石",
        "Copiapite": "叶绿矾",
        "Coquimbite": "菱铁矿",
        "Cordierite": "堇青石",
        "Corrensite": "柯绿泥石",
        "Corundum": "刚玉",
        "Cuprite": "赤铜矿",
        "Cummingtonite": "镁铁闪石",
        "Datolite": "硅硼钙石",
        "Diaspore": "硬水铝石",
        "Dickite": "迪凯石",
        "Diopside": "透辉石",
        "Dolomite": "白云石",
        "Dumortierite": "蓝线石",
        "Elbaite": "电气石",
        "Ellagic": "鞣花酸",
        "Endellite": "埃洛石",
        "Enstatite": "顽火辉石",
        "Epidote": "绿帘石",
        "Epsomite": "泻盐",
        "Erionite": "毛沸石",
        "Fassaite": "深绿辉石",
        "Ferrihydrite": "水铁矿",
        "Forsterite": "镁橄榄石",
        "Galena": "方铅矿",
        "Gibbsite": "三水铝石",
        "Glauconite": "海绿石",
        "Glaucophane": "蓝闪石",
        "Goethite": "针铁矿",
        "Grossular": "钙铝榴石",
        "Gypsum": "石膏",
        "Halite": "石盐",
        "Halloysite": "埃洛石",
        "Hectorite": "锂皂石",
        "Hedenbergite": "钙铁辉石",
        "Hematite": "赤铁矿",
        "Heulandite": "片沸石",
        "Hornblende": "角闪石",
        "Howlite": "硅硼钙石",
        "Hydrogrossular": "水钙铝榴石",
        "Hypersthene": "紫苏辉石",
        "Illite": "伊利石",
        "Ilmenite": "钛铁矿",
        "Jadeite": "硬玉",
        "Jarosite": "黄钾铁矾",
        "Kaolinite": "高岭石",
        "Kieserite": "硫镁矾",
        "Labradorite": "拉长石",
        "Laumontite": "浊沸石",
        "Lazurite": "青金石",
        "Lepidocrocite": "纤铁矿",
        "Lepidolite": "锂云母",
        "Limonite": "褐铁矿",
        "Lizardite": "利蛇纹石",
        "Maghemite": "磁赤铁矿",
        "Magnetite": "磁铁矿",
        "Malachite": "孔雀石",
        "Margarite": "珍珠云母",
        "Marialite": "钠柱石",
        "Meionite": "钙柱石",
        "Microcline": "微斜长石",
        "Mirabilite": "芒硝",
        "Mizzonite": "密乌尼石",
        "Monazite": "独居石",
        "Monticellite": "钙镁橄榄石",
        "Montmorillonite": "蒙脱石",
        "Mordenite": "丝光沸石",
        "Muscovite": "白云母",
        "Nacrite": "珍珠石",
        "Natrolite": "钠沸石",
        "Nepheline": "霞石",
        "Nephrite": "软玉",
        "Nontronite": "绿脱石",
        "Olivine": "橄榄石",
        "Opal": "蛋白石",
        "Orthoclase": "正长石",
        "Palygorskite": "坡缕石",
        "Paragonite": "钠云母",
        "Parisite": "氟碳钙铈矿",
        "Pectolite": "针钠钙石",
        "Perthite": "条纹长石",
        "Phlogopite": "金云母",
        "Pigeonite": "易变辉石",
        "Pinnoite": "柱硼镁石",
        "Prehnite": "葡萄石",
        "Prochlorite": "蠕绿泥石",
        "Psilomelane": "硬锰矿",
        "Pyrite": "黄铁矿",
        "Pyrolusite": "软锰矿",
        "Pyromorphite": "磷氯铅矿",
        "Pyrophyllite": "叶蜡石",
        "Pyroxene": "辉石",
        "Quartz": "石英",
        "Rhodochrosite": "菱锰矿",
        "Rhodonite": "蔷薇辉石",
        "Richterite": "透闪石",
        "Riebeckite": "钠闪石",
        "Roscoelite": "钒云母",
        "Rutile": "金红石",
        "Sanidine": "透长石",
        "Saponite": "皂石",
        "Sauconite": "锌皂石",
        "Scolecite": "钙沸石",
        "Sepiolite": "海泡石",
        "Serpentine": "蛇纹石",
        "Siderite": "菱铁矿",
        "Smargite": "绿色角闪石",
        "Sodalite": "方钠石",
        "Sparite": "亮晶方解石",
        "Sphalerite": "闪锌矿",
        "Sphene": "榍石",
        "Spodumene": "锂辉石",
        "Staurolite": "十字石",
        "Stilbite": "辉沸石",
        "Strontianite": "菱锶矿",
        "Sulfur": "硫磺",
        "Syngenite": "合成石",
        "Talc": "滑石",
        "Thenardite": "无水芒硝",
        "Topaz": "黄玉",
        "Tourmaline": "电气石",
        "Tremolite": "透闪石",
        "Trona": "天然碱",
        "Ulexite": "钠硼解石",
        "Ultramarine": "青金石",
        "Uvarovite": "钙铬榴石",
        "Vermiculite": "蛭石",
        "Vesuvianite": "符山石",
        "Witherite": "毒重石",
        "Wollastonite": "硅灰石",
        "Zircon": "锆石",
        "Zoisite": "黝帘石",
        "Zunyite": "羟硅铝石",
        "Grass": "草地",
        "LeafySpurge": "叶大戟",
        "Sagebrush": "蒿属",
        "Saltbrush": "盐碱草",
        "Juniper": "刺柏",
        "Oak": "橡树",
        "Cactus": "仙人掌",
        "Cedar": "雪松",
        "Aspen": "白杨",
        "Maple": "枫树",
        "Pine": "松树",
        "Fir": "冷杉",
        "Willow": "柳树",
        "Walnut": "胡桃",
        "Concrete": "混凝土",
        "Brick": "砖块",
        "Asphalt": "沥青",
        "Tar": "焦油",
        "Oil": "油",
        "Plastic": "塑料",
        "Paper": "纸",
        "Cotton": "棉花",
        "Wood": "木材",
        "Bone": "骨骼",
        "Water": "水",
        "Ice": "冰",
        "Sand": "砂子",
        "Limestone": "石灰石",
        "Basalt": "玄武岩",
    }
    
    @staticmethod
    def get_sub_category_display_name(sub_category: str) -> str:
        """获取子类别显示名称(中英文)"""
        cn_name = USGSSpectralLibrary.SUB_CATEGORIES.get(sub_category)
        if cn_name:
            return f"{cn_name} ({sub_category})"
        return sub_category
    
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
            
            instrument = self._extract_instrument(filepath.name)
            wavelengths = self._get_wavelengths(len(intensities), instrument)
            
            return USGSSpectrumData(
                wavelengths=wavelengths,
                intensities=np.array(intensities),
                metadata=metadata
            )
        except Exception:
            return None
    
    def _extract_instrument(self, filename: str) -> str:
        """从文件名中提取仪器类型"""
        if "BECK" in filename:
            return "BECK"
        elif "ASD" in filename or "ASDFR" in filename or "ASDHR" in filename:
            return "ASD"
        elif "NIC4" in filename or "NIC" in filename:
            return "NIC4"
        elif "AVIRIS" in filename:
            return "AVIRIS"
        return "ASD"
    
    def _get_wavelengths(self, num_points: int, instrument: str = "ASD") -> np.ndarray:
        """
        根据数据点数和仪器类型生成波长数组
        
        参数:
            num_points: 数据点数量
            instrument: 仪器类型 (ASD, BECK, NIC4, AVIRIS)
            
        返回:
            波长数组 (纳米)
        """
        wavelength_files = {
            "ASD": "splib07a_Wavelengths_ASD_0.35-2.5_microns_2151_ch.txt",
            "BECK": "splib07a_Wavelengths_BECK_Beckman_0.2-3.0_microns.txt",
            "NIC4": "splib07a_Wavenumber_NIC4_Nicolet_8,900_-_46_cm^-1.txt",
            "AVIRIS": "splib07a_Wavelengths_AVIRIS_1996_0.37-2.5_microns.txt",
        }
        
        wavelength_file = self.library_path / wavelength_files.get(instrument, wavelength_files["ASD"])
        
        if wavelength_file.exists():
            try:
                wavelengths = []
                with open(wavelength_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("splib07a"):
                            try:
                                wavelengths.append(float(line) * 1000)
                            except ValueError:
                                continue
                if len(wavelengths) >= num_points:
                    return np.array(wavelengths[:num_points])
            except Exception:
                pass
        
        defaults = {
            "ASD": (350, 2500),
            "BECK": (200, 3000),
            "NIC4": (1120, 216000),
            "AVIRIS": (370, 2500),
        }
        wl_min, wl_max = defaults.get(instrument, (350, 2500))
        return np.linspace(wl_min, wl_max, num_points)
    
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


def get_wavelengths_from_file(filepath: str) -> Optional[np.ndarray]:
    """
    根据光谱文件获取对应的波长列
    
    参数:
        filepath: 光谱文件路径
        
    返回:
        波长数组或None
    """
    filepath = Path(filepath)
    if not filepath.exists():
        return None
    
    library_path = filepath.parent.parent
    
    instrument = "ASD"
    if "BECK" in filepath.name:
        instrument = "BECK"
    elif "ASD" in filepath.name or "ASDFR" in filepath.name or "ASDHR" in filepath.name:
        instrument = "ASD"
    elif "NIC4" in filepath.name or "NIC" in filepath.name:
        instrument = "NIC4"
    elif "AVIRIS" in filepath.name:
        instrument = "AVIRIS"
    
    wavelength_files = {
        "ASD": "splib07a_Wavelengths_ASD_0.35-2.5_microns_2151_ch.txt",
        "BECK": "splib07a_Wavelengths_BECK_Beckman_0.2-3.0_microns.txt",
        "NIC4": "splib07a_Wavelengths_NIC4_Nicolet_1.12-216microns.txt",
        "AVIRIS": "splib07a_Wavelengths_AVIRIS_1996_0.37-2.5_microns.txt",
    }
    
    wavelength_file = library_path / wavelength_files.get(instrument, wavelength_files["ASD"])
    
    if not wavelength_file.exists():
        return None
    
    try:
        wavelengths = []
        with open(wavelength_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("splib07a"):
                    try:
                        wavelengths.append(float(line) * 1000)
                    except ValueError:
                        continue
        return np.array(wavelengths)
    except Exception:
        return None


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