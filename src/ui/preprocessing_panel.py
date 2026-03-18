"""
预处理面板

提供光谱数据预处理功能，包括平滑（Savitzky-Golay、移动平均）、
归一化（Min-Max、Z-Score）、基线校正

主要功能:
    - 平滑处理：Savitzky-Golay滤波、移动平均
    - 归一化处理：Min-Max归一化、Z-Score标准化
    - 基线校正：基线减除
    - 参数实时调整和预览

信号:
    preprocessing_changed: 预处理参数变化时发射

用法:
    panel = PreprocessingPanel()
    panel.preprocessing_changed.connect(handle_preprocessing)
    method = panel.get_smoothing_method()
    params = panel.get_smoothing_params()
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QGroupBox, QCheckBox,
                             QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal
from ..core.i18n import t


class PreprocessingPanel(QWidget):
    """
    预处理面板widget
    
    提供光谱数据预处理参数设置界面
    """
    
    preprocessing_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        初始化预处理面板
        
        Args:
            parent: 父widget
        """
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        
        self.smoothing_group = QGroupBox(t("smoothing"))
        smoothing_layout = QVBoxLayout()
        
        self.smooth_combo = QComboBox()
        self.smooth_combo.addItems([t("none"), t("savitzky_golay"), t("moving_average")])
        
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
        self.smoothing_group.setLayout(smoothing_layout)
        
        self.normalization_group = QGroupBox(t("normalization"))
        norm_layout = QVBoxLayout()
        
        self.norm_combo = QComboBox()
        self.norm_combo.addItems([t("none"), t("min_max"), t("z_score")])
        norm_layout.addWidget(self.norm_combo)
        
        self.normalization_group.setLayout(norm_layout)
        
        self.baseline_group = QGroupBox(t("baseline_correction"))
        baseline_layout = QVBoxLayout()
        
        self.baseline_combo = QComboBox()
        self.baseline_combo.addItems([t("none"), t("airpls"), t("subtract_baseline")])
        baseline_layout.addWidget(self.baseline_combo)
        
        self.baseline_group.setLayout(baseline_layout)
        
        self.options_group = QGroupBox("Display Options")
        options_layout = QVBoxLayout()
        
        self.show_original_check = QCheckBox("Show Original Spectrum")
        self.show_original_check.setChecked(False)
        options_layout.addWidget(self.show_original_check)
        
        self.options_group.setLayout(options_layout)
        
        self.apply_btn = QPushButton("Apply Preprocessing")
        
        main_layout.addWidget(self.smoothing_group)
        main_layout.addWidget(self.normalization_group)
        main_layout.addWidget(self.baseline_group)
        main_layout.addWidget(self.options_group)
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
        """
        预处理参数变化处理
        
        更新参数控件可见性并发射预处理变化信号
        """
        self._update_params_visibility()
        self.preprocessing_changed.emit()

    def _update_params_visibility(self):
        """
        根据选择的平滑方法更新参数控件可见性
        
        当选择Savitzky-Golay时显示窗口和阶数参数，
        选择移动平均时只显示窗口参数
        """
        smooth_type = self.smooth_combo.currentText()
        self.smooth_window.setEnabled(smooth_type != t("none"))
        self.smooth_order.setEnabled(smooth_type == t("savitzky_golay"))

    def get_smoothing_method(self) -> str:
        """
        获取平滑处理方法
        
        Returns:
            平滑方法名称: "Savitzky-Golay", "Moving Average" 或 "None"
        """
        text = self.smooth_combo.currentText()
        if text == t("savitzky_golay"):
            return "Savitzky-Golay"
        elif text == t("moving_average"):
            return "Moving Average"
        return "None"

    def get_smoothing_params(self) -> dict:
        """
        获取平滑处理参数
        
        Returns:
            包含窗口大小和阶数的字典
        """
        return {
            'window': self.smooth_window.value(),
            'order': self.smooth_order.value()
        }

    def get_normalization_method(self) -> str:
        """
        获取归一化方法
        
        Returns:
            归一化方法名称
        """
        return self.norm_combo.currentText()

    def get_baseline_method(self) -> str:
        """
        获取基线校正方法
        
        Returns:
            基线校正方法名称
        """
        return self.baseline_combo.currentText()

    def show_original(self) -> bool:
        """
        是否显示原始光谱
        
        Returns:
            True表示显示原始光谱，False表示不显示
        """
        return self.show_original_check.isChecked()
    
    def refresh_text(self):
        """
        刷新界面文本（用于语言切换）
        """
        self.smoothing_group.setTitle(t("smoothing"))
        self.normalization_group.setTitle(t("normalization"))
        self.baseline_group.setTitle(t("baseline_correction"))
