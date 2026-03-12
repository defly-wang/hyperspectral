from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QGroupBox, QFileDialog,
                             QTextEdit, QDoubleSpinBox, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal
import os


class TrainingPanel(QWidget):
    training_completed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.classifier = None
        self._init_ui()
    
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        
        data_group = QGroupBox("Training Data")
        data_layout = QVBoxLayout()
        
        data_path_layout = QHBoxLayout()
        self.data_path_label = QLabel("Data Directory:")
        self.data_path_label.setWordWrap(True)
        data_path_layout.addWidget(self.data_path_label)
        
        self.select_data_btn = QPushButton("Select...")
        self.select_data_btn.clicked.connect(self._select_data_directory)
        data_path_layout.addWidget(self.select_data_btn)
        
        data_layout.addLayout(data_path_layout)
        
        self.data_info_label = QLabel("No directory selected")
        self.data_info_label.setWordWrap(True)
        self.data_info_label.setStyleSheet("color: gray;")
        data_layout.addWidget(self.data_info_label)
        
        data_group.setLayout(data_layout)
        
        model_group = QGroupBox("Model Settings")
        model_layout = QVBoxLayout()
        
        model_type_layout = QHBoxLayout()
        model_type_layout.addWidget(QLabel("Model Type:"))
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems(["Random Forest", "SVM", "Gradient Boosting"])
        model_type_layout.addWidget(self.model_type_combo)
        model_type_layout.addStretch()
        model_layout.addLayout(model_type_layout)
        
        test_size_layout = QHBoxLayout()
        test_size_layout.addWidget(QLabel("Test Size:"))
        self.test_size_spin = QDoubleSpinBox()
        self.test_size_spin.setRange(0.1, 0.5)
        self.test_size_spin.setValue(0.2)
        self.test_size_spin.setSingleStep(0.05)
        self.test_size_spin.setSuffix(" (ratio)")
        test_size_layout.addWidget(self.test_size_spin)
        test_size_layout.addStretch()
        model_layout.addLayout(test_size_layout)
        
        model_group.setLayout(model_layout)
        
        self.train_btn = QPushButton("Start Training")
        self.train_btn.setEnabled(False)
        self.train_btn.clicked.connect(self._start_training)
        
        self.save_btn = QPushButton("Save Model")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save_model)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        result_group = QGroupBox("Results")
        result_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)
        result_layout.addWidget(self.result_text)
        
        result_group.setLayout(result_layout)
        
        main_layout.addWidget(data_group)
        main_layout.addWidget(model_group)
        main_layout.addWidget(self.train_btn)
        main_layout.addWidget(self.save_btn)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(result_group)
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
        categories = [d for d in os.listdir(directory) 
                     if os.path.isdir(os.path.join(directory, d))]
        
        if not categories:
            self.data_info_label.setText("No category subdirectories found")
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
                "Random Forest": "rf",
                "SVM": "svm",
                "Gradient Boosting": "gb"
            }
            model_type = model_type_map[self.model_type_combo.currentText()]
            
            self.classifier = SpectrumClassifier()
            
            self.result_text.append("Loading data...")
            self.progress_bar.setValue(20)
            
            X, y = self.classifier.load_data_from_directory(
                self.data_dir, 
                min_wavelength=400
            )
            
            self.result_text.append(f"Loaded {len(X)} samples with {X.shape[1]} features")
            self.result_text.append(f"Classes: {', '.join(self.classifier.get_class_names())}")
            self.progress_bar.setValue(50)
            
            self.result_text.append(f"\nTraining {model_type} model...")
            self.progress_bar.setValue(60)
            
            result = self.classifier.train(
                X, y, 
                model_type=model_type,
                test_size=self.test_size_spin.value(),
                random_state=42
            )
            
            self.progress_bar.setValue(90)
            
            self.result_text.append("\n=== Training Results ===")
            self.result_text.append(f"Accuracy: {result['accuracy']:.4f}")
            self.result_text.append(f"Training samples: {result['train_size']}")
            self.result_text.append(f"Test samples: {result['test_size']}")
            self.result_text.append(f"Number of classes: {result['n_classes']}")
            
            self.result_text.append("\n=== Classification Report ===")
            report = result['report']
            for cls in result['classes']:
                if cls in report:
                    self.result_text.append(
                        f"{cls}: Precision={report[cls]['precision']:.4f}, "
                        f"Recall={report[cls]['recall']:.4f}, "
                        f"F1={report[cls]['f1-score']:.4f}"
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
