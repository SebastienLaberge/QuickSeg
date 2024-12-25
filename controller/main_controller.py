"""
Main application controller
"""

from QuickSeg.controller.display_controller \
    import DisplayController
from QuickSeg.controller.seg_selection_controller \
    import SegSelectionController
from QuickSeg.controller.seg_tools_controller \
    import SegToolsController
from QuickSeg.controller.series_selection_controller \
    import SeriesSelectionController


class MainController:

    def __init__(self, model, view):

        self._model = model
        self._view = view

        # Sub-controllers

        self._display_controller = \
            DisplayController(
                self._model,
                self._view.series_selection_panel,
                self._view.seg_selection_panel,
                self._view.display_area,
                self._view.display_control_panel)

        self._seg_selection_controller = \
            SegSelectionController(
                self._model,
                self._view.series_selection_panel,
                self._view.seg_selection_panel,
                self._display_controller)

        self._series_selection_controller = \
            SeriesSelectionController(
                self._model,
                self._view.series_selection_panel,
                self._seg_selection_controller,
                self._display_controller)

        self._seg_tools_controller = \
            SegToolsController(
                self._model,
                self._view.seg_tools_panel,
                self._view.series_selection_panel,
                self._view.seg_selection_panel,
                self._display_controller)
