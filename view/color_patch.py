"""
Implementation of a patch showing a given color
"""

# TODO: Clean up this file

# from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget

from PyQt5.QtCore import Qt


class ColorPatch(QWidget):

    def __init__(self, color: str):

        super().__init__()

        self.setAttribute(Qt.WA_StyledBackground, True)

        # self.setAutoFillBackground(True)

        self.set_color(color)

    def set_color(self, color: str):

        style_sheet = f"""
        background-color: {color};
        border: 1px solid black;
        """
        self.setStyleSheet(style_sheet)

        # palette = self.palette()
        # palette.setColor(self.backgroundRole(), QColor(color))
        # self.setPalette(palette)
