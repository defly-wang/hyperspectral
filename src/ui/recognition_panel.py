"""
识别面板

提供模型加载、文件选择、光谱识别功能，支持批量识别并显示结果

主要功能:
    - 加载预训练模型(.pkl文件)
    - 选择待识别文件(.isf, .xlsx, .xls)
    - 批量识别光谱并显示分类结果和置信度
    - 显示识别结果摘要

信号:
    recognition_completed: 识别完成时发射，参数为识别结果字典

用法:
    panel = RecognitionPanel()
    panel.load_model_from_path("model.pkl")
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QFileDialog, QTextEdit,
                             QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
import os
import numpy as np
from ..core.i18n import t


class RecognitionPanel(QWidget):
    """
    识别面板widget
    
    提供光谱分类识别功能界面
    """
    
    recognition_completed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """
        初始化识别面板
        
        Args:
            parent: 父widget
        """
        super().__init__(parent)
        
        self.classifier = None
        self._init_ui()
    
    def _init_ui(self):
        """构建UI布局"""
        main_layout = QVBoxLayout(self)
        
        # 模型选择组
        self.model_group = QGroupBox(t("model"))
        model_layout = QVBoxLayout()
        
        model_path_layout = QHBoxLayout()
        self.model_path_label = QLabel("No model loaded")
        self.model_path_label.setWordWrap(True)
        model_path_layout.addWidget(self.model_path_label)
        
        self.load_model_btn = QPushButton(t("load_model_btn"))
        self.load_model_btn.clicked.connect(self._load_model)
        model_path_layout.addWidget(self.load_model_btn)
        
        model_layout.addLayout(model_path_layout)
        
        self.model_info_label = QLabel("")
        self.model_info_label.setWordWrap(True)
        self.model_info_label.setStyleSheet("color: gray;")
        model_layout.addWidget(self.model_info_label)
        
        self.model_group.setLayout(model_layout)
        
        # 文件选择组
        self.file_group = QGroupBox(t("recognition_files"))
        file_layout = QVBoxLayout()
        
        file_btn_layout = QHBoxLayout()
        self.select_files_btn = QPushButton(t("select_files"))
        self.select_files_btn.clicked.connect(self._select_files)
        self.select_files_btn.setEnabled(False)
        file_btn_layout.addWidget(self.select_files_btn)
        
        self.clear_files_btn = QPushButton(t("clear"))
        self.clear_files_btn.clicked.connect(self._clear_files)
        self.clear_files_btn.setEnabled(False)
        file_btn_layout.addWidget(self.clear_files_btn)
        
        file_btn_layout.addStretch()
        file_layout.addLayout(file_btn_layout)
        
        self.file_table = QTableWidget()
        self.file_table.setMaximumHeight(150)
        self.file_table.setColumnCount(3)
        self.file_table.setHorizontalHeaderLabels([t("filename"), t("recognition_result"), t("confidence")])
        self.file_table.setColumnWidth(0, 250)
        self.file_table.horizontalHeader().setStretchLastSection(True)
        self.file_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.file_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        file_layout.addWidget(self.file_table)
        
        self.file_group.setLayout(file_layout)
        
        # 识别按钮
        self.recognize_btn = QPushButton(t("start_recognition"))
        self.recognize_btn.clicked.connect(self._start_recognition)
        self.recognize_btn.setEnabled(False)
        
        # 结果显示组
        self.result_group = QGroupBox(t("recognition_results"))
        result_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)
        
        self.result_group.setLayout(result_layout)
        
        main_layout.addWidget(self.model_group)
        main_layout.addWidget(self.file_group)
        main_layout.addWidget(self.recognize_btn)
        main_layout.addWidget(self.result_group)
        main_layout.addStretch()
    
    def _load_model(self):
        """
        加载模型文件
        
        弹出文件对话框选择.pkl模型文件，加载并显示模型信息
        """
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Model File", "", 
            "Pickle Files (*.pkl)"
        )
        
        if filepath:
            try:
                from ..core.model_trainer import SpectrumClassifier
                
                self.classifier = SpectrumClassifier()
                self.classifier.load(filepath)
                
                self.model_path_label.setText(f"Model: {os.path.basename(filepath)}")
                class_names = self.classifier.get_class_names()
                self.model_info_label.setText(
                    f"Classes: {', '.join(class_names)}\n"
                    f"Model type: {type(self.classifier.model).__name__}"
                )
                
                self.select_files_btn.setEnabled(True)
                self.result_text.append(f"Model loaded successfully: {os.path.basename(filepath)}")
                self.result_text.append(f"Classes: {', '.join(class_names)}\n")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load model:\n{str(e)}")
    
    def _select_files(self):
        """
        选择待识别文件
        
        弹出文件对话框选择光谱文件(.isf, .xlsx, .xls, .txt)
        """
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Recognize", "",
            "Spectrum Files (*.isf *.xlsx *.xls *.txt);;All Files (*)"
        )
        
        if files:
            self.file_table.setRowCount(0)
            for filepath in files:
                row = self.file_table.rowCount()
                self.file_table.insertRow(row)
                self.file_table.setItem(row, 0, QTableWidgetItem(os.path.basename(filepath)))
                self.file_table.setItem(row, 1, QTableWidgetItem(""))
                self.file_table.setItem(row, 2, QTableWidgetItem(""))
            self.file_paths = files
            self.clear_files_btn.setEnabled(True)
            self.recognize_btn.setEnabled(True)
            self.result_text.append(f"Selected {len(files)} files for recognition\n")
    
    def _clear_files(self):
        """清空已选择的文件列表"""
        self.file_table.setRowCount(0)
        self.clear_files_btn.setEnabled(False)
        self.recognize_btn.setEnabled(False)
    
    def _start_recognition(self):
        """
        开始识别
        
        加载所有选中文件的光谱数据，使用模型进行分类识别，
        并显示结果
        """
        if self.classifier is None or not hasattr(self, 'file_paths'):
            return
        
        self.result_text.append("Starting recognition...\n")
        self.recognize_btn.setEnabled(False)
        
        try:
            from ..core.isf_reader import parse_isf_file
            from ..core.xlsx_reader import parse_xlsx_file
            
            results = []
            
            for filepath in self.file_paths:
                try:
                    ext = os.path.splitext(filepath)[1].lower()
                    
                    if ext in ('.xlsx', '.xls'):
                        data = parse_xlsx_file(filepath)
                    elif ext == '.txt':
                        from ..core.usgs_reader import USGSSpectralLibrary, get_wavelengths_from_file
                        lib_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(filepath))), 'spectral_database', 'usgs', 'ASCIIdata_splib07a')
                        if os.path.exists(lib_path):
                            lib = USGSSpectralLibrary(lib_path)
                            spectrum = lib.load_spectrum(filepath)
                            if spectrum:
                                data = type('Data', (), {
                                    'wavelengths': spectrum.wavelengths,
                                    'intensities': spectrum.intensities
                                })()
                            else:
                                raise ValueError("Failed to load USGS spectrum")
                        else:
                            wavelengths_usgs = get_wavelengths_from_file(filepath)
                            if wavelengths_usgs is None:
                                raise ValueError("Cannot find wavelengths file")
                            intensities_usgs = []
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                for line in f:
                                    line = line.strip()
                                    if line and not line.startswith('splib07a'):
                                        try:
                                            intensities_usgs.append(float(line))
                                        except ValueError:
                                            continue
                            data = type('Data', (), {
                                'wavelengths': wavelengths_usgs,
                                'intensities': np.array(intensities_usgs)
                            })()
                    else:
                        data = parse_isf_file(filepath)
                    
                    mask = data.wavelengths >= 350
                    wavelengths = data.wavelengths[mask]
                    intensities = data.intensities[mask]
                    
                    features = self.classifier._extract_features(wavelengths, intensities)
                    features = features.reshape(1, -1)
                    
                    prediction = self.classifier.predict(features)[0]
                    class_names = self.classifier.get_class_names()
                    predicted_class = class_names[prediction]
                    
                    proba = self.classifier.predict_proba(features)
                    
                    results.append({
                        'file': os.path.basename(filepath),
                        'class': predicted_class,
                        'confidence': proba[0][prediction] if proba is not None else None
                    })
                    
                except Exception as e:
                    results.append({
                        'file': os.path.basename(filepath),
                        'class': f"Error: {str(e)}",
                        'confidence': None
                    })
            
            # 显示结果
            self.result_text.append("=" * 50)
            self.result_text.append("Recognition Results:")
            self.result_text.append("=" * 50)
            
            for result in results:
                filename = result['file']
                predicted = result['class']
                confidence = result['confidence']
                
                # 更新表格
                for row in range(self.file_table.rowCount()):
                    item = self.file_table.item(row, 0)
                    if item and item.text() == filename:
                        self.file_table.setItem(row, 1, QTableWidgetItem(predicted))
                        if confidence is not None:
                            self.file_table.setItem(row, 2, QTableWidgetItem(f"{confidence*100:.2f}%"))
                        else:
                            self.file_table.setItem(row, 2, QTableWidgetItem("-"))
                        break
                
                # 更新结果文本
                if confidence is not None:
                    self.result_text.append(
                        f"{filename}: {predicted} ({confidence*100:.2f}%)"
                    )
                else:
                    self.result_text.append(f"{filename}: {predicted}")
            
            self.result_text.append("\n")
            self.recognize_btn.setEnabled(True)
            
            self.recognition_completed.emit({'results': results})
            
        except Exception as e:
            self.result_text.append(f"Error during recognition: {str(e)}\n")
            self.recognize_btn.setEnabled(True)
            import traceback
            traceback.print_exc()
    
    def load_model_from_path(self, filepath: str):
        """
        从路径加载模型
        
        Args:
            filepath: 模型文件路径
        """
        if os.path.exists(filepath):
            try:
                from ..core.model_trainer import SpectrumClassifier
                
                self.classifier = SpectrumClassifier()
                self.classifier.load(filepath)
                
                self.model_path_label.setText(f"Model: {os.path.basename(filepath)}")
                class_names = self.classifier.get_class_names()
                self.model_info_label.setText(
                    f"Classes: {', '.join(class_names)}\n"
                    f"Model type: {type(self.classifier.model).__name__}"
                )
                
                self.select_files_btn.setEnabled(True)
                self.result_text.append(f"Model loaded: {os.path.basename(filepath)}\n")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load model:\n{str(e)}")
    
    def refresh_text(self):
        """
        刷新界面文本（用于语言切换）
        """
        self.model_group.setTitle(t("model"))
        self.file_group.setTitle(t("recognition_files"))
        self.result_group.setTitle(t("recognition_results"))
        self.load_model_btn.setText(t("load_model_btn"))
        self.select_files_btn.setText(t("select_files"))
        self.clear_files_btn.setText(t("clear"))
        self.recognize_btn.setText(t("start_recognition"))
