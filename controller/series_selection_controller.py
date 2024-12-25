"""
Controller for selecting a series to display
"""

from functools import partial
from os import getcwd

from PyQt5.QtWidgets import QFileDialog

from QuickSeg.model.model import Model

from QuickSeg.view.popups import \
    warning_popup
from QuickSeg.view.series_selection_panel import \
    SeriesSelectionPanel

from QuickSeg.controller.display_controller import \
    DisplayController
from QuickSeg.controller.seg_selection_controller import \
    SegSelectionController


# TODO: Make same change here as in seg_selection_controller
DEFAULT_DIRECTORY = getcwd()


class SeriesSelectionController:

    def __init__(self,
                 model: Model,
                 series_selection_panel: SeriesSelectionPanel,
                 seg_selection_controller: SegSelectionController,
                 display_controller: DisplayController):

        self._model = model
        self._series_selection_panel = series_selection_panel
        self._seg_selection_controller = seg_selection_controller
        self._display_controller = display_controller

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):

        self._series_selection_panel.open_dicom_dir_button.\
            clicked.connect(partial(self._slot_open_dicom_dir))

        self._series_selection_panel.save_dir_content_button.\
            clicked.connect(partial(self._slot_save_dir_content))

        self._series_selection_panel.load_dir_content_button.\
            clicked.connect(partial(self._slot_load_dir_content))

        self._series_selection_panel.series_list.\
            currentRowChanged.connect(self._slot_series_list)

    def _slot_open_dicom_dir(self, _):

        dicom_dir_path = QFileDialog.getExistingDirectory(
            None,
            "Open DICOM directory",
            DEFAULT_DIRECTORY)

        if dicom_dir_path:
            self._model.read_dicom_dir(dicom_dir_path)
            self._refresh_series_list()
            self._display_controller.refresh_image()

    def _slot_save_dir_content(self, _):

        if not self._model.dicom_dir_is_loaded():

            warning_popup("No dicom directory is loaded")
            return

        # TODO: Make sure the file has the right extension
        content_file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Save DICOM directory content",
            DEFAULT_DIRECTORY,
            "DICOM directory content (*.dir)")

        if content_file_path:
            self._model.save_dir_content(content_file_path)

    def _slot_load_dir_content(self, _):

        content_file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Load DICOM directory content file",
            DEFAULT_DIRECTORY,
            "DICOM directory content (*.dir)")

        if content_file_path:
            self._model.load_dicom_dir_content(content_file_path)
            self._refresh_series_list()

    def _slot_series_list(self, series_index):

        if series_index == -1:
            return

        self._display_controller.update_series()
        self._seg_selection_controller.refresh_seg_list()
        if not self._seg_selection_controller.restore_seg():
            self._display_controller.refresh_image()

        self._series_selection_panel.set_series_to_loaded(
            series_index)

    def _slot_delete_series(self, series_index, _):

        self._model.delete_series(series_index)

        self._refresh_series_list()
        self._display_controller.refresh_image()

    def _refresh_series_list(self):

        series_info = self._model.get_series_info()

        self._series_selection_panel.set_series_list(
            series_info,
            self._slot_delete_series)

        self._seg_selection_controller.refresh_seg_list()
