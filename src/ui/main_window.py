from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QTabWidget, QStatusBar, QMenuBar, 
                             QMenu, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import os

from .preview_panel import PreviewPanel
from .training_panel import TrainingPanel
from .recognition_panel import RecognitionPanel
from .data_cleaning_panel import DataCleaningPanel
from .data_split_panel import DataSplitPanel
from ..core.i18n import t, set_language, LanguageManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle(t("window_title"))
        self.setMinimumSize(1200, 800)
        
        self._create_menu_bar()
        self._create_ui()
        self._connect_signals()
        
        self.statusBar().showMessage(t("ready"))

    def _create_menu_bar(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu(t("file"))
        
        open_action = QAction(t("open_folder"), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_folder)
        
        exit_action = QAction(t("exit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        view_menu = menubar.addMenu(t("view"))
        
        reset_action = QAction(t("reset_view"), self)
        reset_action.triggered.connect(self._reset_view)
        
        view_menu.addAction(reset_action)
        
        data_menu = menubar.addMenu(t("data_menu"))
        
        cleaning_action = QAction(t("data_cleaning"), self)
        cleaning_action.triggered.connect(self._show_cleaning_panel)
        
        split_action = QAction(t("data_split"), self)
        split_action.triggered.connect(self._show_split_panel)
        
        data_menu.addAction(cleaning_action)
        data_menu.addAction(split_action)
        
        lang_menu = menubar.addMenu(t("language"))
        
        zh_action = QAction("中文", self)
        zh_action.triggered.connect(lambda: self._change_language("zh_CN"))
        lang_menu.addAction(zh_action)
        
        en_action = QAction("English", self)
        en_action.triggered.connect(lambda: self._change_language("en_US"))
        lang_menu.addAction(en_action)
        
        model_menu = menubar.addMenu(t("model"))
        
        train_action = QAction(t("train_model"), self)
        train_action.setShortcut("Ctrl+T")
        train_action.triggered.connect(self._show_training_panel)
        
        load_model_action = QAction(t("load_model"), self)
        load_model_action.setShortcut("Ctrl+M")
        load_model_action.triggered.connect(self._load_model)
        
        recognize_action = QAction(t("recognition"), self)
        recognize_action.setShortcut("Ctrl+R")
        recognize_action.triggered.connect(self._show_recognition_panel)
        
        model_menu.addAction(train_action)
        model_menu.addAction(load_model_action)
        model_menu.addAction(recognize_action)
        
        help_menu = menubar.addMenu(t("help"))
        
        about_action = QAction(t("about"), self)
        about_action.triggered.connect(self._show_about)
        
        help_menu.addAction(about_action)

    def _create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        self.tab_widget = QTabWidget()
        
        self.preview_panel = PreviewPanel()
        
        self.training_panel = TrainingPanel()
        self.recognition_panel = RecognitionPanel()
        self.data_cleaning_panel = DataCleaningPanel()
        self.data_split_panel = DataSplitPanel()
        
        self.tab_widget.addTab(self.preview_panel, t("preview"))
        self.tab_widget.addTab(self.data_cleaning_panel, t("data_cleaning"))
        self.tab_widget.addTab(self.data_split_panel, t("data_split"))
        self.tab_widget.addTab(self.training_panel, t("model_training"))
        self.tab_widget.addTab(self.recognition_panel, t("recognition_tab"))
        
        main_layout.addWidget(self.tab_widget)

    def _change_language(self, lang: str):
        set_language(lang)
        self._refresh_ui()
    
    def _refresh_ui(self):
        self.setWindowTitle(t("window_title"))
        self.statusBar().showMessage(t("ready"))
        
        self.menuBar().clear()
        self._create_menu_bar()
        
        current_index = self.tab_widget.currentIndex()
        self.tab_widget.setTabText(0, t("preview"))
        self.tab_widget.setTabText(1, t("data_split"))
        self.tab_widget.setTabText(2, t("data_cleaning"))
        self.tab_widget.setTabText(3, t("model_training"))
        self.tab_widget.setTabText(4, t("recognition_tab"))
        self.tab_widget.setCurrentIndex(current_index)
        
        self.preview_panel.refresh_text()
        self.data_split_panel.refresh_text()
        self.data_cleaning_panel.refresh_text()
        self.training_panel.refresh_text()
        self.recognition_panel.refresh_text()

    def _connect_signals(self):
        pass

    def _open_folder(self):
        self.tab_widget.setCurrentIndex(0)
        self.preview_panel.file_browser._open_folder()

    def _reset_view(self):
        self.preview_panel.clear()

    def _show_cleaning_panel(self):
        self.tab_widget.setCurrentIndex(1)

    def _show_split_panel(self):
        self.tab_widget.setCurrentIndex(2)

    def _show_training_panel(self):
        self.tab_widget.setCurrentIndex(3)

    def _show_recognition_panel(self):
        self.tab_widget.setCurrentIndex(4)
    
    def _load_model(self):
        from PyQt6.QtWidgets import QFileDialog
        import os
        
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Model File", "", 
            "Pickle Files (*.pkl)"
        )
        
        if filepath and os.path.exists(filepath):
            self.recognition_panel.load_model_from_path(filepath)
            self._show_recognition_panel()

    def _show_about(self):
        QMessageBox.about(
            self, 
            t("about_title"),
            f"{t('window_title')}\n\n"
            f"{t('about_description')}\n\n"
            f"{t('supported_format')}"
        )
