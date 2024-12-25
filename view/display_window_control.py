"""
View for the display window control
"""

from typing import Optional, Sequence, Tuple

from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout)

from QuickSeg.view.panel import Panel


class DisplayWindowControl(Panel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        window_label = QLabel("Window: ")
        window_center_label = QLabel("Center: ")
        window_width_label = QLabel("Width: ")

        self.window_combobox = QComboBox()
        self.window_center_edit = QLineEdit()
        self.window_width_edit = QLineEdit()

        window_label.setFixedWidth(50)
        window_center_label.setFixedWidth(40)
        window_width_label.setFixedWidth(40)

        self.window_center_edit.setFixedWidth(55)
        self.window_width_edit.setFixedWidth(55)

        self.window_center_edit.setReadOnly(True)
        self.window_width_edit.setReadOnly(True)

        window_combobox_layout = QHBoxLayout()
        window_combobox_layout.addWidget(window_label)
        window_combobox_layout.addWidget(self.window_combobox)

        manual_window_layout = QHBoxLayout()
        manual_window_layout.addWidget(window_center_label)
        manual_window_layout.addWidget(self.window_center_edit)
        manual_window_layout.addWidget(window_width_label)
        manual_window_layout.addWidget(self.window_width_edit)

        display_window_layout = QVBoxLayout()
        display_window_layout.addLayout(window_combobox_layout)
        display_window_layout.addSpacing(4)
        display_window_layout.addLayout(manual_window_layout)

        self.setLayout(display_window_layout)

    def set_combobox(self,
                     explanation_list: Sequence[str],
                     window_index: int):

        self.window_combobox.clear()
        # TODO: This sends an extraneous signal. Call blockSignals
        self.window_combobox.addItems(explanation_list)
        self.window_combobox.setCurrentIndex(window_index)
        self.window_combobox.blockSignals(False)

    def set_window(self, center: float, width: float):

        self.window_center_edit.setText(f"{center:g}")
        self.window_width_edit.setText(f"{width:g}")

    def get_window(self) -> Tuple[float, float]:

        return float(self.window_center_edit.text()), \
            float(self.window_width_edit.text())

    def enable_window_editing(self, enable: bool):

        read_only = not enable
        self.window_center_edit.setReadOnly(read_only)
        self.window_width_edit.setReadOnly(read_only)
