"""
光谱库面板

提供USGS光谱库的浏览、搜索和加载功能

功能:
    - 浏览光谱库各类别
    - 搜索光谱
    - 加载光谱数据进行可视化
    - 光谱对比分析

信号:
    spectrum_loaded: 加载光谱时发射
    compare_spectrum: 请求对比光谱时发射
"""

import os
from pathlib import Path
from typing import Optional, List, Tuple

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QListWidget, QListWidgetItem,
                             QLineEdit, QComboBox, QSplitter, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView,
                             QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from ..core.usgs_reader import USGSSpectralLibrary, USGSSpectrumData
from .spectrum_plot import SpectrumPlotWidget


class SpectralLibraryPanel(QWidget):
    """
    光谱库面板widget
    
    提供USGS光谱库管理和数据加载功能
    """
    
    spectrum_loaded = pyqtSignal(object)
    compare_spectrum = pyqtSignal(object)
    
    def __init__(self, parent=None):
        """
        初始化光谱库面板
        
        Args:
            parent: 父widget
        """
        super().__init__(parent)
        
        self.current_library: Optional[USGSSpectralLibrary] = None
        self.selected_spectrum: Optional[USGSSpectrumData] = None
        self.compare_spectra: List[USGSSpectrumData] = []
        
        self._init_ui()
        self._init_library()
    
    def _init_ui(self):
        """初始化UI"""
        main_layout = QHBoxLayout(self)
        
        left_layout = QVBoxLayout()
        
        category_group = QGroupBox("光谱类别")
        category_layout = QVBoxLayout()
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("全部", "all")
        
        for en_name, cn_name in USGSSpectralLibrary.CHAPTERS.items():
            self.category_combo.addItem(f"{cn_name} ({en_name})", en_name)
        
        self.sub_category_combo = QComboBox()
        self.sub_category_combo.addItem("全部子类别", "all")
        
        category_layout.addWidget(self.category_combo)
        category_layout.addWidget(self.sub_category_combo)
        category_group.setLayout(category_layout)
        
        search_group = QGroupBox("搜索")
        search_layout = QVBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入光谱名称搜索...")
        self.search_btn = QPushButton("搜索")
        
        search_h_layout = QHBoxLayout()
        search_h_layout.addWidget(self.search_input)
        search_h_layout.addWidget(self.search_btn)
        
        search_layout.addLayout(search_h_layout)
        search_group.setLayout(search_layout)
        
        list_group = QGroupBox("光谱列表")
        list_layout = QVBoxLayout()
        
        self.spectrum_list = QListWidget()
        self.spectrum_list.setMaximumWidth(350)
        self.spectrum_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.spectrum_list.itemSelectionChanged.connect(self._on_spectrum_selected)
        self.spectrum_list.itemDoubleClicked.connect(self._on_spectrum_double_clicked)
        
        list_layout.addWidget(self.spectrum_list)
        list_group.setLayout(list_layout)
        
        info_group = QGroupBox("光谱信息")
        info_layout = QVBoxLayout()
        
        self.info_table = QTableWidget()
        self.info_table.setColumnCount(2)
        self.info_table.setHorizontalHeaderLabels(["属性", "值"])
        self.info_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.info_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.info_table.setColumnWidth(0, 120)
        self.info_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.info_table.setMaximumHeight(120)
        
        info_layout.addWidget(self.info_table)
        info_group.setLayout(info_layout)
        
        left_layout.addWidget(category_group)
        left_layout.addWidget(search_group)
        left_layout.addWidget(list_group)
        left_layout.addWidget(info_group)
        
        right_layout = QVBoxLayout()
        
        self.plot_widget = SpectrumPlotWidget()
        
        right_layout.addWidget(self.plot_widget)
        
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        self.sub_category_combo.currentIndexChanged.connect(self._on_sub_category_changed)
        self.search_btn.clicked.connect(self._on_search)
        self.search_input.returnPressed.connect(self._on_search)
    
    def _init_library(self):
        """初始化光谱库"""
        lib_path = Path(__file__).parent.parent.parent / "spectral_database" / "usgs" / "ASCIIdata_splib07a"
        
        if lib_path.exists():
            self.current_library = USGSSpectralLibrary(str(lib_path))
            self._update_list()    

    def set_status_label(self, label):
        """设置状态标签"""
        self.statusLabel = label
        if self.current_library:
            self.statusLabel.setText(f"已加载 {self.current_library.get_total_count()} 个光谱")
        else:
            self.statusLabel.setText("未找到光谱库")
    
    def _update_list(self, spectra_list: Optional[List] = None):
        """
        更新光谱列表
        
        Args:
            spectra_list: 光谱列表(可选，默认使用当前类别)
        """
        self.spectrum_list.clear()
        
        if spectra_list is None:
            if self.current_library is None:
                return
            
            category = self.category_combo.currentData()
            sub_category = self.sub_category_combo.currentData()
            
            if category == "all":
                spectra_list = self.current_library.get_all_spectra()
            elif sub_category == "all":
                spectra_list = self.current_library.get_spectra_by_category(category)
            else:
                spectra_list = self.current_library.get_spectra_by_sub_category(category, sub_category)
        
        for filepath, metadata in spectra_list:
            item = QListWidgetItem(metadata.name)
            item.setData(Qt.ItemDataRole.UserRole, filepath)
            self.spectrum_list.addItem(item)
    
    def _on_category_changed(self):
        """类别切换处理"""
        self._update_sub_categories()
        self._update_list()
    
    def _on_sub_category_changed(self):
        """子类别切换处理"""
        self._update_list()
    
    def _update_sub_categories(self):
        """更新子类别下拉框"""
        self.sub_category_combo.clear()
        self.sub_category_combo.addItem("全部子类别", "all")
        
        category = self.category_combo.currentData()
        if category == "all" or not self.current_library:
            return
        
        sub_cats = self.current_library.get_sub_categories(category)
        for sub_cat in sub_cats:
            display_name = USGSSpectralLibrary.get_sub_category_display_name(sub_cat)
            self.sub_category_combo.addItem(display_name, sub_cat)
    
    def _on_search(self):
        """搜索处理"""
        query = self.search_input.text().strip()
        
        if not query or not self.current_library:
            self._update_list()
            return
        
        results = self.current_library.search(query)
        self._update_list(results)
    
    def _on_spectrum_double_clicked(self, item: QListWidgetItem):
        """光谱双击处理"""
        filepath = item.data(Qt.ItemDataRole.UserRole)
        self._load_and_display(filepath)
    
    def _load_and_display(self, filepath: str):
        """加载并显示光谱"""
        if not self.current_library:
            return
        
        spectrum = self.current_library.load_spectrum(filepath)
        
        if spectrum:
            self.selected_spectrum = spectrum
            self._update_info(spectrum)
            self.plot_widget.plot_spectrum(spectrum.wavelengths, spectrum.intensities, spectrum.metadata.name)
    
    def _update_info(self, spectrum: USGSSpectrumData):
        """更新光谱信息"""
        self.info_table.setRowCount(0)
        
        info_rows = [
            ("名称", spectrum.metadata.name),
            ("类别", spectrum.metadata.category),
            ("子类别", spectrum.metadata.sub_category),
            ("记录ID", spectrum.metadata.record_id),
            ("波长范围", f"{spectrum.wavelengths[0]:.3f} - {spectrum.wavelengths[-1]:.3f} nm"),
            ("数据点数", str(len(spectrum.wavelengths))),
        ]
        
        for i, (key, value) in enumerate(info_rows):
            self.info_table.insertRow(i)
            self.info_table.setItem(i, 0, QTableWidgetItem(key))
            self.info_table.setItem(i, 1, QTableWidgetItem(value))
    
    def _on_spectrum_selected(self):
        """光谱选中处理"""
        selected_items = self.spectrum_list.selectedItems()
        
        if not selected_items:
            return
        
        spectra_to_plot = []
        
        for item in selected_items:
            filepath = item.data(Qt.ItemDataRole.UserRole)
            spectrum = self.current_library.load_spectrum(filepath)
            
            if spectrum:
                self.selected_spectrum = spectrum
                self._update_info(spectrum)
                spectra_to_plot.append((
                    spectrum.wavelengths,
                    spectrum.intensities,
                    spectrum.metadata.name
                ))
        
        if not spectra_to_plot:
            return
        
        if len(spectra_to_plot) == 1:
            wl, intensity, name = spectra_to_plot[0]
            self.plot_widget.plot_spectrum(wl, intensity, title=name)
        else:
            self.plot_widget.plot_multiple_spectra(spectra_to_plot, title=f"{len(spectra_to_plot)} Spectra")
    
    def _on_plot_selected(self):
        """绘制选中的多条光谱"""
        selected_items = self.spectrum_list.selectedItems()
        
        if not selected_items:
            return
        
        spectra_to_plot = []
        
        for item in selected_items:
            filepath = item.data(Qt.ItemDataRole.UserRole)
            spectrum = self.current_library.load_spectrum(filepath)
            
            if spectrum:
                spectra_to_plot.append((
                    spectrum.wavelengths,
                    spectrum.intensities,
                    spectrum.metadata.name
                ))
        
        if not spectra_to_plot:
            return
        
        if len(spectra_to_plot) == 1:
            wl, intensity, name = spectra_to_plot[0]
            self.plot_widget.plot_spectrum(wl, intensity, title=name)
        else:
            self.plot_widget.plot_multiple_spectra(spectra_to_plot, title=f"{len(spectra_to_plot)} Spectra")
    
    def _on_add_compare(self):
        """添加到对比"""
        if self.selected_spectrum:
            self.compare_spectra.append(self.selected_spectrum)
            self.plot_widget.add_spectrum(
                self.selected_spectrum.wavelengths, 
                self.selected_spectrum.intensities, 
                self.selected_spectrum.metadata.name
            )
    
    def _on_clear_compare(self):
        """清空对比"""
        self.compare_spectra.clear()
        self.plot_widget.clear()
        
        if self.selected_spectrum:
            self.plot_widget.plot_spectrum(
                self.selected_spectrum.wavelengths, 
                self.selected_spectrum.intensities, 
                self.selected_spectrum.metadata.name
            )
    
    def get_selected_spectrum(self) -> Optional[USGSSpectrumData]:
        """获取当前选中的光谱"""
        return self.selected_spectrum
    
    def get_compare_spectra(self) -> List[USGSSpectrumData]:
        """获取对比光谱列表"""
        return self.compare_spectra
    
    def load_library(self, library_path: str):
        """
        加载指定路径的光谱库
        
        Args:
            library_path: 光谱库目录路径
        """
        if Path(library_path).exists():
            self.current_library = USGSSpectralLibrary(library_path)
            self._update_list()
    
    def refresh_text(self):
        """刷新界面文本"""
        pass