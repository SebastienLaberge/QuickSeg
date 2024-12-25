"""
View for the orientation panel
"""

from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel)

from QuickSeg.view.panel import Panel


class OrientationPanel(Panel):

    def __init__(self):
        super().__init__()

        orientation_label = QLabel("Orientation: ")
        self.orientation_combobox = QComboBox()

        self._orientations = ['Axial', 'Coronal', 'Sagittal']
        self.orientation_combobox.addItems(self._orientations)

        orientation_label.setFixedWidth(70)

        orientation_panel_layout = QHBoxLayout()
        orientation_panel_layout.addWidget(orientation_label)
        orientation_panel_layout.addWidget(
            self.orientation_combobox)

        self.setLayout(orientation_panel_layout)

    def get_current_orientation(self) -> str:

        current_orientation_index = \
            self.orientation_combobox.currentIndex()

        return self._orientations[current_orientation_index]
