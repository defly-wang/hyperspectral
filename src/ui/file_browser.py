"""
文件浏览器组件

提供文件夹选择和文件列表显示功能，支持多选文件并发射选中信号

主要功能:
    - 选择数据文件夹并扫描其中的光谱文件(.isf, .xlsx, .xls)
    - 显示文件列表，支持鼠标和键盘多选
    - 选中文件后发射信号通知其他组件

信号:
    files_selected: 选中文件列表变化时发射，参数为文件路径列表
    folder_selected: 文件夹选中时发射，参数为文件夹路径

用法:
    browser = FileBrowserWidget()
    browser.files_selected.connect(handle_files)
    browser.folder_selected.connect(handle_folder)
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QListWidgetItem, QLabel, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
import os
from ..core.i18n import t


class FileBrowserWidget(QWidget):
    """
    文件浏览器widget
    
    整合文件夹选择和文件列表显示，支持多选光谱文件
    """
    
    files_selected = pyqtSignal(list)
    folder_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """
        初始化文件浏览器
        
        Args:
            parent: 父widget
        """
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        self.folder_label = QLabel(t("no_folder_selected"))
        self.folder_label.setStyleSheet("font-weight: bold;")
        self.open_btn = QPushButton(t("open_folder_btn"))
        
        header_layout.addWidget(self.folder_label)
        header_layout.addWidget(self.open_btn)
        
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        self.count_label = QLabel(f"0 {t('files')}")
        
        layout.addLayout(header_layout)
        layout.addWidget(self.file_list)
        layout.addWidget(self.count_label)
        
        self.open_btn.clicked.connect(self._open_folder)
        self.file_list.itemSelectionChanged.connect(self._on_selection_changed)
        
        self.current_folder = ""
        self.file_paths = {}

    def _open_folder(self):
        """
        打开文件夹选择对话框
        
        弹出系统文件夹选择对话框，选中后扫描文件夹中的光谱文件，
        并发射folder_selected信号
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Data Folder")
        if folder:
            self.current_folder = folder
            self.folder_label.setText(folder)
            self.folder_selected.emit(folder)

    def set_files(self, files: list):
        """
        设置文件列表
        
        清空现有列表并显示传入的文件，文件按名称排序
        
        Args:
            files: 文件路径列表
        """
        self.file_list.clear()
        self.file_paths.clear()
        
        sorted_files = sorted(files, key=lambda x: os.path.basename(x))
        
        for filepath in sorted_files:
            item = QListWidgetItem(os.path.basename(filepath))
            item.setData(Qt.ItemDataRole.UserRole, filepath)
            self.file_list.addItem(item)
            self.file_paths[filepath] = filepath
        
        self.count_label.setText(f"{len(files)} {t('files')}")

    def _on_selection_changed(self):
        """
        文件选中状态变化处理
        
        当用户选择或取消选择文件时，获取当前选中文件列表并发射信号
        """
        selected_files = self._get_selected_files()
        self.files_selected.emit(selected_files)

    def _get_selected_files(self) -> list:
        """
        获取选中的文件路径
        
        Returns:
            选中文件的完整路径列表
        """
        selected_items = self.file_list.selectedItems()
        return [item.data(Qt.ItemDataRole.UserRole) or item.text() for item in selected_items]

    def get_selected_files(self) -> list:
        """
        公开方法：获取选中文件
        
        Returns:
            选中文件的完整路径列表
        """
        return self._get_selected_files()

    def get_selected_file(self) -> str:
        """
        获取单个选中文件
        
        如果选中多个文件，返回第一个
        
        Returns:
            选中文件的完整路径，未选中则返回空字符串
        """
        selected = self._get_selected_files()
        return selected[0] if selected else ""

    def clear(self):
        """
        清空文件列表和状态
        """
        self.file_list.clear()
        self.file_paths.clear()
        self.count_label.setText("0 files")
