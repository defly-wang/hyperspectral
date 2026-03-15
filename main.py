"""
高光谱数据处理系统 - 主程序入口
Hyperspectral Data Processing System - Main Entry Point
"""

import sys
# PyQt6 GUI框架，用于创建桌面应用程序
from PyQt6.QtWidgets import QApplication
# 导入主窗口类
from src.ui.main_window import MainWindow


def main():
    """
    主函数 - 应用程序入口点
    1. 创建QApplication实例
    2. 设置应用程序样式
    3. 创建并显示主窗口
    4. 启动事件循环
    """
    # 创建Qt应用程序实例
    app = QApplication(sys.argv)
    # 设置Fusion样式（跨平台的现代风格）
    app.setStyle("Fusion")
    
    # 创建主窗口实例
    window = MainWindow()
    # 显示主窗口
    window.show()
    
    # 启动应用程序事件循环，程序退出时返回退出码
    sys.exit(app.exec())


if __name__ == "__main__":
    # 程序入口点
    main()
