"""
Controller for using segmentation tools
"""

from DicomSeriesManager.reorientation import (
    get_reoriented_PS,
    reorient_from_axial)

from DicomSeriesManager.utils import get_slice_limits

from QuickSeg.model.lasso_utils import (
    trace_line,
    trace_line_on_mask)
from QuickSeg.model.model import Model

from QuickSeg.view.seg_selection_panel import \
    SegmentationSelectionPanel
from QuickSeg.view.seg_tools_panel import \
    SegmentationToolsPanel
from QuickSeg.view.series_selection_panel import \
    SeriesSelectionPanel

from QuickSeg.controller.display_controller import \
    DisplayController


class SegToolsController:

    def __init__(self,
                 model: Model,
                 tools_panel: SegmentationToolsPanel,
                 series_selection_panel: SeriesSelectionPanel,
                 seg_selection_panel: SegmentationSelectionPanel,
                 display_controller: DisplayController):

        self._model = model
        self._tools_panel = tools_panel
        self._series_selection_panel = series_selection_panel
        self._seg_selection_panel = seg_selection_panel
        self._display_controller = display_controller

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):

        self._tools_panel.add_area_button.\
            pressed.connect(self._add_area)

        self._tools_panel.remove_area_button.\
            pressed.connect(self._remove_area)

        self._tools_panel.brush_button.\
            pressed.connect(self._brush)

        self._tools_panel.eraser_button.\
            pressed.connect(self._eraser)

    def _add_area(self):

        self._area_tracing(add=True)

    def _remove_area(self):

        self._area_tracing(add=False)

    def _area_tracing(self, *, add):

        # Make sure there is a segmentation to work on

        current_seg_index = \
            self._seg_selection_panel.get_current_seg_index()

        if current_seg_index is None:
            return

        # Trace line

        line = trace_line(self._display_controller.get_fig())

        if line is None:
            return

        # Get segmentation slice

        series_index = \
            self._series_selection_panel.\
            get_current_series_index()

        current_seg = \
            self._model.get_seg(
                series_index,
                current_seg_index)

        orientation = \
            self._display_controller._orientation_controller.\
            get_current_orientation()

        slice_index = \
            self._display_controller.\
            _slice_navigation_controller.\
            get_current_index()

        seg_slice = reorient_from_axial(
            current_seg,
            orientation,
            slice_index)

        FOV_list = self._model.get_display_parameters(
            series_index).current_FOV

        FOV = FOV_list.get(orientation)

        series = self._model.goc_series(series_index)

        pixel_spacing = \
            get_reoriented_PS(series.get_frame(), orientation)

        if FOV is not None:

            x_range, y_range = \
                get_slice_limits(
                    FOV,
                    seg_slice.shape,
                    pixel_spacing)

            seg_slice = \
                seg_slice[y_range[0]:y_range[1]+1,
                          x_range[0]:x_range[1]+1]

        # Get mask, update seg and refresh image

        mask = trace_line_on_mask(seg_slice.shape, line)

        seg_slice[mask] = add

        self._display_controller.refresh_image()

    def _brush(self):

        self._display_controller.refresh_image()

    def _eraser(self):

        self._display_controller.refresh_image()
