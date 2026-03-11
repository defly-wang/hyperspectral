# 高光谱数据查看器

基于 PyQt6 开发的高光谱数据处理与可视化桌面应用程序。

## 功能特性

- **多格式支持**: 支持读取 `.isf` 和 `.xlsx/.xls` 格式的高光谱数据
- **光谱曲线显示**: 可视化波长与反射/透射率关系曲线
- **多文件查看**: 支持单选和多选文件，多选时在同一图表中显示多条曲线
- **伪彩色图像**: 将光谱数据转换为伪彩色图像展示
- **数据预处理**:
  - 平滑滤波 (Savitzky-Golay / 移动平均)
  - 归一化 (Min-Max / Z-Score)
  - 基线校正 (AirPLS / 基线扣除)
- **波长过滤**: 自动过滤掉 500nm 以下的波长数据

## 环境要求

- Python 3.8+
- PyQt6
- NumPy
- Matplotlib
- SciPy
- openpyxl

## 安装

1. 创建虚拟环境:
```bash
python3 -m venv venv
```

2. 激活虚拟环境:
```bash
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖:
```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## 打包

```bash
./build.sh
```

打包后的可执行文件位于 `dist/HyperspectralViewer/` 目录。

## 数据格式

### ISF 文件

- 波长列: `Wave[nm]`
- 数据列: `Refl/Tran[%]` (反射/透射率)

### XLSX 文件

- 波长列: 第一列 (Wave[nm])
- 数据列: 第五列 (Refl/Tran[%])

## 使用说明

1. 点击 "Open Folder" 按钮选择数据文件夹
2. 在文件列表中单击选择文件（支持 Ctrl+多选 / Shift+连续选择）
3. 使用右侧预处理面板调整数据
4. 切换 "Spectrum" 和 "Image" 标签页查看不同展示

## 项目结构

```
hyperspectral/
├── main.py                      # 程序入口
├── requirements.txt              # Python 依赖
├── build.sh                     # 打包脚本
├── hyperspectral.spec           # PyInstaller 配置
└── src/
    ├── core/
    │   ├── isf_reader.py       # ISF 文件解析
    │   ├── xlsx_reader.py      # XLSX 文件解析
    │   └── preprocessing.py    # 数据预处理
    └── ui/
        ├── main_window.py       # 主窗口
        ├── file_browser.py      # 文件浏览器
        ├── spectrum_plot.py     # 光谱曲线图
        ├── image_view.py        # 伪彩色图像
        └── preprocessing_panel.py  # 预处理面板
```

## 许可证

MIT License
