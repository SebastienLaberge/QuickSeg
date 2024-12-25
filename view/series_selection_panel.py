"""
View for the series selection panel
"""

from functools import partial
from typing import Callable, Optional, Sequence, Tuple

from PyQt5.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget)

from QuickSeg.view.color_patch import ColorPatch
from QuickSeg.view.panel import Panel


COLOR_LOADED_SERIES = 'rgb(0, 255, 0)'
COLOR_NON_LOADED_SERIES = 'rgb(255, 255, 0)'


class SeriesSelectionPanel(Panel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.open_dicom_dir_button = \
            QPushButton("Open DICOM dir.")
        self.save_dir_content_button = \
            QPushButton("Save dir. content")
        self.load_dir_content_button = \
            QPushButton("Load dir. content")

        series_io_layout = QGridLayout()
        series_io_layout.\
            addWidget(self.open_dicom_dir_button, 0, 0)
        series_io_layout.\
            addWidget(self.save_dir_content_button, 0, 1)
        series_io_layout.\
            addWidget(self.load_dir_content_button, 1, 1)

        series_io_panel = Panel()
        series_io_panel.setLayout(series_io_layout)

        self.series_list = QListWidget()

        layout = QVBoxLayout(self)
        layout.addWidget(series_io_panel)
        layout.addWidget(self.series_list)

        self.setLayout(layout)

        # List for easy retrieval of color patches
        self.color_patch_list = []

    def get_current_series_index(self) -> Optional[int]:

        current_row = self.series_list.currentRow()

        return current_row if current_row != -1 else None

    def set_series_list(
            self,
            series_info_list: Sequence[Tuple[str, bool]],
            slot_delete_series: Callable):

        self.series_list.clear()
        self.color_patch_list.clear()

        for series_index, (series_name, series_loaded) in \
                enumerate(series_info_list):

            seg_name_text = QLabel(series_name)

            series_loaded_patch = ColorPatch(
                COLOR_LOADED_SERIES if series_loaded else
                COLOR_NON_LOADED_SERIES)
            series_loaded_patch.setFixedSize(20, 20)
            self.color_patch_list.append(series_loaded_patch)

            delete_series_button = QPushButton("X")
            delete_series_button.clicked.connect(
                partial(slot_delete_series, series_index))
            delete_series_button.setFixedSize(20, 20)

            item_layout = QHBoxLayout()
            item_layout.addWidget(seg_name_text)
            item_layout.addWidget(series_loaded_patch)
            item_layout.addWidget(delete_series_button)

            item_widget = QWidget()
            item_widget.setLayout(item_layout)

            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())

            self.series_list.addItem(item)
            self.series_list.setItemWidget(item, item_widget)

    def set_series_to_loaded(self, series_index: int):

        assert 0 <= series_index < len(self.color_patch_list)

        self.color_patch_list[series_index].\
            set_color(COLOR_LOADED_SERIES)
