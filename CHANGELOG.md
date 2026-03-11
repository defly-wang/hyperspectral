# 版本变化日志

## [Unreleased]

## [1.0.0] - 2026-03-11

### 新增功能
- **数据查看功能**
  - 支持读取 `.isf` 格式高光谱数据文件
  - 支持读取 `.xlsx/.xls` 格式高光谱数据文件
  - 光谱曲线可视化显示（波长 vs 反射/透射率）
  - 多文件选择支持（Ctrl+多选、Shift+连续选择）
  - 多光谱曲线对比显示

- **伪彩色图像**
  - 将光谱数据转换为伪彩色图像展示

- **数据预处理**
  - 平滑滤波：Savitzky-Golay 滤波、移动平均滤波
  - 归一化：Min-Max 归一化、Z-Score 标准化
  - 基线校正：AirPLS、基线扣除
  - 自动过滤 500nm 以下波长数据

- **模型训练**
  - Random Forest 分类器
  - SVM 分类器
  - Gradient Boosting 分类器
  - 训练数据自动从目录加载（按子目录分类）
  - 训练结果准确率显示
  - 详细分类报告（Precision、Recall、F1-Score）
  - 模型保存功能（.pkl 格式）

### UI/UX 改进
- 基于 PyQt6 的现代化桌面界面
- 菜单栏：文件、视图、模型、帮助
- 标签页切换：Preview / Model Training
- 状态栏显示当前操作状态
- 快捷键支持（Ctrl+O、Ctrl+T、Ctrl+Q）

### 项目初始化
- 项目结构搭建
- PyInstaller 打包配置
- requirements.txt 依赖管理
