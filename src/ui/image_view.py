from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import math


class ImageViewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(6, 6))
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        
        self._setup_axes()

    def _setup_axes(self):
        self.axes.set_axis_off()
        self.figure.tight_layout()

    def show_image(self, data: np.ndarray, title: str = "Pseudo-color Image", 
                   cmap: str = 'jet', show_colorbar: bool = True):
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
        self.axes.clear()
        
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
        self.figure.clear()
        
        n_images = len(spectra_list)
        if n_images == 0:
            self.axes = self.figure.add_subplot(111)
            self.axes.text(0.5, 0.5, 'No data available', 
                          ha='center', va='center', transform=self.axes.transAxes)
            self.figure.tight_layout()
            self.canvas.draw()
            return
        
        cols = math.ceil(math.sqrt(n_images))
        rows = math.ceil(n_images / cols)
        
        cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'twilight', 'turbo']
        
        for idx, (wavelengths, intensities, name) in enumerate(spectra_list):
            ax = self.figure.add_subplot(rows, cols, idx + 1)
            
            n_points = len(intensities)
            if n_points < 3:
                ax.text(0.5, 0.5, 'Not enough points', 
                      ha='center', va='center', transform=ax.transAxes)
                ax.set_title(name[:20])
                ax.set_axis_off()
                continue
            
            img_size = int(np.sqrt(n_points))
            if img_size * img_size > n_points:
                img_size = img_size - 1
            
            reshaped = intensities[:img_size*img_size].reshape(img_size, img_size)
            
            cmap = cmaps[idx % len(cmaps)]
            ax.imshow(reshaped, cmap=cmap, aspect='auto')
            ax.set_title(name[:20], fontsize=8)
            ax.set_axis_off()
        
        self.figure.tight_layout()
        self.canvas.draw()

    def clear(self):
        self.figure.clear()
        self.axes = self.figure.add_subplot(111)
        self._setup_axes()
        self.canvas.draw()