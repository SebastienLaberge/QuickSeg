"""
View for the zoom panel
"""

from QuickSeg.view.panel import Panel

from PyQt5.QtWidgets import (
    QHBoxLayout,
    QPushButton)


class ZoomPanel(Panel):

    def __init__(self):
        super().__init__()

        self.select_region_button = QPushButton("Select region")
        self.zoom_out_button = QPushButton("Zoom out")

        self.select_region_button.setFixedWidth(90)
        self.zoom_out_button.setFixedWidth(90)

        zoom_panel_layout = QHBoxLayout()
        zoom_panel_layout.addWidget(self.select_region_button)
        zoom_panel_layout.addWidget(self.zoom_out_button)

        self.setLayout(zoom_panel_layout)
