from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QFileDialog, QTextEdit,
                             QListWidget, QComboBox, QDoubleSpinBox, QSpinBox, QCheckBox, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal
import os
import shutil
import random
from typing import List, Tuple
from ..core.i18n import t


class DataSplitPanel(QWidget):
    split_completed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.source_data_dir = ""
        self.output_dir = ""
        self._init_ui()
    
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        
        source_group = QGroupBox(t("data_source"))
        source_layout = QVBoxLayout()
        
        source_path_layout = QHBoxLayout()
        self.source_path_label = QLabel(t("no_folder_selected"))
        self.source_path_label.setWordWrap(True)
        source_path_layout.addWidget(self.source_path_label)
        
        self.select_source_btn = QPushButton(t("select_folder"))
        self.select_source_btn.clicked.connect(self._select_source_folder)
        source_path_layout.addWidget(self.select_source_btn)
        
        source_layout.addLayout(source_path_layout)
        
        source_group.setLayout(source_layout)
        
        output_group = QGroupBox(t("output_directory"))
        output_layout = QVBoxLayout()
        
        output_path_layout = QHBoxLayout()
        self.output_path_label = QLabel(t("no_folder_selected"))
        self.output_path_label.setWordWrap(True)
        output_path_layout.addWidget(self.output_path_label)
        
        self.select_output_btn = QPushButton(t("select_folder"))
        self.select_output_btn.clicked.connect(self._select_output_folder)
        output_path_layout.addWidget(self.select_output_btn)
        
        output_layout.addLayout(output_path_layout)
        
        output_group.setLayout(output_layout)
        
        settings_group = QGroupBox(t("split_settings"))
        settings_layout = QVBoxLayout()
        
        split_type_layout = QHBoxLayout()
        split_type_layout.addWidget(QLabel(t("split_type") + ":"))
        self.split_type_combo = QComboBox()
        self.split_type_combo.addItems([t("train_val_test"), t("train_test")])
        split_type_layout.addWidget(self.split_type_combo)
        split_type_layout.addStretch()
        settings_layout.addLayout(split_type_layout)
        
        ratio_layout = QHBoxLayout()
        ratio_layout.addWidget(QLabel(t("train_ratio") + ":"))
        self.train_ratio_spin = QDoubleSpinBox()
        self.train_ratio_spin.setRange(0.5, 0.9)
        self.train_ratio_spin.setValue(0.7)
        self.train_ratio_spin.setSingleStep(0.1)
        self.train_ratio_spin.setSuffix(" %")
        ratio_layout.addWidget(self.train_ratio_spin)
        ratio_layout.addStretch()
        settings_layout.addLayout(ratio_layout)
        
        val_ratio_layout = QHBoxLayout()
        val_ratio_layout.addWidget(QLabel(t("val_ratio") + ":"))
        self.val_ratio_spin = QDoubleSpinBox()
        self.val_ratio_spin.setRange(0.05, 0.3)
        self.val_ratio_spin.setValue(0.15)
        self.val_ratio_spin.setSingleStep(0.05)
        self.val_ratio_spin.setSuffix(" %")
        val_ratio_layout.addWidget(self.val_ratio_spin)
        val_ratio_layout.addStretch()
        settings_layout.addLayout(val_ratio_layout)
        
        test_ratio_layout = QHBoxLayout()
        test_ratio_layout.addWidget(QLabel(t("test_ratio") + ":"))
        self.test_ratio_spin = QDoubleSpinBox()
        self.test_ratio_spin.setRange(0.1, 0.5)
        self.test_ratio_spin.setValue(0.15)
        self.test_ratio_spin.setSingleStep(0.05)
        self.test_ratio_spin.setSuffix(" %")
        test_ratio_layout.addWidget(self.test_ratio_spin)
        test_ratio_layout.addStretch()
        settings_layout.addLayout(test_ratio_layout)
        
        shuffle_layout = QHBoxLayout()
        self.shuffle_check = QCheckBox(t("shuffle_data"))
        self.shuffle_check.setChecked(True)
        shuffle_layout.addWidget(self.shuffle_check)
        shuffle_layout.addStretch()
        settings_layout.addLayout(shuffle_layout)
        
        seed_layout = QHBoxLayout()
        seed_layout.addWidget(QLabel(t("random_seed") + ":"))
        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(0, 99999)
        self.seed_spin.setValue(42)
        seed_layout.addWidget(self.seed_spin)
        seed_layout.addStretch()
        settings_layout.addLayout(seed_layout)
        
        settings_group.setLayout(settings_layout)
        
        self.split_btn = QPushButton(t("start_split"))
        self.split_btn.clicked.connect(self._start_split)
        self.split_btn.setEnabled(False)
        
        result_group = QGroupBox(t("split_results"))
        result_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)
        
        result_group.setLayout(result_layout)
        
        main_layout.addWidget(source_group)
        main_layout.addWidget(output_group)
        main_layout.addWidget(settings_group)
        main_layout.addWidget(self.split_btn)
        main_layout.addWidget(result_group, 1)
    
    def _select_source_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, t("select_source_folder"), 
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        )
        
        if folder:
            self.source_data_dir = folder
            self.source_path_label.setText(f"Source: {folder}")
            self._check_ready()
    
    def _select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, t("select_output_folder"), 
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        )
        
        if folder:
            self.output_dir = folder
            self.output_path_label.setText(f"Output: {folder}")
            self._check_ready()
    
    def _check_ready(self):
        self.split_btn.setEnabled(
            bool(self.source_data_dir and self.output_dir)
        )
    
    def _start_split(self):
        if not self.source_data_dir or not self.output_dir:
            return
        
        self.split_btn.setEnabled(False)
        self.result_text.clear()
        
        try:
            split_type = self.split_type_combo.currentText()
            train_ratio = self.train_ratio_spin.value() / 100
            val_ratio = self.val_ratio_spin.value() / 100
            test_ratio = self.test_ratio_spin.value() / 100
            shuffle = self.shuffle_check.isChecked()
            seed = self.seed_spin.value()
            
            if shuffle:
                random.seed(seed)
            
            categories = [d for d in os.listdir(self.source_data_dir) 
                        if os.path.isdir(os.path.join(self.source_data_dir, d))]
            
            if not categories:
                self.result_text.append(t("no_category_found"))
                self.split_btn.setEnabled(True)
                return
            
            results = {
                'categories': {},
                'train_count': 0,
                'val_count': 0,
                'test_count': 0,
                'total_count': 0
            }
            
            if split_type == t("train_val_test"):
                self._split_three_way(categories, train_ratio, val_ratio, test_ratio, shuffle, results)
            else:
                self._split_two_way(categories, train_ratio, test_ratio, shuffle, results)
            
            self.result_text.append("\n" + "="*50)
            self.result_text.append(t("split_complete"))
            self.result_text.append(f"Train: {results['train_count']}")
            self.result_text.append(f"Val: {results['val_count']}")
            self.result_text.append(f"Test: {results['test_count']}")
            self.result_text.append(f"Total: {results['total_count']}")
            
            self.split_btn.setEnabled(True)
            self.split_completed.emit(results)
            
        except Exception as e:
            self.result_text.append(f"Error: {str(e)}")
            self.split_btn.setEnabled(True)
            import traceback
            traceback.print_exc()
    
    def _split_three_way(self, categories, train_ratio, val_ratio, test_ratio, shuffle, results):
        for category in categories:
            category_dir = os.path.join(self.source_data_dir, category)
            files = [f for f in os.listdir(category_dir) 
                    if f.lower().endswith(('.isf', '.xlsx', '.xls'))]
            
            if shuffle:
                random.shuffle(files)
            
            n = len(files)
            train_end = int(n * train_ratio)
            val_end = train_end + int(n * val_ratio)
            
            train_files = files[:train_end]
            val_files = files[train_end:val_end]
            test_files = files[val_end:]
            
            results['categories'][category] = {
                'train': len(train_files),
                'val': len(val_files),
                'test': len(test_files)
            }
            results['train_count'] += len(train_files)
            results['val_count'] += len(val_files)
            results['test_count'] += len(test_files)
            results['total_count'] += n
            
            self._create_category_folders(category, train_files, val_files, test_files)
            
            self.result_text.append(f"\n{category}:")
            self.result_text.append(f"  Train: {len(train_files)}, Val: {len(val_files)}, Test: {len(test_files)}")
    
    def _split_two_way(self, categories, train_ratio, test_ratio, shuffle, results):
        for category in categories:
            category_dir = os.path.join(self.source_data_dir, category)
            files = [f for f in os.listdir(category_dir) 
                    if f.lower().endswith(('.isf', '.xlsx', '.xls'))]
            
            if shuffle:
                random.shuffle(files)
            
            n = len(files)
            train_end = int(n * train_ratio)
            
            train_files = files[:train_end]
            test_files = files[train_end:]
            
            results['categories'][category] = {
                'train': len(train_files),
                'test': len(test_files)
            }
            results['train_count'] += len(train_files)
            results['test_count'] += len(test_files)
            results['total_count'] += n
            
            self._create_category_folders_two(category, train_files, test_files)
            
            self.result_text.append(f"\n{category}:")
            self.result_text.append(f"  Train: {len(train_files)}, Test: {len(test_files)}")
    
    def _create_category_folders(self, category, train_files, val_files, test_files):
        train_dir = os.path.join(self.output_dir, "train", category)
        val_dir = os.path.join(self.output_dir, "val", category)
        test_dir = os.path.join(self.output_dir, "test", category)
        
        os.makedirs(train_dir, exist_ok=True)
        os.makedirs(val_dir, exist_ok=True)
        os.makedirs(test_dir, exist_ok=True)
        
        source_dir = os.path.join(self.source_data_dir, category)
        
        for f in train_files:
            shutil.copy2(os.path.join(source_dir, f), os.path.join(train_dir, f))
        
        for f in val_files:
            shutil.copy2(os.path.join(source_dir, f), os.path.join(val_dir, f))
        
        for f in test_files:
            shutil.copy2(os.path.join(source_dir, f), os.path.join(test_dir, f))
    
    def _create_category_folders_two(self, category, train_files, test_files):
        train_dir = os.path.join(self.output_dir, "train", category)
        test_dir = os.path.join(self.output_dir, "test", category)
        
        os.makedirs(train_dir, exist_ok=True)
        os.makedirs(test_dir, exist_ok=True)
        
        source_dir = os.path.join(self.source_data_dir, category)
        
        for f in train_files:
            shutil.copy2(os.path.join(source_dir, f), os.path.join(train_dir, f))
        
        for f in test_files:
            shutil.copy2(os.path.join(source_dir, f), os.path.join(test_dir, f))
    
    def refresh_text(self):
        pass
