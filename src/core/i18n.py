import os
from typing import Dict

translations: Dict[str, Dict[str, str]] = {
    "zh_CN": {
        # Main Window
        "window_title": "高光谱数据管理系统 - HyperspectralDMS",
        "file": "文件",
        "open_folder": "打开文件夹...",
        "exit": "退出",
        "view": "视图",
        "reset_view": "重置视图",
        "model": "模型",
        "train_model": "训练模型...",
        "load_model": "加载模型...",
        "recognition": "识别...",
        "help": "帮助",
        "about": "关于",
        
        # Preview Tab
        "preview": "预览",
        "no_folder_selected": "未选择文件夹",
        "open_folder_btn": "打开文件夹",
        "files": "文件",
        
        # Preprocessing
        "smoothing": "平滑滤波",
        "normalization": "归一化",
        "baseline_correction": "基线校正",
        "none": "无",
        "savitzky_golay": "Savitzky-Golay",
        "moving_average": "移动平均",
        "min_max": "Min-Max",
        "z_score": "Z-Score",
        "airpls": "AirPLS",
        "subtract_baseline": "基线扣除",
        
        # Spectrum Plot
        "wavelength": "波长 (nm)",
        "intensity": "强度",
        
        # Data Cleaning Tab
        "data_cleaning": "数据清洗",
        "data_source": "数据源",
        "select_folder": "选择文件夹...",
        "detection_options": "检测选项",
        "detect_invalid_data": "检测无效数据",
        "detect_anomalies": "检测异常数据",
        "method": "方法",
        "threshold": "阈值",
        "detect_duplicates": "检测重复数据",
        "similarity": "相似度",
        "start_analysis": "开始分析",
        "analysis_results": "分析结果",
        "file_col": "文件",
        "type_col": "类型",
        "severity_col": "严重程度",
        "description_col": "描述",
        "spectrum_preview": "光谱预览",
        "actions": "操作",
        "export_report": "导出报告",
        "clear": "清除",
        
        # Issue Types
        "invalid_file": "无效文件",
        "invalid_format": "格式错误",
        "load_error": "加载错误",
        "insufficient_data": "数据不足",
        "empty": "数据为空",
        "mismatch": "数据不匹配",
        "nan": "包含NaN值",
        "inf": "包含无穷值",
        "negative": "包含负值",
        "overflow": "值溢出",
        "invalid_wavelength": "波长无效",
        "flat": "数据过于平坦",
        "anomaly": "异常数据",
        "duplicate": "重复数据",
        
        # Severity
        "high": "高",
        "medium": "中",
        "low": "低",
        
        # Model Training Tab
        "model_training": "模型训练",
        "training_data": "训练数据",
        "data_directory": "数据目录",
        "model_settings": "模型设置",
        "model_type": "模型类型",
        "random_forest": "Random Forest",
        "svm": "SVM",
        "gradient_boosting": "Gradient Boosting",
        "test_size": "测试集比例",
        "start_training": "开始训练",
        "save_model": "保存模型",
        "results": "结果",
        "no_directory_selected": "未选择目录",
        "no_category_found": "未找到分类子目录",
        
        # Recognition Tab
        "recognition_tab": "识别",
        "load_model_btn": "加载模型...",
        "recognition_files": "识别文件",
        "select_files": "选择文件...",
        "start_recognition": "开始识别",
        "recognition_results": "识别结果",
        
        # Messages
        "ready": "就绪",
        "loaded_files": "已加载 {count} 个文件",
        "loaded": "已加载: {filename}",
        "files_selected": "已选择 {count} 个文件",
        "training_results": "训练结果",
        "accuracy": "准确率",
        "training_samples": "训练样本数",
        "test_samples": "测试样本数",
        "number_of_classes": "类别数",
        "classification_report": "分类报告",
        "model_saved": "模型已保存",
        "model_loaded": "模型已加载",
        
        # About Dialog
        "about_title": "关于",
        "about_description": "高光谱数据处理与可视化工具。",
        "supported_format": "支持格式: iSpecField (.isf)",
        
        # Language
        "language": "语言",
        "chinese": "中文",
        "english": "English",
    },
    "en_US": {
        # Main Window
        "window_title": "Hyperspectral Data Management System - HyperspectralDMS",
        "file": "File",
        "open_folder": "Open Folder...",
        "exit": "Exit",
        "view": "View",
        "reset_view": "Reset View",
        "model": "Model",
        "train_model": "Train Model...",
        "load_model": "Load Model...",
        "recognition": "Recognition...",
        "help": "Help",
        "about": "About",
        
        # Preview Tab
        "preview": "Preview",
        "no_folder_selected": "No folder selected",
        "open_folder_btn": "Open Folder",
        "files": "files",
        
        # Preprocessing
        "smoothing": "Smoothing",
        "normalization": "Normalization",
        "baseline_correction": "Baseline Correction",
        "none": "None",
        "savitzky_golay": "Savitzky-Golay",
        "moving_average": "Moving Average",
        "min_max": "Min-Max",
        "z_score": "Z-Score",
        "airpls": "AirPLS",
        "subtract_baseline": "Subtract Baseline",
        
        # Spectrum Plot
        "wavelength": "Wavelength (nm)",
        "intensity": "Intensity",
        
        # Data Cleaning Tab
        "data_cleaning": "Data Cleaning",
        "data_source": "Data Source",
        "select_folder": "Select Folder...",
        "detection_options": "Detection Options",
        "detect_invalid_data": "Detect Invalid Data",
        "detect_anomalies": "Detect Anomalies",
        "method": "Method",
        "threshold": "Threshold",
        "detect_duplicates": "Detect Duplicates",
        "similarity": "Similarity",
        "start_analysis": "Start Analysis",
        "analysis_results": "Analysis Results",
        "file_col": "File",
        "type_col": "Type",
        "severity_col": "Severity",
        "description_col": "Description",
        "spectrum_preview": "Spectrum Preview",
        "actions": "Actions",
        "export_report": "Export Report",
        "clear": "Clear",
        
        # Issue Types
        "invalid_file": "Invalid File",
        "invalid_format": "Invalid Format",
        "load_error": "Load Error",
        "insufficient_data": "Insufficient Data",
        "empty": "Empty Data",
        "mismatch": "Data Mismatch",
        "nan": "Contains NaN",
        "inf": "Contains Inf",
        "negative": "Contains Negative",
        "overflow": "Value Overflow",
        "invalid_wavelength": "Invalid Wavelength",
        "flat": "Data Too Flat",
        "anomaly": "Anomaly",
        "duplicate": "Duplicate",
        
        # Severity
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        
        # Model Training Tab
        "model_training": "Model Training",
        "training_data": "Training Data",
        "data_directory": "Data Directory",
        "model_settings": "Model Settings",
        "model_type": "Model Type",
        "random_forest": "Random Forest",
        "svm": "SVM",
        "gradient_boosting": "Gradient Boosting",
        "test_size": "Test Size",
        "start_training": "Start Training",
        "save_model": "Save Model",
        "results": "Results",
        "no_directory_selected": "No directory selected",
        "no_category_found": "No category subdirectories found",
        
        # Recognition Tab
        "recognition_tab": "Recognition",
        "load_model_btn": "Load Model...",
        "recognition_files": "Recognition Files",
        "select_files": "Select Files...",
        "start_recognition": "Start Recognition",
        "recognition_results": "Recognition Results",
        
        # Messages
        "ready": "Ready",
        "loaded_files": "Loaded {count} files",
        "loaded": "Loaded: {filename}",
        "files_selected": "{count} files selected",
        "training_results": "Training Results",
        "accuracy": "Accuracy",
        "training_samples": "Training Samples",
        "test_samples": "Test Samples",
        "number_of_classes": "Number of Classes",
        "classification_report": "Classification Report",
        "model_saved": "Model saved",
        "model_loaded": "Model loaded",
        
        # About Dialog
        "about_title": "About",
        "about_description": "Hyperspectral data processing and visualization tool.",
        "supported_format": "Supported format: iSpecField (.isf)",
        
        # Language
        "language": "Language",
        "chinese": "中文",
        "english": "English",
    }
}


class LanguageManager:
    _instance = None
    _current_language = "zh_CN"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def set_language(self, lang: str):
        if lang in translations:
            self._current_language = lang
    
    def get_language(self) -> str:
        return self._current_language
    
    def t(self, key: str) -> str:
        return translations.get(self._current_language, {}).get(key, key)
    
    def get_available_languages(self):
        return list(translations.keys())


def t(key: str) -> str:
    return LanguageManager().t(key)


def set_language(lang: str):
    LanguageManager().set_language(lang)


def get_current_language():
    return LanguageManager().get_language()
