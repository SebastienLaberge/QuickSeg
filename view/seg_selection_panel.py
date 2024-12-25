"""
View for the segmentation selection panel
"""

from functools import partial
from typing import Sequence, Optional, Callable

from PyQt5.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget)

from QuickSeg.view.panel import Panel


class SegmentationSelectionPanel(Panel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.new_seg_button = QPushButton("New seg.")
        self.save_seg_file_button = QPushButton("Save seg. file")
        self.load_seg_file_button = QPushButton("Load seg. file")

        seg_io_layout = QGridLayout()
        seg_io_layout.addWidget(
            self.new_seg_button,
            0, 0)
        seg_io_layout.addWidget(
            self.save_seg_file_button,
            0, 1)
        seg_io_layout.addWidget(
            self.load_seg_file_button,
            1, 1)

        seg_io_panel = Panel()
        seg_io_panel.setLayout(seg_io_layout)

        self.seg_list = QListWidget()

        layout = QVBoxLayout(self)
        layout.addWidget(seg_io_panel)
        layout.addWidget(self.seg_list)

        self.setLayout(layout)

    def get_current_seg_index(self) -> Optional[int]:

        current_row = self.seg_list.currentRow()

        return current_row if current_row != -1 else None

    def set_current_seg(self, seg_index: int):

        self.seg_list.setCurrentRow(seg_index)

    def set_seg_list(self,
                     seg_name_list: Sequence[str],
                     slot_delete_seg: Callable):

        self.seg_list.clear()

        for seg_index, seg_name in enumerate(seg_name_list):

            seg_name_text = QLabel(seg_name)

            delete_seg_button = QPushButton("X")
            delete_seg_button.clicked.connect(
                partial(slot_delete_seg, seg_index))
            delete_seg_button.setFixedSize(20, 20)

            item_layout = QHBoxLayout()
            item_layout.addWidget(seg_name_text)
            item_layout.addWidget(delete_seg_button)

            item_widget = QWidget()
            item_widget.setLayout(item_layout)

            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())

            self.seg_list.addItem(item)
            self.seg_list.setItemWidget(item, item_widget)
