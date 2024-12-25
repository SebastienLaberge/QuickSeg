"""
Controller for selecting a segmentation to display and work on
"""

from functools import partial
from os import getcwd

from PyQt5.QtWidgets import QFileDialog

from QuickSeg.model.model import Model

from QuickSeg.view.seg_selection_panel import \
    SegmentationSelectionPanel
from QuickSeg.view.series_selection_panel import \
    SeriesSelectionPanel

from QuickSeg.controller.display_controller import \
    DisplayController


# TODO: Determine why connect isn't working when removing partial
# TODO: Find something better and keep user's choice in memory
DEFAULT_DIRECTORY = getcwd()


class SegSelectionController:

    def __init__(self,
                 model: Model,
                 series_selection_panel: SeriesSelectionPanel,
                 seg_selection_panel: SegmentationSelectionPanel,
                 display_controller: DisplayController):

        self._model = model
        self._series_selection_panel = series_selection_panel
        self._seg_selection_panel = seg_selection_panel
        self._display_controller = display_controller

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):

        self._seg_selection_panel.new_seg_button.\
            clicked.connect(partial(self._slot_new_seg))

        self._seg_selection_panel.save_seg_file_button.\
            clicked.connect(partial(self._slot_save_seg_file))

        self._seg_selection_panel.load_seg_file_button.\
            clicked.connect(partial(self._slot_load_seg_file))

        self._seg_selection_panel.seg_list.\
            currentRowChanged.connect(self._slot_seg_list)

    def _slot_new_seg(self):

        current_series_index = \
            self._series_selection_panel.\
            get_current_series_index()

        if current_series_index is None:
            # TODO: Add warning
            return

        # Todo input new seg name
        new_seg_index = \
            self._model.add_new_seg(
                "New seg",
                current_series_index)

        self.refresh_seg_list()

        self._seg_selection_panel.set_current_seg(new_seg_index)

    def _slot_save_seg_file(self):

        current_series_index = \
            self._series_selection_panel.\
            get_current_series_index()

        if current_series_index is None:
            # TODO: Add warning
            return

        current_seg_index = \
            self._seg_selection_panel.get_current_seg_index()

        if current_seg_index is None:
            # TODO: Add warning
            return

        seg_name = self._model.get_seg_name(
            current_series_index,
            current_seg_index)

        # TODO: Make sure the file has the right extension
        seg_file_path, _ = \
            QFileDialog.getSaveFileName(
                None,
                f"Save segmentation \"{seg_name}\" to file",
                DEFAULT_DIRECTORY,
                "Segmentation file (*.npy)")

        if seg_file_path:
            self._model.save_seg(
                seg_file_path,
                current_series_index,
                current_seg_index)

    def _slot_load_seg_file(self):

        current_series_index = \
            self._series_selection_panel.\
            get_current_series_index()

        if current_series_index is None:
            # TODO: Add warning
            return

        seg_file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select segmentation",
            DEFAULT_DIRECTORY,
            "Segmentation file (*.npy)")

        if seg_file_path:

            # Load segmentation
            new_seg_index = self._model.load_seg(
                seg_file_path,
                current_series_index)

            # Return if segmentation didn't load successfully
            if new_seg_index is None:
                return

            # Update view
            self.refresh_seg_list()
            self._seg_selection_panel.set_current_seg(
                new_seg_index)

    def _slot_seg_list(self, seg_index: int):

        if seg_index < 0:
            return

        current_series_index = \
            self._series_selection_panel.\
            get_current_series_index()

        # Update segmentation index in model
        display_parameters = \
            self._model.get_display_parameters(
                current_series_index)
        display_parameters.current_seg_index = seg_index

        self._display_controller.refresh_image()

    def _slot_delete_seg(self, seg_index: int):

        current_series_index = \
            self._series_selection_panel.\
            get_current_series_index()

        # Delete segmentation in model
        self._model.delete_seg(current_series_index, seg_index)

        # Clear segmentation index in model
        display_parameters = \
            self._model.get_display_parameters(
                current_series_index)
        display_parameters.current_seg_index = None

        # Update view
        self.refresh_seg_list()
        self._display_controller.refresh_image()

    def refresh_seg_list(self):

        current_series_index = \
            self._series_selection_panel.\
            get_current_series_index()

        # Get segmentation names for current series from model
        seg_names = \
            self._model.get_seg_names(current_series_index) \
            if current_series_index is not None else []

        # Repopulate segmentation list
        self._seg_selection_panel.set_seg_list(
            seg_names,
            self._slot_delete_seg)

    def restore_seg(self) -> bool:

        current_series_index = \
            self._series_selection_panel.\
            get_current_series_index()

        assert current_series_index is not None

        display_parameters = \
            self._model.get_display_parameters(
                current_series_index)

        current_seg_index = display_parameters.current_seg_index

        seg_restored = current_seg_index is not None

        if seg_restored:
            self._seg_selection_panel.seg_list.setCurrentRow(
                current_seg_index)

        return seg_restored
