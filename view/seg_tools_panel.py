"""
View for the segmentation tools panel
"""

from PyQt5.QtWidgets import (
    QGridLayout,
    QPushButton,
    QVBoxLayout)

from QuickSeg.view.panel import Panel


# TODO
# 1) Additive lasso (add area)
# 2) Subtractive lasso (remove area)
# 3) Additive brush (brush)
# 4) Subtractive brush (eraser)


class SegmentationToolsPanel(Panel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_area_button = QPushButton("Add area")
        self.remove_area_button = QPushButton("Remove area")
        self.brush_button = QPushButton("Brush")
        self.eraser_button = QPushButton("Eraser")

        seg_tools_layout = QGridLayout()
        seg_tools_layout.addWidget(
            self.add_area_button,
            0, 0)
        seg_tools_layout.addWidget(
            self.remove_area_button,
            0, 1)
        seg_tools_layout.addWidget(
            self.brush_button,
            1, 0)
        seg_tools_layout.addWidget(
            self.eraser_button,
            1, 1)

        layout = QVBoxLayout(self)
        layout.addLayout(seg_tools_layout)
        layout.addStretch()

        self.setLayout(layout)
