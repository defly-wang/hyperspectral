"""
预览面板

集成文件浏览器、光谱绘图、图像视图和预处理功能，用于预览光谱数据

主要功能:
    - 文件浏览器：选择文件夹，显示光谱文件列表
    - 光谱绘图：显示选中文件的原始光谱
    - 图像视图：显示伪彩色图像
    - 预处理：平滑、归一化、基线校正
    - 支持本地文件和USGS光谱库数据

信号:
    files_loaded: 文件加载完成时发射，参数为文件路径到数据的字典

用法:
    panel = PreviewPanel()
    panel.file_browser._open_folder()  # 打开文件夹选择对话框
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
                              QComboBox, QPushButton, QGroupBox, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
import os

from .file_browser import FileBrowserWidget
from .spectrum_plot import SpectrumPlotWidget
from .image_view import ImageViewWidget
from .preprocessing_panel import PreprocessingPanel
from ..core.i18n import t


class PreviewPanel(QWidget):
    """
    预览面板widget
    
    整合文件浏览、光谱显示和预处理功能，是应用的主要预览界面
    """
    
    files_loaded = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """
        初始化预览面板
        
        Args:
            parent: 父widget
        """
        super().__init__(parent)
        
        self.loaded_data = {}
        self.usgs_library = None
        self.usgs_mode = False
        self._init_ui()
        self._init_usgs_library()
    
    def _init_usgs_library(self):
        """初始化USGS光谱库"""
        try:
            from ..core.usgs_reader import USGSSpectralLibrary
            from pathlib import Path
            lib_path = Path(__file__).parent.parent.parent / "spectral_database" / "usgs" / "ASCIIdata_splib07a"
            if lib_path.exists():
                self.usgs_library = USGSSpectralLibrary(str(lib_path))
        except Exception:
            self.usgs_library = None
    
    def _init_ui(self):
        """构建UI布局"""
        main_layout = QVBoxLayout(self)
        
        # 数据源选择
        source_group = QGroupBox(t("data_source") if hasattr(t, '__call__') else "数据源")
        source_layout = QHBoxLayout()
        
        self.source_combo = QComboBox()
        self.source_combo.addItem("本地文件", "local")
        self.source_combo.addItem("USGS光谱库", "usgs")
        self.source_combo.currentIndexChanged.connect(self._on_source_changed)
        source_layout.addWidget(QLabel(t("data_source") + ":" if hasattr(t, '__call__') else "数据源:"))
        source_layout.addWidget(self.source_combo)
        source_layout.addStretch()
        source_group.setLayout(source_layout)
        
        main_layout.addWidget(source_group)
        
        # 左侧面板：文件浏览器 + 预处理
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        self.file_browser = FileBrowserWidget()
        self.preprocessing_panel = PreprocessingPanel()
        
        left_layout.addWidget(self.file_browser, stretch=2)
        left_layout.addWidget(self.preprocessing_panel, stretch=1)
        
        # USGS选择面板
        self.usgs_select_widget = QWidget()
        usgs_layout = QVBoxLayout(self.usgs_select_widget)
        
        self.usgs_category_combo = QComboBox()
        self.usgs_category_combo.addItem("全部", "all")
        usgs_layout.addWidget(QLabel("类别:"))
        usgs_layout.addWidget(self.usgs_category_combo)
        
        self.usgs_subcategory_combo = QComboBox()
        self.usgs_subcategory_combo.addItem("全部子类别", "all")
        usgs_layout.addWidget(QLabel("子类别:"))
        usgs_layout.addWidget(self.usgs_subcategory_combo)
        
        self.usgs_spectrum_list = QComboBox()
        self.usgs_spectrum_list.currentIndexChanged.connect(self._on_usgs_spectrum_selected)
        usgs_layout.addWidget(QLabel("光谱:"))
        usgs_layout.addWidget(self.usgs_spectrum_list)
        
        self.usgs_select_widget.setVisible(False)
        left_layout.insertWidget(0, self.usgs_select_widget)
        
        # 右侧面板：光谱图 + 伪彩图
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.spectrum_plot = SpectrumPlotWidget()
        self.image_view = ImageViewWidget()
        
        right_layout.addWidget(self.spectrum_plot, stretch=1)
        right_layout.addWidget(self.image_view, stretch=1)
        
        # 使用分割器组织左右布局
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        
        # 连接信号槽
        self.file_browser.folder_selected.connect(self._on_folder_selected)
        self.file_browser.files_selected.connect(self._on_files_selected)
        self.preprocessing_panel.preprocessing_changed.connect(self._apply_preprocessing)
        
        if self.usgs_library:
            self._init_usgs_ui()
    
    def _init_usgs_ui(self):
        """初始化USGS UI"""
        from ..core.usgs_reader import USGSSpectralLibrary
        
        for en_name, cn_name in USGSSpectralLibrary.CHAPTERS.items():
            self.usgs_category_combo.addItem(f"{cn_name} ({en_name})", en_name)
            self.usgs_category_combo.addItem(f"{cn_name} ({en_name})", en_name)
        
        self.usgs_category_combo.currentIndexChanged.connect(self._on_usgs_category_changed)
    
    def _on_source_changed(self, index):
        """数据源切换"""
        source = self.source_combo.currentData()
        self.usgs_mode = (source == "usgs")
        
        self.file_browser.setVisible(not self.usgs_mode)
        self.usgs_select_widget.setVisible(self.usgs_mode)
        
        if self.usgs_mode:
            self._apply_usgs_preprocessing()
        else:
            self._apply_preprocessing()
    
    def _on_usgs_category_changed(self, index):
        """USGS类别切换"""
        if not self.usgs_library:
            return
        
        self.usgs_subcategory_combo.clear()
        self.usgs_subcategory_combo.addItem("全部子类别", "all")
        
        category = self.usgs_category_combo.currentData()
        if category == "all":
            return
        
        from ..core.usgs_reader import USGSSpectralLibrary
        
        sub_cats = self.usgs_library.get_sub_categories(category)
        for sub_cat in sub_cats:
            display_name = USGSSpectralLibrary.get_sub_category_display_name(sub_cat)
            self.usgs_subcategory_combo.addItem(display_name, sub_cat)
        
        self._update_usgs_spectrum_list()
    
    def _update_usgs_spectrum_list(self):
        """更新USGS光谱列表"""
        from ..core.usgs_reader import USGSSpectralLibrary
        
        self.usgs_spectrum_list.clear()
        
        if not self.usgs_library:
            return
        
        category = self.usgs_category_combo.currentData()
        sub_category = self.usgs_subcategory_combo.currentData()
        
        if category == "all":
            spectra = self.usgs_library.get_all_spectra()
        elif sub_category == "all":
            spectra = self.usgs_library.get_spectra_by_category(category)
        else:
            spectra = self.usgs_library.get_spectra_by_sub_category(category, sub_category)
        
        for filepath, metadata in spectra[:500]:
            self.usgs_spectrum_list.addItem(metadata.name, filepath)
    
    def _on_usgs_spectrum_selected(self, index):
        """USGS光谱选中"""
        if index < 0:
            return
        
        filepath = self.usgs_spectrum_list.currentData()
        if filepath and self.usgs_library:
            spectrum = self.usgs_library.load_spectrum(filepath)
            if spectrum:
                self.loaded_data = {"usgs": spectrum}
                self._apply_usgs_preprocessing()
    
    def _apply_usgs_preprocessing(self):
        """应用USGS光谱预处理"""
        if "usgs" not in self.loaded_data:
            return
        
        from ..core.preprocessing import Preprocessor
        
        spectrum = self.loaded_data["usgs"]
        wavelengths = spectrum.wavelengths.copy()
        intensities = spectrum.intensities.copy()
        
        mask = wavelengths >= 350
        wavelengths = wavelengths[mask]
        intensities = intensities[mask]
        
        smooth_method = self.preprocessing_panel.get_smoothing_method()
        if smooth_method != "None":
            params = self.preprocessing_panel.get_smoothing_params()
            if smooth_method == "Savitzky-Golay":
                intensities = Preprocessor.apply(intensities, "Savitzky-Golay", **params)
            elif smooth_method == "Moving Average":
                intensities = Preprocessor.apply(intensities, "Moving Average", window=params['window'])
        
        norm_method = self.preprocessing_panel.get_normalization_method()
        if norm_method != "None":
            if norm_method == "Min-Max":
                intensities = Preprocessor.apply(intensities, "Min-Max")
            elif norm_method == "Z-Score":
                intensities = Preprocessor.apply(intensities, "Z-Score")
        
        baseline_method = self.preprocessing_panel.get_baseline_method()
        if baseline_method != "None":
            if baseline_method == "AirPLS" or baseline_method == "Subtract Baseline":
                intensities = Preprocessor.apply(intensities, "Subtract Baseline")
        
        title = spectrum.metadata.name
        self.spectrum_plot.plot_spectrum(wavelengths, intensities, title=title)
        self.image_view.show_fake_hsi_image(wavelengths, intensities, title=title)
    
    def _on_folder_selected(self, folder: str):
        """
        文件夹选中处理
        
        扫描选中文件夹中的光谱文件(.isf, .xlsx, .xls)并显示
        
        Args:
            folder: 文件夹路径
        """
        isf_files = [f for f in os.listdir(folder) if f.lower().endswith('.isf')]
        xlsx_files = [f for f in os.listdir(folder) if f.lower().endswith(('.xlsx', '.xls'))]
        all_files = isf_files + xlsx_files
        files = [os.path.join(folder, f) for f in all_files]
        self.file_browser.set_files(files)
        self.loaded_data = {}
    
    def _on_files_selected(self, filepaths: list):
        """
        文件选中处理
        
        加载选中文件的数据并应用预处理
        
        Args:
            filepaths: 文件路径列表
        """
        if not filepaths:
            return
        
        from ..core.isf_reader import parse_isf_file
        from ..core.xlsx_reader import parse_xlsx_file
        
        try:
            self.loaded_data = {}
            for filepath in filepaths:
                ext = os.path.splitext(filepath)[1].lower()
                if ext in ('.xlsx', '.xls'):
                    data = parse_xlsx_file(filepath)
                else:
                    data = parse_isf_file(filepath)
                self.loaded_data[filepath] = data
            
            self._apply_preprocessing()
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
    
    def _apply_preprocessing(self):
        """
        应用预处理
        
        根据预处理面板设置对加载的数据进行处理，
        并更新光谱图和伪彩图显示
        """
        if not self.loaded_data:
            return
        
        from ..core.preprocessing import Preprocessor
        
        selected_files = self.file_browser.get_selected_files()
        if not selected_files:
            return
        
        spectra_to_plot = []
        
        for filepath in selected_files:
            if filepath not in self.loaded_data:
                continue
            
            data = self.loaded_data[filepath]
            # 过滤350nm以下的数据
            mask = data.wavelengths >= 350
            wavelengths = data.wavelengths[mask]
            intensities = data.intensities[mask].copy()
            
            # 平滑处理
            smooth_method = self.preprocessing_panel.get_smoothing_method()
            if smooth_method != "None":
                params = self.preprocessing_panel.get_smoothing_params()
                if smooth_method == "Savitzky-Golay":
                    intensities = Preprocessor.apply(intensities, "Savitzky-Golay", **params)
                elif smooth_method == "Moving Average":
                    intensities = Preprocessor.apply(intensities, "Moving Average", window=params['window'])
            
            # 归一化处理
            norm_method = self.preprocessing_panel.get_normalization_method()
            if norm_method != "None":
                if norm_method == "Min-Max":
                    intensities = Preprocessor.apply(intensities, "Min-Max")
                elif norm_method == "Z-Score":
                    intensities = Preprocessor.apply(intensities, "Z-Score")
            
            # 基线校正
            baseline_method = self.preprocessing_panel.get_baseline_method()
            if baseline_method != "None":
                if baseline_method == "AirPLS" or baseline_method == "Subtract Baseline":
                    intensities = Preprocessor.apply(intensities, "Subtract Baseline")
            
            filename = os.path.basename(filepath)
            spectra_to_plot.append((wavelengths, intensities, filename))
        
        # 更新光谱图
        if len(spectra_to_plot) == 1:
            wl, intensity, name = spectra_to_plot[0]
            self.spectrum_plot.plot_spectrum(wl, intensity, title=name)
        else:
            self.spectrum_plot.plot_multiple_spectra(spectra_to_plot, title=f"{len(spectra_to_plot)} Spectra")
        
        # 更新伪彩图
        if spectra_to_plot:
            if len(spectra_to_plot) == 1:
                wl, intensity, name = spectra_to_plot[0]
                self.image_view.show_fake_hsi_image(wl, intensity, title=name)
            else:
                self.image_view.show_multiple_images(spectra_to_plot)
    
    def refresh_text(self):
        """
        刷新界面文本（用于语言切换）
        """
        self.preprocessing_panel.refresh_text()
    
    def clear(self):
        """
        清空显示内容
        """
        self.spectrum_plot.clear()
        self.image_view.clear()
        self.loaded_data = {}
