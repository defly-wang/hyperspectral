from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QGroupBox, QCheckBox,
                             QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal


class PreprocessingPanel(QWidget):
    preprocessing_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        
        smoothing_group = QGroupBox("Smoothing")
        smoothing_layout = QVBoxLayout()
        
        self.smooth_combo = QComboBox()
        self.smooth_combo.addItems(["None", "Savitzky-Golay", "Moving Average"])
        
        smooth_params_layout = QHBoxLayout()
        smooth_params_layout.addWidget(QLabel("Window:"))
        self.smooth_window = QSpinBox()
        self.smooth_window.setRange(3, 51)
        self.smooth_window.setValue(11)
        self.smooth_window.setSingleStep(2)
        smooth_params_layout.addWidget(self.smooth_window)
        
        smooth_params_layout.addWidget(QLabel("Order:"))
        self.smooth_order = QSpinBox()
        self.smooth_order.setRange(0, 5)
        self.smooth_order.setValue(3)
        smooth_params_layout.addWidget(self.smooth_order)
        smooth_params_layout.addStretch()
        
        smoothing_layout.addWidget(self.smooth_combo)
        smoothing_layout.addLayout(smooth_params_layout)
        smoothing_group.setLayout(smoothing_layout)
        
        normalization_group = QGroupBox("Normalization")
        norm_layout = QVBoxLayout()
        
        self.norm_combo = QComboBox()
        self.norm_combo.addItems(["None", "Min-Max", "Z-Score"])
        norm_layout.addWidget(self.norm_combo)
        
        normalization_group.setLayout(norm_layout)
        
        baseline_group = QGroupBox("Baseline Correction")
        baseline_layout = QVBoxLayout()
        
        self.baseline_combo = QComboBox()
        self.baseline_combo.addItems(["None", "AirPLS", "Subtract Baseline"])
        baseline_layout.addWidget(self.baseline_combo)
        
        baseline_group.setLayout(baseline_layout)
        
        options_group = QGroupBox("Display Options")
        options_layout = QVBoxLayout()
        
        self.show_original_check = QCheckBox("Show Original Spectrum")
        self.show_original_check.setChecked(False)
        options_layout.addWidget(self.show_original_check)
        
        options_group.setLayout(options_layout)
        
        self.apply_btn = QPushButton("Apply Preprocessing")
        
        main_layout.addWidget(smoothing_group)
        main_layout.addWidget(normalization_group)
        main_layout.addWidget(baseline_group)
        main_layout.addWidget(options_group)
        main_layout.addWidget(self.apply_btn)
        main_layout.addStretch()
        
        self.smooth_combo.currentTextChanged.connect(self._on_params_changed)
        self.smooth_window.valueChanged.connect(self._on_params_changed)
        self.smooth_order.valueChanged.connect(self._on_params_changed)
        self.norm_combo.currentTextChanged.connect(self._on_params_changed)
        self.baseline_combo.currentTextChanged.connect(self._on_params_changed)
        self.apply_btn.clicked.connect(self.preprocessing_changed.emit)
        self.show_original_check.stateChanged.connect(self._on_params_changed)
        
        self._update_params_visibility()

    def _on_params_changed(self):
        self._update_params_visibility()
        self.preprocessing_changed.emit()

    def _update_params_visibility(self):
        smooth_type = self.smooth_combo.currentText()
        self.smooth_window.setEnabled(smooth_type != "None")
        self.smooth_order.setEnabled(smooth_type == "Savitzky-Golay")

    def get_smoothing_method(self) -> str:
        text = self.smooth_combo.currentText()
        if text == "Savitzky-Golay":
            return "Savitzky-Golay"
        elif text == "Moving Average":
            return "Moving Average"
        return "None"

    def get_smoothing_params(self) -> dict:
        return {
            'window': self.smooth_window.value(),
            'order': self.smooth_order.value()
        }

    def get_normalization_method(self) -> str:
        return self.norm_combo.currentText()

    def get_baseline_method(self) -> str:
        return self.baseline_combo.currentText()

    def show_original(self) -> bool:
        return self.show_original_check.isChecked()
