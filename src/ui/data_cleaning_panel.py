from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QFileDialog, QTextEdit,
                             QListWidget, QCheckBox, QSpinBox, QDoubleSpinBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QProgressBar, QMessageBox, QComboBox, QSplitter, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
import os
import numpy as np
from typing import List, Dict
from ..core.i18n import t


class DataCleaningPanel(QWidget):
    cleaning_completed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.data_cleaner = None
        self.loaded_files = []
        self.file_data = {}
        self.all_issues = []
        
        self._init_ui()
    
    def _init_ui(self):
        from ..core.data_cleaner import DataCleaner
        self.data_cleaner = DataCleaner()
        
        main_layout = QVBoxLayout(self)
        
        self.options_group = QGroupBox(t("detection_options"))
        options_layout = QVBoxLayout()
        
        invalid_layout = QHBoxLayout()
        self.check_invalid_cb = QCheckBox(t("detect_invalid_data"))
        self.check_invalid_cb.setChecked(True)
        invalid_layout.addWidget(self.check_invalid_cb)
        invalid_layout.addStretch()
        options_layout.addLayout(invalid_layout)
        
        anomaly_layout = QHBoxLayout()
        self.check_anomaly_cb = QCheckBox(t("detect_anomalies"))
        self.check_anomaly_cb.setChecked(True)
        anomaly_layout.addWidget(self.check_anomaly_cb)
        
        anomaly_layout.addWidget(QLabel(t("method") + ":"))
        self.anomaly_method_combo = QComboBox()
        self.anomaly_method_combo.addItems(["IQR", "Z-Score"])
        anomaly_layout.addWidget(self.anomaly_method_combo)
        
        anomaly_layout.addWidget(QLabel(t("threshold") + ":"))
        self.anomaly_threshold_spin = QDoubleSpinBox()
        self.anomaly_threshold_spin.setRange(1.0, 5.0)
        self.anomaly_threshold_spin.setValue(3.0)
        self.anomaly_threshold_spin.setSingleStep(0.5)
        anomaly_layout.addWidget(self.anomaly_threshold_spin)
        anomaly_layout.addStretch()
        options_layout.addLayout(anomaly_layout)
        
        duplicate_layout = QHBoxLayout()
        self.check_duplicate_cb = QCheckBox(t("detect_duplicates"))
        self.check_duplicate_cb.setChecked(True)
        duplicate_layout.addWidget(self.check_duplicate_cb)
        
        duplicate_layout.addWidget(QLabel(t("similarity") + ":"))
        self.similarity_threshold_spin = QDoubleSpinBox()
        self.similarity_threshold_spin.setRange(0.8, 1.0)
        self.similarity_threshold_spin.setValue(0.99)
        self.similarity_threshold_spin.setSingleStep(0.01)
        self.similarity_threshold_spin.setSuffix(" (correlation)")
        duplicate_layout.addWidget(self.similarity_threshold_spin)
        duplicate_layout.addStretch()
        options_layout.addLayout(duplicate_layout)
        
        outlier_layout = QHBoxLayout()
        self.check_outlier_cb = QCheckBox(t("detect_outlier_spectra"))
        self.check_outlier_cb.setChecked(True)
        outlier_layout.addWidget(self.check_outlier_cb)
        
        outlier_layout.addWidget(QLabel(t("similarity") + ":"))
        self.outlier_threshold_spin = QDoubleSpinBox()
        self.outlier_threshold_spin.setRange(0.1, 0.6)
        self.outlier_threshold_spin.setValue(0.6)
        self.outlier_threshold_spin.setSingleStep(0.05)
        self.outlier_threshold_spin.setSuffix(" (correlation)")
        outlier_layout.addWidget(self.outlier_threshold_spin)
        outlier_layout.addStretch()
        options_layout.addLayout(outlier_layout)
        
        self.options_group.setLayout(options_layout)
        
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.options_group, 1)
        
        data_group_widget = QWidget()
        data_group_layout = QVBoxLayout()
        
        data_path_layout = QHBoxLayout()
        self.data_path_label = QLabel(t("no_folder_selected"))
        self.data_path_label.setWordWrap(True)
        data_path_layout.addWidget(self.data_path_label, 1)
        
        self.select_data_btn = QPushButton(t("select_folder"))
        self.select_data_btn.clicked.connect(self._select_data_folder)
        data_path_layout.addWidget(self.select_data_btn)
        
        data_group_layout.addLayout(data_path_layout)
        
        self.file_count_label = QLabel("")
        self.file_count_label.setStyleSheet("color: gray;")
        data_group_layout.addWidget(self.file_count_label)
        
        data_group_widget.setLayout(data_group_layout)
        top_layout.addWidget(data_group_widget, 1)
        
        self.analyze_btn = QPushButton(t("start_analysis"))
        self.analyze_btn.clicked.connect(self._start_analysis)
        self.analyze_btn.setEnabled(False)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        self.results_group = QGroupBox(t("analysis_results"))
        results_layout = QVBoxLayout()
        
        self.issues_table = QTableWidget()
        self.issues_table.setColumnCount(4)
        self.issues_table.setHorizontalHeaderLabels([t("file_col"), t("type_col"), t("severity_col"), t("description_col")])
        self.issues_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.issues_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.issues_table.setColumnWidth(0, 200)
        self.issues_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.issues_table.itemClicked.connect(self._on_issue_clicked)
        self.issues_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.issues_table.customContextMenuRequested.connect(self._show_context_menu)
        
        self.preview_group = QGroupBox(t("spectrum_preview"))
        preview_layout = QVBoxLayout()
        
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
            self.preview_canvas = FigureCanvasQTAgg(Figure(figsize=(8, 6)))
            preview_layout.addWidget(self.preview_canvas)
            self.preview_ax = self.preview_canvas.figure.add_subplot(111)
        except ImportError:
            self.preview_canvas = None
            preview_layout.addWidget(QLabel("Matplotlib not available"))
        
        self.preview_group.setLayout(preview_layout)
        
        self.result_summary = QTextEdit()
        self.result_summary.setReadOnly(True)
        
        bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        bottom_splitter.addWidget(self.result_summary)
        bottom_splitter.addWidget(self.preview_group)
        
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(self.issues_table)
        main_splitter.addWidget(bottom_splitter)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 1)
        
        results_layout.addWidget(main_splitter, 1)
        
        self.results_group.setLayout(results_layout)
        
        self.action_group = QGroupBox(t("actions"))
        action_layout = QHBoxLayout()
        
        self.export_btn = QPushButton(t("export_report"))
        self.export_btn.clicked.connect(self._export_report)
        self.export_btn.setEnabled(False)
        action_layout.addWidget(self.export_btn)
        
        self.batch_delete_btn = QPushButton(t("delete_selected"))
        self.batch_delete_btn.clicked.connect(self._batch_delete)
        self.batch_delete_btn.setEnabled(False)
        action_layout.addWidget(self.batch_delete_btn)
        
        self.batch_move_btn = QPushButton(t("move_to_temp"))
        self.batch_move_btn.clicked.connect(self._batch_move)
        self.batch_move_btn.setEnabled(False)
        action_layout.addWidget(self.batch_move_btn)
        
        self.clear_btn = QPushButton(t("clear"))
        self.clear_btn.clicked.connect(self._clear_results)
        action_layout.addWidget(self.clear_btn)
        
        action_layout.addStretch()
        self.action_group.setLayout(action_layout)
        
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.analyze_btn)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.results_group)
        main_layout.addWidget(self.action_group)
    
    def _select_data_folder(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Data Directory", 
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        )
        
        if directory:
            self.data_dir = directory
            self.data_path_label.setText(f"Data: {directory}")
            
            isf_files = [f for f in os.listdir(directory) if f.lower().endswith('.isf')]
            xlsx_files = [f for f in os.listdir(directory) if f.lower().endswith(('.xlsx', '.xls'))]
            all_files = isf_files + xlsx_files
            
            self.loaded_files = [os.path.join(directory, f) for f in all_files]
            self.file_count_label.setText(f"Found {len(self.loaded_files)} files")
            
            if self.loaded_files:
                self.analyze_btn.setEnabled(True)
            else:
                self.file_count_label.setText("No data files found")
    
    def _start_analysis(self):
        if not self.loaded_files:
            return
        
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.result_summary.clear()
        self.issues_table.setRowCount(0)
        self.all_issues = []
        self.file_data = {}
        
        try:
            from ..core.isf_reader import parse_isf_file
            from ..core.xlsx_reader import parse_xlsx_file
            
            self.result_summary.append("Loading files...")
            self.progress_bar.setValue(10)
            
            total_files = len(self.loaded_files)
            
            for idx, filepath in enumerate(self.loaded_files):
                try:
                    ext = os.path.splitext(filepath)[1].lower()
                    
                    if ext not in ('.isf', '.xlsx', '.xls'):
                        self.all_issues.append({
                            'file': os.path.basename(filepath),
                            'type': 'invalid_format',
                            'severity': 'high',
                            'description': f'不支持的文件格式: {ext}，仅支持 .isf, .xlsx, .xls',
                            'full_path': filepath
                        })
                        continue
                    
                    if ext in ('.xlsx', '.xls'):
                        try:
                            from python_calamine import CalamineWorkbook
                            wb = CalamineWorkbook.from_path(filepath)
                            ws = wb.get_sheet_by_index(0)
                            data_check = ws.to_python()
                            
                            has_wave = False
                            has_intensity = False
                            for row in data_check[:10]:
                                if row and len(row) > 0 and row[0] is not None:
                                    try:
                                        float(row[0])
                                        has_wave = True
                                    except:
                                        pass
                                if row and len(row) > 4 and row[4] is not None:
                                    try:
                                        float(row[4])
                                        has_intensity = True
                                    except:
                                        pass
                            
                            if not has_wave or not has_intensity:
                                self.all_issues.append({
                                    'file': os.path.basename(filepath),
                                    'type': 'invalid_format',
                                    'severity': 'high',
                                    'description': 'Excel文件缺少有效的波长列(第1列)或强度列(第5列)',
                                    'full_path': filepath
                                })
                                continue
                        except Exception as excel_err:
                            self.all_issues.append({
                                'file': os.path.basename(filepath),
                                'type': 'invalid_format',
                                'severity': 'high',
                                'description': f'Excel文件格式错误: {str(excel_err)}',
                                'full_path': filepath
                            })
                            continue
                    
                    if ext == '.isf':
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                first_line = f.readline()
                                if 'Wave[nm]' not in first_line and 'Refl/Tran' not in first_line:
                                    self.all_issues.append({
                                        'file': os.path.basename(filepath),
                                        'type': 'invalid_format',
                                        'severity': 'high',
                                        'description': 'ISF文件格式错误，缺少必要的表头 Wave[nm] 或 Refl/Tran',
                                        'full_path': filepath
                                    })
                                    continue
                        except UnicodeDecodeError:
                            try:
                                with open(filepath, 'r', encoding='gbk') as f:
                                    first_line = f.readline()
                                    if 'Wave[nm]' not in first_line and 'Refl/Tran' not in first_line:
                                        self.all_issues.append({
                                            'file': os.path.basename(filepath),
                                            'type': 'invalid_format',
                                            'severity': 'high',
                                            'description': 'ISF文件编码错误或格式错误',
                                            'full_path': filepath
                                        })
                                        continue
                            except:
                                self.all_issues.append({
                                    'file': os.path.basename(filepath),
                                    'type': 'invalid_format',
                                    'severity': 'high',
                                    'description': 'ISF文件读取失败，可能是编码问题',
                                    'full_path': filepath
                                })
                                continue
                        except Exception as isf_err:
                            self.all_issues.append({
                                'file': os.path.basename(filepath),
                                'type': 'invalid_format',
                                'severity': 'high',
                                'description': f'ISF文件格式错误: {str(isf_err)}',
                                'full_path': filepath
                            })
                            continue
                    
                    if ext in ('.xlsx', '.xls'):
                        data = parse_xlsx_file(filepath)
                    else:
                        data = parse_isf_file(filepath)
                    
                    if data.wavelengths is None or data.intensities is None:
                        self.all_issues.append({
                            'file': os.path.basename(filepath),
                            'type': 'invalid_file',
                            'severity': 'high',
                            'description': '文件无有效数据（wavelengths或intensities为空）',
                            'full_path': filepath
                        })
                        continue
                    
                    if len(data.wavelengths) == 0 or len(data.intensities) == 0:
                        self.all_issues.append({
                            'file': os.path.basename(filepath),
                            'type': 'invalid_file',
                            'severity': 'high',
                            'description': '文件数据为空',
                            'full_path': filepath
                        })
                        continue
                    
                    mask = data.wavelengths >= 400
                    filtered_wl = data.wavelengths[mask]
                    filtered_int = data.intensities[mask]
                    
                    if len(filtered_wl) == 0:
                        self.all_issues.append({
                            'file': os.path.basename(filepath),
                            'type': 'invalid_file',
                            'severity': 'high',
                            'description': '过滤400nm后无有效数据',
                            'full_path': filepath
                        })
                        continue
                    
                    if len(filtered_wl) < 10:
                        self.all_issues.append({
                            'file': os.path.basename(filepath),
                            'type': 'insufficient_data',
                            'severity': 'medium',
                            'description': f'有效数据点过少（{len(filtered_wl)}个），建议至少10个点',
                            'full_path': filepath
                        })
                    
                    self.file_data[filepath] = {
                        'wavelengths': filtered_wl,
                        'intensities': filtered_int,
                        'filename': os.path.basename(filepath)
                    }
                    
                except Exception as e:
                    self.all_issues.append({
                        'file': os.path.basename(filepath),
                        'type': 'invalid_file',
                        'severity': 'high',
                        'description': f'文件读取失败: {str(e)}',
                        'full_path': filepath
                    })
                
                progress = 10 + int((idx + 1) / total_files * 30)
                self.progress_bar.setValue(progress)
            
            self.result_summary.append(f"Loaded {len(self.file_data)} files successfully\n")
            
            self._detect_issues()
            
            self.progress_bar.setValue(100)
            self.analyze_btn.setEnabled(True)
            has_issues = len(self.all_issues) > 0
            self.export_btn.setEnabled(has_issues)
            self.batch_delete_btn.setEnabled(has_issues)
            self.batch_move_btn.setEnabled(has_issues)
            
            self.cleaning_completed.emit({'issues': self.all_issues})
            
        except Exception as e:
            self.result_summary.append(f"Error: {str(e)}\n")
            self.analyze_btn.setEnabled(True)
            import traceback
            traceback.print_exc()
    
    def _detect_issues(self):
        invalid_issues = []
        anomaly_issues = []
        duplicate_issues = []
        outlier_issues = []
        
        total_issues_expected = len(self.file_data)
        if self.check_duplicate_cb.isChecked():
            total_issues_expected += 1
        if self.check_outlier_cb.isChecked():
            total_issues_expected += 1
        
        progress_base = 40
        progress_per_item = 50 // max(total_issues_expected, 1)
        
        if self.check_invalid_cb.isChecked():
            self.result_summary.append("\n=== Checking Invalid Data ===")
            
            for idx, (filepath, data) in enumerate(self.file_data.items()):
                wavelengths = data['wavelengths']
                intensities = data['intensities']
                
                issues = self.data_cleaner.check_invalid_data(
                    wavelengths, intensities, filepath
                )
                
                for issue in issues:
                    invalid_issues.append({
                        'file': data['filename'],
                        'type': issue.issue_type,
                        'severity': issue.severity,
                        'description': issue.description,
                        'full_path': filepath
                    })
                
                progress = progress_base + (idx + 1) * progress_per_item
                self.progress_bar.setValue(progress)
            
            self.result_summary.append(f"Found {len(invalid_issues)} invalid data issues\n")
        
        if self.check_anomaly_cb.isChecked():
            self.result_summary.append("\n=== Checking Anomalies ===")
            
            method = self.anomaly_method_combo.currentText().lower().replace("-", "")
            threshold = self.anomaly_threshold_spin.value()
            
            idx = 0
            for filepath, data in self.file_data.items():
                intensities = data['intensities']
                
                anomalies, anomaly_indices = self.data_cleaner.detect_anomalies(
                    intensities, method=method, threshold=threshold
                )
                
                anomaly_count = len(anomaly_indices)
                if anomaly_count > 0:
                    anomaly_issues.append({
                        'file': data['filename'],
                        'type': 'anomaly',
                        'severity': 'medium',
                        'description': f"Found {anomaly_count} anomalous points ({anomaly_count/len(intensities)*100:.1f}%)",
                        'full_path': filepath,
                        'indices': anomaly_indices
                    })
                
                idx += 1
                progress = progress_base + (idx + 1) * progress_per_item
                self.progress_bar.setValue(progress)
            
            self.result_summary.append(f"Found {len(anomaly_issues)} files with anomalies\n")
        
        if self.check_duplicate_cb.isChecked():
            self.result_summary.append("\n=== Checking Duplicates ===")
            
            self.progress_bar.setValue(90)
            
            spectra = []
            paths = []
            for filepath, data in self.file_data.items():
                spectra.append((data['wavelengths'], data['intensities']))
                paths.append(filepath)
            
            similarity = self.similarity_threshold_spin.value()
            duplicate_issues = self.data_cleaner.detect_duplicates(
                spectra, paths, similarity_threshold=similarity
            )
            
            for issue in duplicate_issues:
                anomaly_issues.append({
                    'file': os.path.basename(issue.file_path),
                    'type': issue.issue_type,
                    'severity': issue.severity,
                    'description': issue.description,
                    'full_path': issue.file_path,
                    'indices': issue.indices
                })
            
            self.result_summary.append(f"Found {len(duplicate_issues)} duplicate files\n")
        
        if self.check_outlier_cb.isChecked():
            self.result_summary.append("\n=== Checking Outlier Spectra (异种类别) ===")
            
            self.progress_bar.setValue(90)
            
            spectra = []
            paths = []
            for filepath, data in self.file_data.items():
                spectra.append((data['wavelengths'], data['intensities']))
                paths.append(filepath)
            
            similarity = self.outlier_threshold_spin.value()
            outlier_issues = self.data_cleaner.detect_outlier_spectra(
                spectra, paths, similarity_threshold=similarity
            )
            
            for issue in outlier_issues:
                anomaly_issues.append({
                    'file': os.path.basename(issue.file_path),
                    'type': issue.issue_type,
                    'severity': issue.severity,
                    'description': issue.description,
                    'full_path': issue.file_path,
                    'indices': issue.indices
                })
            
            self.result_summary.append(f"Found {len(outlier_issues)} outlier spectra\n")
        
        self.all_issues = self.all_issues + invalid_issues + anomaly_issues
        self._display_results()
    
    def _display_results(self):
        self.issues_table.setRowCount(len(self.all_issues))
        
        high_count = sum(1 for i in self.all_issues if i['severity'] == 'high')
        medium_count = sum(1 for i in self.all_issues if i['severity'] == 'medium')
        low_count = sum(1 for i in self.all_issues if i['severity'] == 'low')
        
        for row, issue in enumerate(self.all_issues):
            self.issues_table.setItem(row, 0, QTableWidgetItem(issue['file']))
            self.issues_table.setItem(row, 1, QTableWidgetItem(issue['type']))
            
            severity_item = QTableWidgetItem(issue['severity'])
            if issue['severity'] == 'high':
                severity_item.setBackground(Qt.GlobalColor.red)
            elif issue['severity'] == 'medium':
                severity_item.setBackground(Qt.GlobalColor.yellow)
            else:
                severity_item.setBackground(Qt.GlobalColor.green)
            self.issues_table.setItem(row, 2, severity_item)
            
            self.issues_table.setItem(row, 3, QTableWidgetItem(issue['description']))
        
        self.result_summary.append("\n=== Summary ===")
        self.result_summary.append(f"Total issues: {len(self.all_issues)}")
        self.result_summary.append(f"  - High: {high_count}")
        self.result_summary.append(f"  - Medium: {medium_count}")
        self.result_summary.append(f"  - Low: {low_count}")
        
        if high_count > 0:
            self.result_summary.append(f"\nWarning: {high_count} high severity issues detected!")
            self.result_summary.append("Please review and clean these files before modeling.")
    
    def _export_report(self):
        if not self.all_issues:
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Report", "data_cleaning_report.txt", 
            "Text Files (*.txt)"
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("Data Cleaning Report\n")
                    f.write("=" * 60 + "\n\n")
                    
                    f.write(f"Total issues: {len(self.all_issues)}\n")
                    
                    high = [i for i in self.all_issues if i['severity'] == 'high']
                    medium = [i for i in self.all_issues if i['severity'] == 'medium']
                    low = [i for i in self.all_issues if i['severity'] == 'low']
                    
                    f.write(f"  High: {len(high)}\n")
                    f.write(f"  Medium: {len(medium)}\n")
                    f.write(f"  Low: {len(low)}\n\n")
                    
                    if high:
                        f.write("\n=== High Severity Issues ===\n")
                        for issue in high:
                            f.write(f"\n[{issue['file']}]\n")
                            f.write(f"  Type: {issue['type']}\n")
                            f.write(f"  Description: {issue['description']}\n")
                    
                    if medium:
                        f.write("\n=== Medium Severity Issues ===\n")
                        for issue in medium:
                            f.write(f"\n[{issue['file']}]\n")
                            f.write(f"  Type: {issue['type']}\n")
                            f.write(f"  Description: {issue['description']}\n")
                    
                    if low:
                        f.write("\n=== Low Severity Issues ===\n")
                        for issue in low:
                            f.write(f"\n[{issue['file']}]\n")
                            f.write(f"  Type: {issue['type']}\n")
                            f.write(f"  Description: {issue['description']}\n")
                
                QMessageBox.information(self, "Success", f"Report saved to:\n{filepath}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save report:\n{str(e)}")
    
    def _clear_results(self):
        self.issues_table.setRowCount(0)
        self.result_summary.clear()
        self.all_issues = []
        self.file_data = {}
        self.export_btn.setEnabled(False)
        self.batch_delete_btn.setEnabled(False)
        self.batch_move_btn.setEnabled(False)
        if hasattr(self, 'preview_ax'):
            self.preview_ax.clear()
            self.preview_canvas.figure.canvas.draw()
    
    def _on_issue_clicked(self, item):
        row = item.row()
        if row < len(self.all_issues):
            issue = self.all_issues[row]
            filename = issue.get('file', '')
            full_path = issue.get('full_path', '')
            
            data = None
            if full_path and full_path in self.file_data:
                data = self.file_data[full_path]
            elif filename:
                for path, d in self.file_data.items():
                    if d.get('filename') == filename:
                        data = d
                        break
            
            if data is not None and hasattr(self, 'preview_ax'):
                wavelengths = data.get('wavelengths', [])
                intensities = data.get('intensities', [])
                
                if len(wavelengths) > 0 and len(intensities) > 0:
                    self.preview_ax.clear()
                    self.preview_ax.plot(wavelengths, intensities, 'b-', linewidth=1)
                    self.preview_ax.set_xlabel('Wavelength (nm)')
                    self.preview_ax.set_ylabel('Intensity')
                    self.preview_ax.set_title(f"{filename}")
                    self.preview_ax.grid(True, alpha=0.3)
                else:
                    self.preview_ax.clear()
                    self.preview_ax.text(0.5, 0.5, issue.get('description', 'No data available'), 
                                        ha='center', va='center', fontsize=12,
                                        transform=self.preview_ax.transAxes)
                    self.preview_ax.set_title(f"{filename} - No Data")
                    self.preview_ax.axis('off')
                self.preview_canvas.figure.canvas.draw()
    
    def refresh_text(self):
        self.options_group.setTitle(t("detection_options"))
        self.results_group.setTitle(t("analysis_results"))
        self.preview_group.setTitle(t("spectrum_preview"))
        self.action_group.setTitle(t("actions"))
        self.select_data_btn.setText(t("select_folder"))
        self.analyze_btn.setText(t("start_analysis"))
        self.export_btn.setText(t("export_report"))
        self.batch_delete_btn.setText(t("delete_selected"))
        self.batch_move_btn.setText(t("move_to_temp"))
        self.clear_btn.setText(t("clear"))
    
    def _show_context_menu(self, position):
        selected_items = self.issues_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        if row >= len(self.all_issues):
            return
        
        issue = self.all_issues[row]
        full_path = issue.get('full_path', '')
        
        menu = QMenu(self)
        
        delete_action = QAction(t("delete_file"), self)
        delete_action.triggered.connect(lambda: self._delete_file(row))
        menu.addAction(delete_action)
        
        open_location_action = QAction(t("open_file_location"), self)
        open_location_action.triggered.connect(lambda: self._open_file_location(full_path))
        menu.addAction(open_location_action)
        
        menu.exec(self.issues_table.viewport().mapToGlobal(position))
    
    def _delete_file(self, row):
        if row >= len(self.all_issues):
            return
        
        issue = self.all_issues[row]
        filename = issue.get('file', '')
        full_path = issue.get('full_path', '')
        
        reply = QMessageBox.question(
            self, 
            t("confirm_delete"),
            t("confirm_delete_msg").format(filename=filename),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.exists(full_path):
                    os.remove(full_path)
                    self.result_summary.append(f"Deleted: {filename}")
                    
                    self.all_issues.pop(row)
                    
                    self.issues_table.removeRow(row)
                    
                    if full_path in self.file_data:
                        del self.file_data[full_path]
                        
            except Exception as e:
                QMessageBox.critical(self, t("error"), f"{t('delete_failed')}: {str(e)}")
    
    def _batch_delete(self):
        selected_rows = set()
        for item in self.issues_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            return
        
        rows_to_delete = sorted(selected_rows, reverse=True)
        count = len(rows_to_delete)
        
        reply = QMessageBox.question(
            self,
            t("confirm_batch_delete"),
            t("confirm_batch_delete_msg").format(count=count),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            deleted_count = 0
            for row in rows_to_delete:
                if row >= len(self.all_issues):
                    continue
                issue = self.all_issues[row]
                full_path = issue.get('full_path', '')
                
                try:
                    if os.path.exists(full_path):
                        os.remove(full_path)
                        deleted_count += 1
                        
                    if full_path in self.file_data:
                        del self.file_data[full_path]
                        
                except Exception as e:
                    self.result_summary.append(f"Failed to delete {issue.get('file', '')}: {str(e)}")
            
            for row in rows_to_delete:
                if row < len(self.all_issues):
                    self.all_issues.pop(row)
            
            self._refresh_issues_table()
            self.result_summary.append(f"Deleted {deleted_count} files")
    
    def _batch_move(self):
        selected_rows = set()
        for item in self.issues_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            return
        
        target_folder = QFileDialog.getExistingDirectory(
            self,
            t("select_target_folder"),
            ""
        )
        
        if not target_folder:
            return
        
        moved_count = 0
        rows_to_remove = []
        
        for row in selected_rows:
            if row >= len(self.all_issues):
                continue
            issue = self.all_issues[row]
            full_path = issue.get('full_path', '')
            filename = issue.get('file', '')
            
            if not full_path or not os.path.exists(full_path):
                continue
            
            try:
                import shutil
                target_path = os.path.join(target_folder, filename)
                shutil.move(full_path, target_path)
                moved_count += 1
                rows_to_remove.append(row)
                
                if full_path in self.file_data:
                    del self.file_data[full_path]
                    
            except Exception as e:
                self.result_summary.append(f"Failed to move {filename}: {str(e)}")
        
        for row in sorted(rows_to_remove, reverse=True):
            if row < len(self.all_issues):
                self.all_issues.pop(row)
        
        self._refresh_issues_table()
        self.result_summary.append(t("move_success").format(count=moved_count, folder=target_folder))
    
    def _refresh_issues_table(self):
        self.issues_table.setRowCount(len(self.all_issues))
        for row, issue in enumerate(self.all_issues):
            self.issues_table.setItem(row, 0, QTableWidgetItem(issue.get('file', '')))
            self.issues_table.setItem(row, 1, QTableWidgetItem(issue.get('type', '')))
            
            severity = issue.get('severity', 'low')
            severity_item = QTableWidgetItem(severity)
            if severity == 'high':
                severity_item.setBackground(Qt.GlobalColor.red)
            elif severity == 'medium':
                severity_item.setBackground(Qt.GlobalColor.yellow)
            self.issues_table.setItem(row, 2, severity_item)
            
            self.issues_table.setItem(row, 3, QTableWidgetItem(issue.get('description', '')))
            
            self.issues_table.setItem(row, 4, QTableWidgetItem(issue.get('description', '')))
    
    def _open_file_location(self, filepath):
        if not filepath or not os.path.exists(filepath):
            return
        
        folder = os.path.dirname(filepath)
        os.startfile(folder) if os.name == 'nt' else os.system(f'xdg-open "{folder}"')
