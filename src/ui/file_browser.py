from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QListWidgetItem, QLabel, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal


class FileBrowserWidget(QWidget):
    files_selected = pyqtSignal(list)
    folder_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setStyleSheet("font-weight: bold;")
        self.open_btn = QPushButton("Open Folder")
        
        header_layout.addWidget(self.folder_label)
        header_layout.addWidget(self.open_btn)
        
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        self.count_label = QLabel("0 files")
        
        layout.addLayout(header_layout)
        layout.addWidget(self.file_list)
        layout.addWidget(self.count_label)
        
        self.open_btn.clicked.connect(self._open_folder)
        self.file_list.itemClicked.connect(self._on_item_clicked)
        
        self.current_folder = ""
        self.file_paths = {}

    def _open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Data Folder")
        if folder:
            self.current_folder = folder
            self.folder_label.setText(folder)
            self.folder_selected.emit(folder)

    def set_files(self, files: list):
        self.file_list.clear()
        self.file_paths.clear()
        
        for filepath in files:
            item = QListWidgetItem(filepath)
            self.file_list.addItem(item)
            self.file_paths[filepath] = filepath
        
        self.count_label.setText(f"{len(files)} files")

    def _on_item_clicked(self, item):
        selected_files = self._get_selected_files()
        self.files_selected.emit(selected_files)

    def _get_selected_files(self) -> list:
        selected_items = self.file_list.selectedItems()
        return [self.file_paths.get(item.text(), item.text()) for item in selected_items]

    def get_selected_files(self) -> list:
        return self._get_selected_files()

    def get_selected_file(self) -> str:
        selected = self._get_selected_files()
        return selected[0] if selected else ""

    def clear(self):
        self.file_list.clear()
        self.file_paths.clear()
        self.count_label.setText("0 files")
