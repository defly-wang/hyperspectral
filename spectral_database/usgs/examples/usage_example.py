#!/usr/bin/env python3
"""
光谱数据库使用示例

展示如何加载和可视化USGS光谱库数据

依赖: numpy, pandas, matplotlib
安装: pip install numpy pandas matplotlib
"""

import os
import sys

try:
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    HAS_FULL = True
except ImportError as e:
    HAS_FULL = False
    print("警告: 部分依赖缺失，功能受限")
    print(f"缺少: {e}")
    print("请安装: pip install numpy pandas matplotlib")
    np = None
    pd = None

def load_example_spectrum(filepath):
    """加载示例光谱CSV文件"""
    if pd:
        df = pd.read_csv(filepath)
        df.columns = ['wavelength', 'reflectance']  # 标准化列名
        return df
    else:
        wavelengths = []
        reflectances = []
        with open(filepath, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('wavelength'):
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        wavelengths.append(float(parts[0]))
                        reflectances.append(float(parts[1]))
        class SimpleDF:
            def __init__(self, wl, refl):
                self._wl = wl
                self._refl = refl
                self._wavelength = np.array(wl) if np else wl
                self._reflectance = np.array(refl) if np else refl
            def __getitem__(self, key):
                if key == 'wavelength':
                    return self._wavelength
                elif key == 'reflectance':
                    return self._reflectance
            def keys(self):
                return ['wavelength', 'reflectance']
            def items(self):
                return [('wavelength', self._wavelength), ('reflectance', self._reflectance)]
        return SimpleDF(wavelengths, reflectances)

def load_usgs_ascii(filepath):
    """加载USGS ASCII格式光谱文件"""
    wavelengths = []
    reflectances = []
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 2:
                try:
                    wl = float(parts[0])
                    refl = float(parts[1])
                    if refl > -1e30:
                        wavelengths.append(wl)
                        reflectances.append(refl)
                except ValueError:
                    continue
    
    if pd:
        return pd.DataFrame({'wavelength': wavelengths, 'reflectance': reflectances})
    else:
        class SimpleDF:
            def __init__(self, wl, refl):
                self._wavelength = np.array(wl) if np else wl
                self._reflectance = np.array(refl) if np else refl
            def __getitem__(self, key):
                if key == 'wavelength':
                    return self._wavelength
                elif key == 'reflectance':
                    return self._reflectance
            def keys(self):
                return ['wavelength', 'reflectance']
            def items(self):
                return [('wavelength', self._wavelength), ('reflectance', self._reflectance)]
        return SimpleDF(wavelengths, reflectances)

def find_absorption_features(df, threshold=0.1):
    """简单检测吸收特征"""
    if not np:
        return []
    
    absorptions = []
    wavelengths = df['wavelength']
    reflectances = df['reflectance']
    mean_refl = np.mean(reflectances)
    
    for i in range(1, len(reflectances)-1):
        if (reflectances[i] < reflectances[i-1] and
            reflectances[i] < reflectances[i+1] and
            mean_refl - reflectances[i] > threshold):
            absorptions.append(wavelengths[i])
    
    return absorptions

def plot_spectra(spectra_dict, title="Mineral Spectra", save_path=None):
    """绘制多条光谱曲线"""
    if not HAS_FULL:
        print("可视化需要完整依赖: pip install numpy pandas matplotlib")
        return
    
    plt.figure(figsize=(12, 8))
    
    for name, df in spectra_dict.items():
        plt.plot(df['wavelength'], df['reflectance'], label=name, linewidth=1.5)
    
    plt.xlabel('Wavelength (um)', fontsize=12)
    plt.ylabel('Reflectance', fontsize=12)
    plt.title(title, fontsize=14)
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.xlim(0.35, 2.5)
    plt.ylim(0, 1)
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.close()

def main():
    examples_dir = os.path.dirname(__file__)
    
    print("=" * 60)
    print("Spectral Database Usage Example")
    print("=" * 60)
    
    minerals = {}
    for filename in os.listdir(examples_dir):
        if filename.endswith('.csv'):
            name = filename.replace('_typical.csv', '')
            filepath = os.path.join(examples_dir, filename)
            minerals[name] = load_example_spectrum(filepath)
            print(f"Loaded: {name}")
    
    print(f"\nTotal: {len(minerals)} mineral spectra examples loaded")
    
    print("\n" + "=" * 60)
    print("Absorption Features Analysis")
    print("=" * 60)
    for name, df in minerals.items():
        absorptions = find_absorption_features(df)
        if absorptions:
            print(f"{name}: Absorptions at ~{', '.join([f'{a:.2f}um' for a in absorptions])}")
    
    print("\n" + "=" * 60)
    print("Visualization")
    print("=" * 60)
    
    if minerals:
        output_path = os.path.join(examples_dir, 'mineral_spectra_comparison.png')
        plot_spectra(minerals, title="Common Mineral Spectra (Examples)", save_path=output_path)
    
    print("\nUsage:")
    print("1. Download full USGS library: python download_usgs_spectral.py --all")
    print("2. List chapter directories:")
    print("   ls ChapterM_Minerals/     # Minerals")
    print("   ls ChapterS_SoilsAndMixtures/  # Rocks/Soils")
    print("3. Load full spectra:")
    print("   df = load_usgs_ascii('ChapterM_Minerals/splib07a_Chr_MineralName.txt')")

if __name__ == "__main__":
    main()
