"""
Canvas on which to display the image
"""

from PyQt5.QtWidgets import QVBoxLayout

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from QuickSeg.view.panel import Panel


matplotlib.use('Qt5Agg')


class Canvas(FigureCanvasQTAgg):

    def __init__(self, width=5, height=4, dpi=100):

        # Create axes
        self._axes = plt.axes()

        # Get figure underlying axes
        self._fig = self._axes.get_figure()

        # self._fig.set_size_inches(width, height)
        # self._fig.set_dpi(dpi)

        # Set background color to black
        self._fig.set_facecolor('black')

        self._border = None

        # Initialize canvas to figure
        super().__init__(self._fig)

    def get_fig(self):

        return self._fig

    def get_axes(self):

        return self._axes

    def add_border(self):

        pad_factor = 0.01
        linewidth = 1

        bbox = self._axes.get_tightbbox(
            self._fig.canvas.get_renderer())

        x_0, y_0, width, height = \
            bbox.transformed(
                self._fig.transFigure.inverted()).bounds

        xpad, ypad = pad_factor*width, pad_factor*height

        if self._border is not None:
            self._border.remove()

        self._border = patches.Rectangle(
            (x_0 - xpad, y_0 - ypad),
            width + 2*xpad,
            height + 2*ypad,
            linewidth=linewidth,
            edgecolor=[0.7, 0.0, 0.0],
            facecolor='none')

        self._fig.add_artist(self._border)


class DisplayArea(Panel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._canvas = Canvas()

        layout = QVBoxLayout()
        layout.addWidget(self._canvas)

        self.setLayout(layout)

    def get_fig(self):

        return self._canvas.get_fig()

    def get_axes(self):

        return self._canvas.get_axes()

    def refresh_canvas(self):

        self._canvas.draw()

    def add_border(self):

        self._canvas.add_border()
