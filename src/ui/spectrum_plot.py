"""
光谱绘图组件

使用Matplotlib绘制光谱图，支持单光谱和多光谱显示，可交互选择高亮线条

主要功能:
    - 绘制单条光谱曲线
    - 绘制多条光谱曲线（不同颜色）
    - 交互式选择光谱线，高亮显示
    - 可拖拽图例

用法:
    plot = SpectrumPlotWidget()
    plot.plot_spectrum(wavelengths, intensities, title="Spectrum")
    plot.plot_multiple_spectra(spectra_list)
    plot.clear()
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.legend import Legend
import numpy as np
import matplotlib.pyplot as plt


class SpectrumPlotWidget(QWidget):
    """
    光谱绘图widget
    
    使用Matplotlib显示光谱曲线图，支持交互式选择高亮
    """
    
    def __init__(self, parent=None):
        """
        初始化光谱绘图组件
        
        Args:
            parent: 父widget
        """
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
        """设置坐标轴标签和网格"""
        self.axes.set_xlabel('Wavelength (nm)')
        self.axes.set_ylabel('Intensity')
        self.axes.grid(True, alpha=0.3)
        self.figure.tight_layout()

    def _connect_events(self):
        """连接Matplotlib事件"""
        self.canvas.mpl_connect('pick_event', self._on_pick)
        self.canvas.mpl_connect('button_press_event', self._on_click)

    def _on_pick(self, event):
        """
        处理pick事件（点击图线）
        
        Args:
            event: pick事件对象
        """
        if isinstance(event.artist, Line2D):
            line = event.artist
            self._toggle_selection(line)

    def _on_click(self, event):
        """
        处理鼠标点击事件
        
        Args:
            event: 鼠标事件对象
        """
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
        """
        切换线条选中状态
        
        Args:
            line: matplotlib Line2D对象
        """
        if line in self.selected_lines:
            self.selected_lines.discard(line)
            self._restore_line_style(line)
        else:
            self.selected_lines.add(line)
            self._highlight_line(line)
        
        self._update_legend()
        self.canvas.draw()

    def _highlight_line(self, line):
        """
        高亮选中的线条
        
        Args:
            line: matplotlib Line2D对象
        """
        color = line.get_color()
        self.original_colors[line] = {'color': color, 'linewidth': line.get_linewidth(), 'alpha': line.get_alpha()}
        line.set_linewidth(2.5)
        line.set_alpha(1.0)

    def _restore_line_style(self, line):
        """
        恢复线条原始样式
        
        Args:
            line: matplotlib Line2D对象
        """
        if line in self.original_colors:
            orig = self.original_colors[line]
            line.set_linewidth(orig['linewidth'])
            line.set_alpha(orig['alpha'])

    def _update_legend(self):
        """更新图例样式以匹配选中的线条"""
        if self.legend is None:
            return
        
        legend_lines = self.legend.get_lines()
        for leg_line, ax_line in zip(legend_lines, self.axes.get_lines()):
            if ax_line in self.selected_lines:
                leg_line.set_linewidth(3)
                leg_line.set_alpha(1.0)
            else:
                orig = self.original_colors.get(ax_line)
                if orig:
                    leg_line.set_linewidth(orig['linewidth'])
                    leg_line.set_alpha(orig['alpha'])

    def plot_spectrum(self, wavelengths: np.ndarray, intensities: np.ndarray, 
                      title: str = "Spectrum", color: str = 'blue', show_original: bool = False,
                      original_intensities: np.ndarray = None):
        """
        绘制单条光谱
        
        Args:
            wavelengths: 波长数组
            intensities: 强度数组
            title: 图表标题
            color: 线条颜色
            show_original: 是否显示原始光谱
            original_intensities: 原始强度数组（预处理前）
        """
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
        """
        绘制多条光谱
        
        Args:
            spectra: 光谱列表，每项为(wavelengths, intensities, name)元组
            title: 图表标题
        """
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
        """清空图表"""
        self.axes.clear()
        self._setup_axes()
        self.selected_lines = set()
        self.original_colors = {}
        self.legend = None
        self.canvas.draw()

    def set_xlabel(self, label: str):
        """
        设置X轴标签
        
        Args:
            label: X轴标签文本
        """
        self.axes.set_xlabel(label)
        self.canvas.draw()

    def add_spectrum(self, wavelengths: np.ndarray, intensities: np.ndarray, 
                     name: str = "Spectrum", color: str = None):
        """
        添加一条光谱到当前图表
        
        Args:
            wavelengths: 波长数组
            intensities: 强度数组
            name: 光谱名称
            color: 线条颜色(可选)
        """
        if color is None:
            num_lines = len(self.axes.get_lines())
            colors = plt.cm.tab10(np.linspace(0, 1, 10))
            color = colors[num_lines % 10]
        
        line, = self.axes.plot(wavelengths, intensities, color=color, 
                      linewidth=1, label=name, picker=True, pickradius=5)
        
        self.legend = self.axes.legend()
        self.legend.set_draggable(True)
        
        self.canvas.draw()

    def set_ylabel(self, label: str):
        """
        设置Y轴标签
        
        Args:
            label: Y轴标签文本
        """
        self.axes.set_ylabel(label)
        self.canvas.draw()
