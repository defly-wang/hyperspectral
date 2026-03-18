"""
图像视图组件

使用Matplotlib显示伪彩色图像，支持单图和多图显示，可交互点击查看

主要功能:
    - 显示单个伪彩色图像（将光谱数据重塑为2D图像）
    - 同时显示多个伪彩色图像（不同颜色映射）
    - 点击图像子图显示名称

用法:
    viewer = ImageViewWidget()
    viewer.show_fake_hsi_image(wavelengths, intensities, title="Spectrum")
    viewer.show_multiple_images(spectra_list)
    viewer.clear()
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backend_bases import MouseEvent
import numpy as np
import math


class ImageViewWidget(QWidget):
    """
    图像视图widget
    
    使用Matplotlib显示伪彩色图像，将光谱强度数据转换为可视化图像
    """
    
    def __init__(self, parent=None):
        """
        初始化图像视图
        
        Args:
            parent: 父widget
        """
        super().__init__(parent)
        self.figure = Figure(figsize=(6, 6))
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)
        self.spectra_list = []
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        
        self._setup_axes()
        self.canvas.mpl_connect('button_press_event', self._on_canvas_click)

    def _setup_axes(self):
        """设置坐标轴样式，隐藏坐标轴"""
        self.axes.set_axis_off()
        self.figure.tight_layout()

    def show_image(self, data: np.ndarray, title: str = "Pseudo-color Image", 
                   cmap: str = 'jet', show_colorbar: bool = True):
        """
        显示一般图像
        
        Args:
            data: 2D numpy数组
            title: 图像标题
            cmap: 颜色映射名称
            show_colorbar: 是否显示颜色条
        """
        self.axes.clear()
        
        if show_colorbar:
            im = self.axes.imshow(data, cmap=cmap, aspect='auto')
            self.figure.colorbar(im, ax=self.axes)
        else:
            self.axes.imshow(data, cmap=cmap, aspect='auto')
        
        self.axes.set_title(title)
        self.axes.set_axis_off()
        self.figure.tight_layout()
        self.canvas.draw()

    def show_fake_hsi_image(self, wavelengths: np.ndarray, intensities: np.ndarray, 
                           title: str = "Pseudo-color Composite"):
        """
        显示伪彩色高光谱图像
        
        将光谱强度数据重塑为2D图像并显示
        
        Args:
            wavelengths: 波长数组
            intensities: 强度数组
            title: 图像标题
        """
        self.figure.clear()
        self.axes = self.figure.add_subplot(111)
        
        n_points = len(intensities)
        if n_points < 3:
            self.axes.text(0.5, 0.5, 'Not enough spectral points', 
                          ha='center', va='center', transform=self.axes.transAxes)
            self.canvas.draw()
            return
        
        img_size = int(np.sqrt(n_points))
        if img_size * img_size > n_points:
            img_size = img_size - 1
        
        reshaped = intensities[:img_size*img_size].reshape(img_size, img_size)
        
        self.axes.imshow(reshaped, cmap='viridis', aspect='auto')
        self.axes.set_title(title)
        self.axes.set_axis_off()
        self.figure.tight_layout()
        self.canvas.draw()

    def show_multiple_images(self, spectra_list: list, title: str = "Pseudo-color Composite"):
        """
        显示多个伪彩色图像
        
        将多个光谱数据分别显示为伪彩色图像，使用不同颜色映射
        
        Args:
            spectra_list: 光谱列表，每项为(wavelengths, intensities, name)元组
            title: 总标题
        """
        self.figure.clear()
        self.spectra_list = spectra_list
        
        n_images = len(spectra_list)
        if n_images == 0:
            self.axes = self.figure.add_subplot(111)
            self.axes.text(0.5, 0.5, 'No data available', 
                          ha='center', va='center', transform=self.axes.transAxes)
            self.figure.tight_layout()
            self.canvas.draw()
            return
        
        cols = n_images
        rows = 1
        
        cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'twilight', 'turbo']
        
        for idx, (wavelengths, intensities, name) in enumerate(spectra_list):
            ax = self.figure.add_subplot(rows, cols, idx + 1)
            
            n_points = len(intensities)
            if n_points < 3:
                ax.text(0.5, 0.5, 'Not enough points', 
                      ha='center', va='center', transform=ax.transAxes)
                ax.set_axis_off()
                continue
            
            img_size = int(np.sqrt(n_points))
            if img_size * img_size > n_points:
                img_size = img_size - 1
            
            reshaped = intensities[:img_size*img_size].reshape(img_size, img_size)
            
            cmap = cmaps[idx % len(cmaps)]
            ax.imshow(reshaped, cmap=cmap, aspect='auto')
            ax.set_axis_off()
        
        self.figure.subplots_adjust(wspace=0, hspace=0)
        for ax in self.figure.axes:
            for spine in ax.spines.values():
                spine.set_visible(False)
        self.canvas.draw()

    def clear(self):
        """清空图像显示"""
        self.figure.clear()
        self.axes = self.figure.add_subplot(111)
        self._setup_axes()
        self.canvas.draw()

    def _on_canvas_click(self, event: MouseEvent):
        """
        处理画布点击事件
        
        点击某个子图时，在总标题显示该图像对应的文件名
        
        Args:
            event: Matplotlib鼠标事件
        """
        if event.inaxes is None or not self.spectra_list:
            return
        
        for idx, ax in enumerate(self.figure.axes):
            if ax == event.inaxes and idx < len(self.spectra_list):
                _, _, name = self.spectra_list[idx]
                self.figure.suptitle(name, fontsize=12, y=0.98)
                self.canvas.draw()
                break
