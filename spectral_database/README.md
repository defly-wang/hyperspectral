# 地质岩性高光谱数据库

本目录用于存放地质和岩性相关的高光谱数据库。

## 数据库列表

### 1. USGS Spectral Library Version 7 (美国地质调查局光谱库)

**简介**: USGS光谱库是全球最权威、最广泛使用的矿物、岩石、土壤、植物等材料的光谱数据库。包含从紫外到远红外的反射率光谱数据。

**官方主页**: https://www.usgs.gov/labs/spectroscopy-lab/science/spectral-library

**数据下载页面**: https://www.sciencebase.gov/catalog/item/586e8c88e4b0f5ce109fccae

**DOI**: https://doi.org/10.5066/F7RR1WDJ

**数据组成**:
- Chapter M = 矿物 (Minerals)
- Chapter S = 土壤和混合物 (Soils and Mixtures) - 包含岩石
- Chapter C = 涂层 (Coatings)
- Chapter L = 液体 (Liquids)
- Chapter O = 有机化合物 (Organic Compounds)
- Chapter A = 人工材料 (Artificial Materials)
- Chapter V = 植被 (Vegetation)

**光谱范围**: 0.2 - 200 微米

**主要文件**:
| 文件名 | 大小 | 说明 |
|--------|------|------|
| ASCIIdata_splib07a.zip | 20.8 MB | 原始测量光谱 |
| ASCIIdata_splib07b.zip | 41.4 MB | 过采样光谱 |
| ASCIIdata_splib07b_cvASD.zip | 27.1 MB | ASD标准分辨率卷积 |
| ASCIIdata_splib07b_cvAVIRISc2014.zip | 4.1 MB | AVIRIS 2014卷积 |
| ASCIIdata_splib07b_rsASTER.zip | 1.3 MB | ASTER重采样 |
| ASCIIdata_splib07b_rsSentinel2.zip | 1.4 MB | Sentinel-2重采样 |

**使用方法**:
```bash
# 下载ASCII光谱数据
cd spectral_database/usgs
wget "https://www.sciencebase.gov/catalog/file/get/586e8c88e4b0f5ce109fccae?name=ASCIIdata_splib07a.zip"
unzip ASCIIdata_splib07a.zip
```

**引用**:
Kokaly, R.F., Clark, R.N., Swayze, G.A., Livo, K.E., Hoefen, T.M., Pearson, N.C., Wise, R.A., Benzel, W.M., Lowers, H.A., Driscoll, R.L., and Klein, A.J., 2017, USGS Spectral Library Version 7: U.S. Geological Survey Data Series 1035, 61 p., https://doi.org/10.3133/ds1035

---

### 2. ASTER Spectral Library v2.0 (ASTER光谱库)

**简介**: NASA JPL维护的ASTER光谱库，收集了来自JHU、JPL和USGS的光谱数据。包含超过2300种自然和人工材料的光谱。

**官方主页**: https://speclib.jpl.nasa.gov

**数据下载**: https://speclib.jpl.nasa.gov/download

**数据组成**:
- Minerals (矿物): 3104 files
- Rocks (岩石): 647 files
- Soils (土壤): 120 files
- Vegetation (植被): 1966 files
- Man-made (人工材料): 72 files
- Lunar (月球): 17 files
- Meteorites (陨石): 59 files
- Non-Photosynthetic Vegetation: 162 files
- Water (水): 9 files

**光谱范围**: 0.4 - 15.4 微米 (VNIR-SWIR-TIR)

**使用方法**:
访问 https://speclib.jpl.nasa.gov/download 选择需要的光谱类别下载。

**引用**:
Baldridge, A.M., Hook, S.J., Grove, C.I., and Rivera, G., 2009, The ASTER spectral library version 2.0: Remote Sensing of Environment, v. 113, no. 4, p. 711-715, https://doi.org/10.1016/j.rse.2008.11.007

---

### 3. Coso Geothermal Spectral Library (科索地热光谱库)

**简介**: 专门针对地热勘探的光谱库，整合了USGS光谱库和Coso地热田(加利福尼亚)的野外观测数据。

**数据下载**: https://gdr.openei.org/submissions/1528

**DOI**: 10.15121/1999403

**使用设备**: ASD FieldSpec 便携式光谱仪

---

### 4. RockSL (岩石光谱库)

**简介**: 中国 CSU-PCP-XBS 团队整合的开放岩石矿物光谱库，汇集了USGS、JHU、JPL、ASU、MISA等主要光谱库。

**GitHub**: https://github.com/CSU-PCP-XBS/spectral-dataset-RockSL

**数据来源**:
| 光谱库 | 波长范围 | 粒度 | 共享格式 |
|--------|----------|------|----------|
| USGS | 0.2-200μm | μm级 | Yes |
| JHU | 0.4-14μm | Variable | Yes |
| JPL | 0.4-15.4μm | Variable | Yes |
| ASU | Variable | Variable | Yes |

---

## 文件格式说明

### USGS ASCII格式
```
# Wavelength range and data columns
# Example: splib07a_Ch__MaterialName_Wavelength_Spectrometer.txt
# Columns: wavelength(μm)  reflectance  std_dev  num_samples
```

### 数据读取示例 (Python)
```python
import numpy as np
import pandas as pd

# 读取USGS光谱数据
def read_usgs_spectrum(filepath):
    """读取USGS ASCII格式光谱文件"""
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('#') or line.strip() == '':
                continue
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    wavelength = float(parts[0])
                    reflectance = float(parts[1])
                    if reflectance > -1e30:  # 排除无效值 -1.23e34
                        data.append([wavelength, reflectance])
                except ValueError:
                    continue
    return np.array(data)

# 使用示例
spectrum = read_usgs_spectrum('splib07a_Chr_Muscovite_GDS55_80600_BECKA.txt')
```

---

## 建议下载

对于岩性分析，推荐下载以下文件：

1. **ASCIIdata_splib07a.zip** - 包含所有原始测量光谱
2. **ASCIIdata_splib07b_rsASTER.zip** - ASTER卫星波段重采样光谱（适合ASTER数据应用）
3. **ASCIIdata_splib07b_rsSentinel2.zip** - Sentinel-2波段重采样光谱

---

## 注意事项

1. USGS光谱库完整包约5.1GB，建议只下载需要的ASCII数据文件
2. 矿物(Minerals)和土壤/岩石(Soils/Mixtures)章节对岩性分析最有用
3. 原始测量数据(splib07a)波长覆盖最广，但ASD卷积数据(splib07b_cvASD)更适合大多数遥感应用
