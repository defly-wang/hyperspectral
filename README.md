# 高光谱数据管理系统 - HyperspectralDMS

基于 PyQt6 开发的高光谱数据处理与可视化桌面应用程序。

## 功能特性

### 多语言支持
- **中文/英文切换**: 支持简体中文和英文两种语言
- 菜单 Language 可随时切换语言

### 数据查看
- **多格式支持**: 支持读取 `.isf` 和 `.xlsx/.xls` 格式的高光谱数据
- **光谱曲线显示**: 可视化波长与反射/透射率关系曲线
- **多文件查看**: 支持单选和多选文件，多选时在同一图表中显示多条曲线
- **伪彩色图像**: 将光谱数据转换为伪彩色图像展示
- **文件排序**: 文件列表按文件名排序

### 数据清洗
- **无效数据检测**: 空值、NaN、无穷值、负值、超出范围值、数据长度不匹配、方差过小
- **异常数据检测**: IQR和Z-Score两种方法，可调阈值
- **重复数据检测**: 基于相关系数的光谱相似度检测
- **文件格式检查**: 支持格式验证、表头检查、编码检测
- **报告导出**: 支持导出清洗报告
- **数据预览**: 点击问题列表查看对应光谱曲线

### 数据集分割
- **训练/验证/测试集分割**: 支持三种方式分割（训练集/验证集/测试集 或 训练集/测试集）
- **比例配置**: 可自定义训练集、验证集、测试集比例
- **进度显示**: 分割过程中显示进度条
- **自动清除**: 分割前自动清除旧文件
- **随机打乱**: 支持随机打乱数据，配置随机种子

### 数据预处理
- 平滑滤波 (Savitzky-Golay / 移动平均)
- 归一化 (Min-Max / Z-Score)
- 基线校正 (AirPLS / 基线扣除)
- 自动过滤 400nm 以下波长数据

### 模型训练
- 支持三种机器学习模型: Random Forest、SVM、Gradient Boosting
- 自动从目录加载训练数据（按子目录分类）
- 训练结果显示准确率、分类报告
- 模型保存与加载功能

### 识别
- 加载训练好的模型进行预测
- 支持批量识别多个文件
- 显示识别结果及置信度

## 环境要求

- Python 3.8+
- PyQt6
- NumPy
- Matplotlib
- SciPy
- openpyxl
- scikit-learn
- joblib

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

打包后的可执行文件位于 `dist/HyperspectralDMS/` 目录。

## 数据格式

### ISF 文件
- 波长列: `Wave[nm]`
- 数据列: `Refl/Tran[%]` (反射/透射率)

### XLSX 文件
- 波长列: 第一列 (Wave[nm])
- 数据列: 第五列 (Refl/Tran[%])

### 训练数据目录结构
```
training_data/
├── category1/
│   ├── sample1.xlsx
│   └── sample2.xlsx
├── category2/
│   └── sample1.xlsx
└── category3/
    └── sample1.xlsx
```

## 使用说明

### 数据查看
1. 点击 "Open Folder" 按钮选择数据文件夹
2. 在文件列表中单击选择文件（支持 Ctrl+多选 / Shift+连续选择）
3. 使用右侧预处理面板调整数据
4. 切换 "Spectrum" 和 "Image" 标签页查看不同展示

### 数据清洗
1. 切换到 "Data Cleaning" 标签页
2. 点击 "Select Folder..." 选择数据文件夹
3. 配置检测选项（无效数据、异常数据、重复数据）
4. 点击 "Start Analysis" 开始分析
5. 查看问题列表，点击查看对应光谱曲线
6. 可导出清洗报告

### 数据集分割
1. 切换到 "Data Split" 标签页
2. 点击 "Select Folder" 选择源数据文件夹（需包含分类子目录）
3. 点击 "Select Folder" 选择输出目录
4. 配置分割类型（训练/验证/测试集 或 训练/测试集）
5. 配置各数据集比例
6. 可选择是否打乱数据，设置随机种子
7. 点击 "开始分割" 开始分割
8. 分割完成后查看结果统计

### 模型训练
1. 切换到 "Model Training" 标签页
2. 点击 "Select..." 选择训练数据目录（需包含分类子目录）
3. 选择模型类型和测试集比例
4. 点击 "Start Training" 开始训练
5. 训练完成后可保存模型

### 识别
1. 切换到 "Recognition" 标签页
2. 点击 "Load Model..." 加载训练好的模型
3. 点击 "Select Files..." 选择要识别的文件
4. 点击 "Start Recognition" 开始识别
5. 查看识别结果及置信度

## 项目结构

```
hyperspectral/
├── main.py                      # 程序入口
├── requirements.txt              # Python 依赖
├── build.sh                     # 打包脚本
├── build.bat                    # Windows打包脚本
├── hyperspectral.spec           # PyInstaller 配置
└── src/
    ├── core/
    │   ├── isf_reader.py       # ISF 文件解析
    │   ├── xlsx_reader.py      # XLSX 文件解析
    │   ├── preprocessing.py    # 数据预处理
│   ├── model_trainer.py      # 机器学习模型
│   ├── data_cleaner.py       # 数据清洗
│   └── i18n.py                # 国际化
│   └── ui/
│       ├── main_window.py       # 主窗口
│       ├── file_browser.py      # 文件浏览器
│       ├── spectrum_plot.py     # 光谱曲线图
│       ├── image_view.py        # 伪彩色图像
│       ├── preprocessing_panel.py  # 预处理面板
│       ├── training_panel.py    # 模型训练面板
│       ├── recognition_panel.py # 识别面板
│       ├── data_cleaning_panel.py # 数据清洗面板
│       └── data_split_panel.py  # 数据集分割面板
```

## 快捷键

- `Ctrl+O`: 打开文件夹
- `Ctrl+T`: 打开模型训练面板
- `Ctrl+M`: 加载模型
- `Ctrl+R`: 打开识别面板
- `Ctrl+Q`: 退出程序

## 许可证

MIT License
