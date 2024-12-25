"""
Controller for the display area and display controls
"""

from typing import Optional

from DicomSeriesManager.display import show
from DicomSeriesManager.reorientation import \
    get_reoriented_n_slices

from QuickSeg.model.display_window_model import DisplayWindow
from QuickSeg.model.model import Model, DisplayParameters
from QuickSeg.model.zoom_utils import (
    convert_region_to_FOV,
    Region)

from QuickSeg.view.display_area import \
    DisplayArea
from QuickSeg.view.display_control_panel import \
    DisplayControlPanel
from QuickSeg.view.seg_selection_panel import \
    SegmentationSelectionPanel
from QuickSeg.view.series_selection_panel import \
    SeriesSelectionPanel

from QuickSeg.controller.display_window_controller import \
    DisplayWindowController
from QuickSeg.controller.navigation_controller import \
    NavigationController
from QuickSeg.controller.orientation_controller import \
    OrientationController
from QuickSeg.controller.zoom_controller import \
    ZoomController


class DisplayController:

    def __init__(self,
                 model: Model,
                 series_selection_panel: SeriesSelectionPanel,
                 seg_selection_panel: SegmentationSelectionPanel,
                 display_area: DisplayArea,
                 display_control_panel: DisplayControlPanel):

        self._model = model

        # View components
        self._series_selection_panel = series_selection_panel
        self._seg_selection_panel = seg_selection_panel
        self._display_area = display_area

        # Display window controller
        self._display_window_controller = \
            DisplayWindowController(
                display_control_panel.display_window,
                display_control_panel.frame_navigation,
                self.refresh_image,
                self._set_window_index,
                self._set_manual_window)

        # Navigation controller for slice index
        self._slice_navigation_controller = \
            NavigationController(
                display_control_panel.slice_navigation,
                self._series_selection_panel,
                self.refresh_image,
                self._set_slice_index)

        # Navigation controller for frame index
        self._frame_navigation_controller = \
            NavigationController(
                display_control_panel.frame_navigation,
                self._series_selection_panel,
                self.refresh_image,
                self._set_frame_index,
                self._display_window_controller.update_window)

        # Orientation control
        self._orientation_controller = \
            OrientationController(
                display_control_panel.orientation_panel,
                self.update_series,
                self.refresh_image)

        # Zoom control
        self._zoom_controller = \
            ZoomController(
                display_control_panel.zoom_panel,
                self.refresh_image,
                self._set_FOV,
                display_area)

    def _set_slice_index(self, slice_index: int):

        display_parameters = self._get_display_parameters()

        # Get current orientation
        orientation = self._orientation_controller.\
            get_current_orientation()

        # Update slice index in model for current orientation
        display_parameters.current_slice_index[orientation] = \
            slice_index

    def _set_frame_index(self, frame_index: int):

        display_parameters = self._get_display_parameters()

        # Update frame index in model
        display_parameters.current_frame_index = frame_index

        # Update size specifier in slice navigation controller
        self._slice_navigation_controller.\
            set_size_specifier_index(frame_index)

    def _set_window_index(self, window_index: int):

        display_parameters = self._get_display_parameters()

        # Update window index in model
        display_parameters.current_window_index = window_index

    def _set_manual_window(
            self,
            manual_window: Optional[DisplayWindow]):

        display_parameters = self._get_display_parameters()

        # Update manual window in model
        display_parameters.manual_window = manual_window

    def _set_FOV(self, region: Region):

        previous_FOV = self._zoom_controller.get_current_FOV()

        series_index = \
            self._series_selection_panel.\
            get_current_series_index()

        series = self._model.goc_series(series_index)

        orientation = \
            self._orientation_controller.\
            get_current_orientation()

        FOV = convert_region_to_FOV(
            region,
            previous_FOV,
            series,
            orientation) \
            if region is not None else None

        # Update FOV in model
        display_parameters = self._get_display_parameters()
        display_parameters.current_FOV[orientation] = FOV

        # Update current FOV in controller
        self._zoom_controller.set_current_FOV(FOV)

    def _get_display_parameters(self) -> DisplayParameters:

        current_series_index = \
            self._series_selection_panel.\
            get_current_series_index()

        return self._model.get_display_parameters(
            current_series_index)

    def update_series(self, update_window=True):
        """
        Must be called when current series is changed
        """

        # TODO: The boolean parameter is there to avoid an
        # extraneous signal being sent. Fix the problem at the
        # source and remove boolean

        current_series_index = \
            self._series_selection_panel.\
            get_current_series_index()

        series = self._model.goc_series(current_series_index)

        # Get current orientation
        orientation = self._orientation_controller.\
            get_current_orientation()

        # Get series dimensions
        n_frames = series.get_number_of_frames()
        n_slices_vector = \
            [get_reoriented_n_slices(
                series.get_vol_shape(frame_index),
                orientation)
             for frame_index in range(n_frames)]

        # Get saved display parameters for current series
        disp_params = self._model.get_display_parameters(
            current_series_index)

        # Get saved current frame for current series
        # If non-existent, defaults to last frame
        frame_index = disp_params.current_frame_index \
            if disp_params.current_frame_index is not None \
            else n_frames - 1

        # Get current slice for current series and orientation
        # If non-existent, defaults to middle slice
        slice_index = \
            disp_params.current_slice_index[orientation] \
            if orientation in disp_params.current_slice_index\
            else n_slices_vector[frame_index] // 2

        # Size specifier: Defined in such a way that:
        #     n_slices = size_specifier[1][size_specifier[0]]
        size_specifier = (frame_index, n_slices_vector)

        # Set navigation control for slice index
        self._slice_navigation_controller.\
            set_current_index(slice_index, update_window=False)
        self._slice_navigation_controller.\
            set_size_specifier(size_specifier)

        # Set navigation control for frame index
        # TODO: display_params.current_window_index is changed
        self._frame_navigation_controller.\
            set_current_index(frame_index, update_window=False)
        self._frame_navigation_controller.\
            set_size_specifier(n_frames)

        # Get saved current window for current series
        # If non-existent, defaults to the first window
        window_index = disp_params.current_window_index \
            if disp_params.current_window_index is not None \
            else 0

        # Get extracted windows
        extracted_windows = \
            self._model.get_extracted_windows(
                current_series_index)

        # Update current window
        if update_window:
            self._display_window_controller.update_series(
                series,
                extracted_windows,
                disp_params.manual_window,
                window_index)

        # Get current FOV for current series and orientation
        # If non-existent, defaults to None (widest FOV)
        FOV = disp_params.current_FOV[orientation] \
            if orientation in disp_params.current_FOV \
            else None

        # Update FOV
        self._zoom_controller.set_current_FOV(FOV)

    def get_fig(self):

        return self._display_area.get_fig()

    def get_axes(self):

        return self._display_area.get_axes()

    def refresh_image(self):

        # Get axes
        axes = self.get_axes()

        # Get index of currently selected series
        # None if no series is currently selected
        current_series_index = \
            self._series_selection_panel.\
            get_current_series_index()

        # If there is no selected series, clear image and return
        if current_series_index is None:
            axes.clear()
            axes.set_visible(False)
            self._display_area.refresh_canvas()
            return

        # Get index of current segmentation
        # None if no segmentation is currently selected
        current_seg_index = \
            self._seg_selection_panel.get_current_seg_index()

        # Get current series
        series = self._model.goc_series(current_series_index)

        # Get current segmentation (None if non-existent)
        seg = self._model.get_seg(
            current_series_index,
            current_seg_index)

        # Get current slice and frame indices
        slice_index = self._slice_navigation_controller.\
            get_current_index()
        frame_index = self._frame_navigation_controller.\
            get_current_index()

        # Get current orientation
        orientation = self._orientation_controller.\
            get_current_orientation()

        # Get current window
        window = self._display_window_controller.get_window()

        # Get current field of view
        FOV = self._zoom_controller.get_current_FOV()

        # Replace axes content with current image and seg
        axes.set_visible(True)
        show(series, axes,
             ind=slice_index,
             frame=frame_index,
             orientation=orientation,
             window=window,
             FOV=FOV,
             seg=seg)

        self._display_area.add_border()

        # Refresh canvas
        self._display_area.refresh_canvas()
