from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal
import os

from .file_browser import FileBrowserWidget
from .spectrum_plot import SpectrumPlotWidget
from .image_view import ImageViewWidget
from .preprocessing_panel import PreprocessingPanel
from ..core.i18n import t


class PreviewPanel(QWidget):
    files_loaded = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.loaded_data = {}
        self._init_ui()
    
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
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
        
        main_layout.addWidget(splitter)
        
        self.file_browser.folder_selected.connect(self._on_folder_selected)
        self.file_browser.files_selected.connect(self._on_files_selected)
        self.preprocessing_panel.preprocessing_changed.connect(self._apply_preprocessing)
    
    def _on_folder_selected(self, folder: str):
        isf_files = [f for f in os.listdir(folder) if f.lower().endswith('.isf')]
        xlsx_files = [f for f in os.listdir(folder) if f.lower().endswith(('.xlsx', '.xls'))]
        all_files = isf_files + xlsx_files
        files = [os.path.join(folder, f) for f in all_files]
        self.file_browser.set_files(files)
        self.loaded_data = {}
    
    def _on_files_selected(self, filepaths: list):
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
            if len(spectra_to_plot) == 1:
                wl, intensity, name = spectra_to_plot[0]
                self.image_view.show_fake_hsi_image(wl, intensity, title=name)
            else:
                self.image_view.show_multiple_images(spectra_to_plot)
    
    def refresh_text(self):
        self.preprocessing_panel.refresh_text()
    
    def clear(self):
        self.spectrum_plot.clear()
        self.image_view.clear()
        self.loaded_data = {}
