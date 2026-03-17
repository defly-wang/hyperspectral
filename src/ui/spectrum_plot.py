from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.legend import Legend
import numpy as np
import matplotlib.pyplot as plt


class SpectrumPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.axes: Axes = self.figure.add_subplot(111)
        self.selected_lines = set()
        self.legend = None
        self.original_colors = {}
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        
        self._setup_axes()
        self._connect_events()

    def _setup_axes(self):
        self.axes.set_xlabel('Wavelength (nm)')
        self.axes.set_ylabel('Intensity')
        self.axes.grid(True, alpha=0.3)
        self.figure.tight_layout()

    def _connect_events(self):
        self.canvas.mpl_connect('pick_event', self._on_pick)
        self.canvas.mpl_connect('button_press_event', self._on_click)

    def _on_pick(self, event):
        if isinstance(event.artist, Line2D):
            line = event.artist
            self._toggle_selection(line)

    def _on_click(self, event):
        if event.inaxes != self.axes:
            return
        
        if event.button == 1 and event.xdata is not None:
            clicked_on_line = False
            for line in self.axes.get_lines():
                if line.contains(event)[0]:
                    clicked_on_line = True
                    break
            
            if not clicked_on_line:
                pass

    def _toggle_selection(self, line):
        if line in self.selected_lines:
            self.selected_lines.discard(line)
            self._restore_line_style(line)
        else:
            self.selected_lines.add(line)
            self._highlight_line(line)
        
        self._update_legend()
        self._dim_unselected_lines()
        self.canvas.draw()

    def _highlight_line(self, line):
        color = line.get_color()
        line.set_linewidth(2.5)
        line.set_alpha(1.0)
        self.original_colors[line] = {'color': color, 'linewidth': line.get_linewidth(), 'alpha': line.get_alpha()}

    def _restore_line_style(self, line):
        if line in self.original_colors:
            orig = self.original_colors[line]
            line.set_linewidth(0.5)
            line.set_alpha(0.3)
        else:
            line.set_linewidth(0.5)
            line.set_alpha(0.3)

    def _dim_unselected_lines(self):
        for line in self.axes.get_lines():
            if line not in self.selected_lines:
                if line not in self.original_colors:
                    self.original_colors[line] = {
                        'color': line.get_color(),
                        'linewidth': line.get_linewidth(),
                        'alpha': line.get_alpha()
                    }
                line.set_linewidth(0.5)
                line.set_alpha(0.3)

    def _update_legend(self):
        if self.legend is None:
            return
        
        legend_lines = self.legend.get_lines()
        for leg_line, ax_line in zip(legend_lines, self.axes.get_lines()):
            if ax_line in self.selected_lines:
                leg_line.set_linewidth(3)
                leg_line.set_alpha(1.0)
            else:
                leg_line.set_linewidth(0.5)
                leg_line.set_alpha(0.3)

    def plot_spectrum(self, wavelengths: np.ndarray, intensities: np.ndarray, 
                      title: str = "Spectrum", color: str = 'blue', show_original: bool = False,
                      original_intensities: np.ndarray = None):
        self.axes.clear()
        self._setup_axes()
        self.selected_lines = set()
        self.original_colors = {}
        
        self.axes.plot(wavelengths, intensities, color=color, linewidth=1, label='Processed', picker=True)
        
        if show_original and original_intensities is not None:
            self.axes.plot(wavelengths, original_intensities, color='gray', 
                          linewidth=0.5, alpha=0.5, label='Original', picker=True)
        
        self.legend = self.axes.legend()
        self.legend.set_draggable(True)
        
        self.axes.set_title(title)
        self.canvas.draw()

    def plot_multiple_spectra(self, spectra: list, title: str = "Spectra"):
        self.axes.clear()
        self._setup_axes()
        self.selected_lines = set()
        self.original_colors = {}
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(spectra)))
        
        for i, (wavelengths, intensities, name) in enumerate(spectra):
            line, = self.axes.plot(wavelengths, intensities, color=colors[i], 
                          linewidth=1, label=name, picker=True, pickradius=5)
        
        self.legend = self.axes.legend()
        self.legend.set_draggable(True)
        
        self.axes.set_title(title)
        self.canvas.draw()

    def clear(self):
        self.axes.clear()
        self._setup_axes()
        self.selected_lines = set()
        self.original_colors = {}
        self.legend = None
        self.canvas.draw()

    def set_xlabel(self, label: str):
        self.axes.set_xlabel(label)
        self.canvas.draw()

    def set_ylabel(self, label: str):
        self.axes.set_ylabel(label)
        self.canvas.draw()
