from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QFileDialog, QTextEdit,
                             QListWidget, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
import os
import numpy as np
from ..core.i18n import t


class RecognitionPanel(QWidget):
    recognition_completed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.classifier = None
        self._init_ui()
    
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        
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
        
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(150)
        file_layout.addWidget(self.file_list)
        
        self.file_group.setLayout(file_layout)
        
        self.recognize_btn = QPushButton(t("start_recognition"))
        self.recognize_btn.clicked.connect(self._start_recognition)
        self.recognize_btn.setEnabled(False)
        
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
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Recognize", "",
            "Spectrum Files (*.isf *.xlsx *.xls);;All Files (*)"
        )
        
        if files:
            self.file_list.clear()
            for filepath in files:
                self.file_list.addItem(os.path.basename(filepath))
            self.file_paths = files
            self.clear_files_btn.setEnabled(True)
            self.recognize_btn.setEnabled(True)
            self.result_text.append(f"Selected {len(files)} files for recognition\n")
    
    def _clear_files(self):
        self.file_list.clear()
        self.clear_files_btn.setEnabled(False)
        self.recognize_btn.setEnabled(False)
    
    def _start_recognition(self):
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
                    else:
                        data = parse_isf_file(filepath)
                    
                    mask = data.wavelengths >= 400
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
            
            self.result_text.append("=" * 50)
            self.result_text.append("Recognition Results:")
            self.result_text.append("=" * 50)
            
            for result in results:
                filename = result['file']
                predicted = result['class']
                confidence = result['confidence']
                
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
        self.model_group.setTitle(t("model"))
        self.file_group.setTitle(t("recognition_files"))
        self.result_group.setTitle(t("recognition_results"))
        self.load_model_btn.setText(t("load_model_btn"))
        self.select_files_btn.setText(t("select_files"))
        self.clear_files_btn.setText(t("clear"))
        self.recognize_btn.setText(t("start_recognition"))
