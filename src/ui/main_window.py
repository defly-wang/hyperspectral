from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QSplitter, QTabWidget, QStatusBar, QMenuBar, 
                             QMenu, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import os

from .file_browser import FileBrowserWidget
from .spectrum_plot import SpectrumPlotWidget
from .image_view import ImageViewWidget
from .preprocessing_panel import PreprocessingPanel
from .training_panel import TrainingPanel
from .recognition_panel import RecognitionPanel
from .data_cleaning_panel import DataCleaningPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("高光谱数据管理系统 - HyperspectralDMS")
        self.setMinimumSize(1200, 800)
        
        self.current_data = None
        self.original_intensities = None
        self.loaded_files = []
        
        self._create_menu_bar()
        self._create_ui()
        self._connect_signals()
        
        self.statusBar().showMessage("Ready")

    def _create_menu_bar(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open Folder...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_folder)
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        view_menu = menubar.addMenu("View")
        
        reset_action = QAction("Reset View", self)
        reset_action.triggered.connect(self._reset_view)
        
        view_menu.addAction(reset_action)
        
        model_menu = menubar.addMenu("Model")
        
        train_action = QAction("Train Model...", self)
        train_action.setShortcut("Ctrl+T")
        train_action.triggered.connect(self._show_training_panel)
        
        load_model_action = QAction("Load Model...", self)
        load_model_action.setShortcut("Ctrl+M")
        load_model_action.triggered.connect(self._load_model)
        
        recognize_action = QAction("Recognition...", self)
        recognize_action.setShortcut("Ctrl+R")
        recognize_action.triggered.connect(self._show_recognition_panel)
        
        model_menu.addAction(train_action)
        model_menu.addAction(load_model_action)
        model_menu.addAction(recognize_action)
        
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        
        help_menu.addAction(about_action)

    def _create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        self.tab_widget = QTabWidget()
        
        preview_widget = QWidget()
        preview_layout = QHBoxLayout(preview_widget)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.file_browser = FileBrowserWidget()
        self.preprocessing_panel = PreprocessingPanel()
        
        left_layout.addWidget(self.file_browser, stretch=2)
        left_layout.addWidget(self.preprocessing_panel, stretch=1)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.spectrum_plot = SpectrumPlotWidget()
        self.image_view = ImageViewWidget()
        
        right_layout.addWidget(self.spectrum_plot, stretch=1)
        right_layout.addWidget(self.image_view, stretch=1)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        preview_layout.addWidget(splitter)
        
        self.training_panel = TrainingPanel()
        self.recognition_panel = RecognitionPanel()
        self.data_cleaning_panel = DataCleaningPanel()
        
        self.tab_widget.addTab(preview_widget, "Preview")
        self.tab_widget.addTab(self.data_cleaning_panel, "Data Cleaning")
        self.tab_widget.addTab(self.training_panel, "Model Training")
        self.tab_widget.addTab(self.recognition_panel, "Recognition")
        
        main_layout.addWidget(self.tab_widget)

    def _connect_signals(self):
        self.file_browser.folder_selected.connect(self._on_folder_selected)
        self.file_browser.files_selected.connect(self._on_files_selected)
        self.preprocessing_panel.preprocessing_changed.connect(self._apply_preprocessing)

    def _open_folder(self):
        self.file_browser._open_folder()

    def _on_folder_selected(self, folder: str):
        isf_files = [f for f in os.listdir(folder) if f.lower().endswith('.isf')]
        xlsx_files = [f for f in os.listdir(folder) if f.lower().endswith(('.xlsx', '.xls'))]
        all_files = isf_files + xlsx_files
        files = [os.path.join(folder, f) for f in all_files]
        self.file_browser.set_files(files)
        self.loaded_files = files
        self.statusBar().showMessage(f"Loaded {len(files)} files from {folder}")

    def _on_files_selected(self, filepaths: list):
        from ..core.isf_reader import parse_isf_file
        from ..core.xlsx_reader import parse_xlsx_file
        
        if not filepaths:
            return
        
        try:
            self.loaded_data = {}
            for filepath in filepaths:
                ext = os.path.splitext(filepath)[1].lower()
                if ext in ('.xlsx', '.xls'):
                    data = parse_xlsx_file(filepath)
                else:
                    data = parse_isf_file(filepath)
                self.loaded_data[filepath] = data
            
            if len(filepaths) == 1:
                filepath = filepaths[0]
                self.current_data = self.loaded_data[filepath]
                self.original_intensities = self.current_data.intensities.copy()
            
            filename = os.path.basename(filepaths[0]) if len(filepaths) == 1 else f"{len(filepaths)} files selected"
            self.statusBar().showMessage(f"Loaded: {filename}")
            
            self._apply_preprocessing()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")

    def _apply_preprocessing(self):
        if not hasattr(self, 'loaded_data') or not self.loaded_data:
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
            mask = data.wavelengths >= 400
            wavelengths = data.wavelengths[mask]
            intensities = data.intensities[mask].copy()
            
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
            
            filename = os.path.basename(filepath)
            spectra_to_plot.append((wavelengths, intensities, filename))
        
        if len(spectra_to_plot) == 1:
            wl, intensity, name = spectra_to_plot[0]
            self.spectrum_plot.plot_spectrum(wl, intensity, title=name)
        else:
            self.spectrum_plot.plot_multiple_spectra(spectra_to_plot, title=f"{len(spectra_to_plot)} Spectra")
        
        if spectra_to_plot:
            wl = spectra_to_plot[0][0]
            intensity = spectra_to_plot[0][1]
            self.image_view.show_fake_hsi_image(wl, intensity)

    def _reset_view(self):
        self.spectrum_plot.clear()
        self.image_view.clear()
        self.current_data = None
        self.original_intensities = None
        if hasattr(self, 'loaded_data'):
            self.loaded_data = {}

    def _show_training_panel(self):
        self.tab_widget.setCurrentIndex(1)

    def _show_recognition_panel(self):
        self.tab_widget.setCurrentIndex(2)
    
    def _load_model(self):
        from PyQt6.QtWidgets import QFileDialog
        import os
        
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Model File", "", 
            "Pickle Files (*.pkl)"
        )
        
        if filepath and os.path.exists(filepath):
            self.recognition_panel.load_model_from_path(filepath)
            self._show_recognition_panel()

    def _show_about(self):
        QMessageBox.about(
            self, 
            "About",
            "高光谱数据管理系统 - HyperspectralDMS\n\n"
            "高光谱数据处理与可视化工具。\n\n"
            "支持格式: iSpecField (.isf)"
        )
