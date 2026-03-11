from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np
import matplotlib.pyplot as plt


class SpectrumPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.axes: Axes = self.figure.add_subplot(111)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        
        self._setup_axes()

    def _setup_axes(self):
        self.axes.set_xlabel('Wavelength (nm)')
        self.axes.set_ylabel('Intensity')
        self.axes.grid(True, alpha=0.3)
        self.figure.tight_layout()

    def plot_spectrum(self, wavelengths: np.ndarray, intensities: np.ndarray, 
                      title: str = "Spectrum", color: str = 'blue', show_original: bool = False,
                      original_intensities: np.ndarray = None):
        self.axes.clear()
        self._setup_axes()
        
        self.axes.plot(wavelengths, intensities, color=color, linewidth=1, label='Processed')
        
        if show_original and original_intensities is not None:
            self.axes.plot(wavelengths, original_intensities, color='gray', 
                          linewidth=0.5, alpha=0.5, label='Original')
            self.axes.legend()
        
        self.axes.set_title(title)
        self.canvas.draw()

    def plot_multiple_spectra(self, spectra: list, title: str = "Spectra"):
        self.axes.clear()
        self._setup_axes()
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(spectra)))
        
        for i, (wavelengths, intensities, name) in enumerate(spectra):
            self.axes.plot(wavelengths, intensities, color=colors[i], 
                          linewidth=1, label=name)
        
        self.axes.legend()
        self.axes.set_title(title)
        self.canvas.draw()

    def clear(self):
        self.axes.clear()
        self._setup_axes()
        self.canvas.draw()

    def set_xlabel(self, label: str):
        self.axes.set_xlabel(label)
        self.canvas.draw()

    def set_ylabel(self, label: str):
        self.axes.set_ylabel(label)
        self.canvas.draw()
