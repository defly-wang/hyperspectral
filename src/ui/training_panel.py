from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QGroupBox, QFileDialog,
                             QTextEdit, QDoubleSpinBox, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal
import os
from ..core.i18n import t


class TrainingPanel(QWidget):
    training_completed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.classifier = None
        self._init_ui()
    
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        
        self.data_group = QGroupBox(t("training_data"))
        data_layout = QVBoxLayout()
        
        data_path_layout = QHBoxLayout()
        self.data_path_label = QLabel(t("data_directory") + ":")
        self.data_path_label.setWordWrap(True)
        data_path_layout.addWidget(self.data_path_label)
        
        self.select_data_btn = QPushButton("Select...")
        self.select_data_btn.clicked.connect(self._select_data_directory)
        data_path_layout.addWidget(self.select_data_btn)
        
        data_layout.addLayout(data_path_layout)
        
        self.data_info_label = QLabel(t("no_directory_selected"))
        self.data_info_label.setWordWrap(True)
        self.data_info_label.setStyleSheet("color: gray;")
        data_layout.addWidget(self.data_info_label)
        
        self.data_group.setLayout(data_layout)
        
        self.model_group = QGroupBox(t("model_settings"))
        model_layout = QVBoxLayout()
        
        model_type_layout = QHBoxLayout()
        model_type_layout.addWidget(QLabel(t("model_type") + ":"))
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems([t("random_forest"), t("svm"), t("gradient_boosting")])
        model_type_layout.addWidget(self.model_type_combo)
        model_type_layout.addStretch()
        model_layout.addLayout(model_type_layout)
        
        test_size_layout = QHBoxLayout()
        test_size_layout.addWidget(QLabel(t("test_size") + ":"))
        self.test_size_spin = QDoubleSpinBox()
        self.test_size_spin.setRange(0.1, 0.5)
        self.test_size_spin.setValue(0.2)
        self.test_size_spin.setSingleStep(0.05)
        self.test_size_spin.setSuffix(" (ratio)")
        test_size_layout.addWidget(self.test_size_spin)
        test_size_layout.addStretch()
        model_layout.addLayout(test_size_layout)
        
        self.model_group.setLayout(model_layout)
        
        self.train_btn = QPushButton(t("start_training"))
        self.train_btn.setEnabled(False)
        self.train_btn.clicked.connect(self._start_training)
        
        self.save_btn = QPushButton(t("save_model"))
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save_model)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        self.result_group = QGroupBox(t("results"))
        result_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)
        result_layout.addWidget(self.result_text)
        
        self.result_group.setLayout(result_layout)
        
        main_layout.addWidget(self.data_group)
        main_layout.addWidget(self.model_group)
        main_layout.addWidget(self.train_btn)
        main_layout.addWidget(self.save_btn)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.result_group)
        main_layout.addStretch()
    
    def _select_data_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Training Data Directory", 
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        )
        
        if directory:
            self.data_dir = directory
            self.data_path_label.setText(f"Data: {directory}")
            self._scan_directory(directory)
    
    def _scan_directory(self, directory):
        from ..core.model_trainer import SpectrumClassifier
        
        classifier = SpectrumClassifier()
        is_split = classifier.detect_split_dirs(directory)
        
        if is_split:
            train_dir = os.path.join(directory, 'train')
            categories = sorted([d for d in os.listdir(train_dir) 
                               if os.path.isdir(os.path.join(train_dir, d))])
            
            train_count = 0
            val_count = 0
            test_count = 0
            
            for category in categories:
                train_cat_dir = os.path.join(train_dir, category)
                if os.path.exists(train_cat_dir):
                    train_count += len([f for f in os.listdir(train_cat_dir) 
                                      if f.lower().endswith(('.xlsx', '.xls'))])
                
                val_cat_dir = os.path.join(directory, 'val', category)
                if os.path.exists(val_cat_dir):
                    val_count += len([f for f in os.listdir(val_cat_dir) 
                                    if f.lower().endswith(('.xlsx', '.xls'))])
                
                test_cat_dir = os.path.join(directory, 'test', category)
                if os.path.exists(test_cat_dir):
                    test_count += len([f for f in os.listdir(test_cat_dir) 
                                     if f.lower().endswith(('.xlsx', '.xls'))])
            
            total_files = train_count + val_count + test_count
            
            val_info = f", Val: {val_count}" if val_count > 0 else ""
            test_info = f", Test: {test_count}" if test_count > 0 else ""
            
            self.data_info_label.setText(
                f"Found {len(categories)} categories: {', '.join(categories)}\n"
                f"Total files: {total_files} (Train: {train_count}{val_info}{test_info})\n"
                f"Feature dimension: 400-2500nm (2101 points)\n"
                f"Data source: Pre-split directories"
            )
            self.is_split_data = True
            self.split_data = None
        else:
            categories = [d for d in os.listdir(directory) 
                         if os.path.isdir(os.path.join(directory, d))]
            
            if not categories:
                self.data_info_label.setText(t("no_category_found"))
                self.train_btn.setEnabled(False)
                return
            
            total_files = 0
            for category in categories:
                category_dir = os.path.join(directory, category)
                files = [f for f in os.listdir(category_dir) 
                        if f.lower().endswith(('.xlsx', '.xls'))]
                total_files += len(files)
            
            self.data_info_label.setText(
                f"Found {len(categories)} categories: {', '.join(categories)}\n"
                f"Total files: {total_files}\n"
                f"Feature dimension: 400-2500nm (2101 points)"
            )
            self.is_split_data = False
            self.split_data = None
        
        self.categories = categories
        self.train_btn.setEnabled(True)
    
    def _start_training(self):
        if not hasattr(self, 'data_dir'):
            return
        
        self.train_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        self.result_text.clear()
        
        try:
            from ..core.model_trainer import SpectrumClassifier
            
            model_type_map = {
                t("random_forest"): "rf",
                t("svm"): "svm",
                t("gradient_boosting"): "gb"
            }
            model_type = model_type_map[self.model_type_combo.currentText()]
            
            self.classifier = SpectrumClassifier()
            
            self.result_text.append("Loading data...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(5)
            
            # 定义进度回调函数
            def progress_callback(progress: int, status: str):
                # 将进度映射到 5-45% 范围
                actual_progress = 5 + int(progress * 0.4)
                self.progress_bar.setValue(actual_progress)
                self.result_text.append(status)
            
            if hasattr(self, 'is_split_data') and self.is_split_data:
                X_train, y_train, X_val, y_val, X_test, y_test = self.classifier.load_data_from_directory(
                    self.data_dir, 
                    min_wavelength=400,
                    use_split_dirs=True,
                    progress_callback=progress_callback
                )
                self.result_text.append(f"Loaded {len(y_train)} training samples")
                self.result_text.append(f"Using pre-split data (Train: {len(y_train)}, Val: {len(y_val) if y_val is not None else 0}, Test: {len(y_test) if y_test is not None else 0})")
            else:
                X, y, X_val, y_val, X_test, y_test = self.classifier.load_data_from_directory(
                    self.data_dir, 
                    min_wavelength=400,
                    use_split_dirs=False,
                    progress_callback=progress_callback
                )
                y_train = y
                self.result_text.append(f"Loaded {len(X)} samples with {X.shape[1]} features")
            
            self.result_text.append(f"Classes: {', '.join(self.classifier.get_class_names())}")
            self.progress_bar.setValue(50)
            
            self.result_text.append(f"\nTraining {model_type} model...")
            self.progress_bar.setValue(60)
            
            if hasattr(self, 'is_split_data') and self.is_split_data:
                result = self.classifier.train(
                    X_train, y_train, 
                    model_type=model_type,
                    random_state=42,
                    X_val=X_val if X_val is not None else None, 
                    y_val=y_val if y_val is not None else None,
                    X_test=X_test if X_test is not None else None, 
                    y_test=y_test if y_test is not None else None
                )
            else:
                result = self.classifier.train(
                    X, y, 
                    model_type=model_type,
                    test_size=self.test_size_spin.value(),
                    random_state=42
                )
            
            self.progress_bar.setValue(90)
            
            self.result_text.append("\n=== Training Results ===")
            self.result_text.append(f"Test Accuracy: {result['accuracy']:.4f}")
            self.result_text.append(f"Training samples: {result['train_size']}")
            self.result_text.append(f"Test samples: {result['test_size']}")
            if result.get('val_size', 0) > 0:
                self.result_text.append(f"Validation samples: {result['val_size']}")
                self.result_text.append(f"Validation Accuracy: {result['val_accuracy']:.4f}")
            self.result_text.append(f"Number of classes: {result['n_classes']}")
            
            self.result_text.append("\n=== Test Set Classification Report ===")
            report = result['report']
            for cls in result['classes']:
                if cls in report:
                    self.result_text.append(
                        f"{cls}: Precision={report[cls]['precision']:.4f}, "
                        f"Recall={report[cls]['recall']:.4f}, "
                        f"F1={report[cls]['f1-score']:.4f}"
                    )
            
            if result.get('has_validation') and 'val_report' in result:
                self.result_text.append("\n=== Validation Set Classification Report ===")
                val_report = result['val_report']
                for cls in result['classes']:
                    if cls in val_report:
                        self.result_text.append(
                            f"{cls}: Precision={val_report[cls]['precision']:.4f}, "
                            f"Recall={val_report[cls]['recall']:.4f}, "
                            f"F1={val_report[cls]['f1-score']:.4f}"
                        )
            
            self.progress_bar.setValue(100)
            self.train_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            
            self.training_completed.emit(result)
            
        except Exception as e:
            self.result_text.append(f"\nError: {str(e)}")
            self.train_btn.setEnabled(True)
            import traceback
            traceback.print_exc()
    
    def _save_model(self):
        if self.classifier is None or not self.classifier.is_trained:
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Model", "spectrum_classifier.pkl", 
            "Pickle Files (*.pkl)"
        )
        
        if filepath:
            try:
                self.classifier.save(filepath)
                self.result_text.append(f"\nModel saved to: {filepath}")
            except Exception as e:
                self.result_text.append(f"Error saving model: {str(e)}")
    
    def refresh_text(self):
        self.data_group.setTitle(t("training_data"))
        self.model_group.setTitle(t("model_settings"))
        self.result_group.setTitle(t("results"))
        self.data_path_label.setText(t("data_directory") + ":")
        self.select_data_btn.setText("Select...")
        self.train_btn.setText(t("start_training"))
        self.save_btn.setText(t("save_model"))
