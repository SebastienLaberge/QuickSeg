"""
Controller for the selection of a display window
"""

from typing import Callable, Optional, Sequence

from DicomSeriesManager.series import BaseSeries

from QuickSeg.model.display_window_model import DisplayWindow
from QuickSeg.model.model import ExtractedWindows

from QuickSeg.view.display_window_control import \
    DisplayWindowControl
from QuickSeg.view.navigation_panel import \
    NavigationPanel


GLOBAL_WINDOW_TEXT = '> Global'
FRAME_WINDOW_TEXT = '> Frame'
MANUAL_WINDOW_TEXT = '> Manual'


class DisplayWindowController:

    def __init__(self,
                 display_window_control: DisplayWindowControl,
                 frame_navigation: NavigationPanel,
                 refresh_image: Callable,
                 on_window_index_change: Callable,
                 on_manual_window_change: Callable):

        self._display_window_control = display_window_control
        self._frame_navigation = frame_navigation

        self._refresh_image = refresh_image
        self._on_window_index_change = on_window_index_change
        self._on_manual_window_change = on_manual_window_change

        self._dicom_window_list = []
        self._global_window = None
        self._frame_window_list = None
        self._manual_window = None

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):

        self._display_window_control.window_combobox.\
            currentIndexChanged.connect(self._slot_select_window)

        self._display_window_control.window_center_edit.\
            returnPressed.connect(self._slot_window_center)

        self._display_window_control.window_width_edit.\
            returnPressed.connect(self._slot_window_width)

    def _slot_select_window(self, window_index: int):

        if window_index == -1:
            return

        self._set_window(window_index)

        self._refresh_image()

    def _slot_window_center(self):

        self._update_manual_window()

        self._refresh_image()

    def _slot_window_width(self):

        self._update_manual_window()

        self._refresh_image()

    def update_series(self,
                      series: BaseSeries,
                      extracted_windows: ExtractedWindows,
                      manual_window: Optional[DisplayWindow],
                      window_index: int):

        if extracted_windows.initialized is False:

            self._dicom_window_list = \
                DisplayWindow.extract_dicom_window_list(series)
            self._global_window, self._frame_window_list = \
                DisplayWindow.extract_tight_windows(series)

            extracted_windows.dicom_window_list = \
                self._dicom_window_list
            extracted_windows.global_window = \
                self._global_window
            extracted_windows.frame_window_list = \
                self._frame_window_list
            extracted_windows.initialized = True
        else:
            self._dicom_window_list = \
                extracted_windows.dicom_window_list
            self._global_window = \
                extracted_windows.global_window
            self._frame_window_list = \
                extracted_windows.frame_window_list

        # Set manual window (may be None)
        self._manual_window = manual_window

        explanation_list = [window.explanation for window in
                            self._dicom_window_list]

        explanation_list.append(GLOBAL_WINDOW_TEXT)
        if self._frame_window_list is not None:
            explanation_list.append(FRAME_WINDOW_TEXT)
        explanation_list.append(MANUAL_WINDOW_TEXT)

        # TODO: This triggers refresh image!
        self._display_window_control.set_combobox(
            explanation_list,
            window_index)

    # TODO: Should this be removed or repurposed?
    def _set_combobox(self,
                      explanation_list: Sequence[str],
                      window_index: int):
        """
        This would normally have been in the view, but it
        it requires a signal to be temporarily disconnected
        """

        combobox = self._display_window_control.window_combobox

        combobox.currentIndexChanged.disconnect(
            self._slot_select_window)

        combobox.clear()

        combobox.addItems(explanation_list)

        combobox.currentIndexChanged.connect(
            self._slot_select_window)

        combobox.setCurrentIndex(window_index)

    def update_window(self):

        combobox = self._display_window_control.window_combobox
        window_index = combobox.currentIndex()

        if window_index == -1:
            return

        self._set_window(window_index)

    def _set_window(self, window_index: int):

        n_dicom_windows = len(self._dicom_window_list)
        global_window_index = n_dicom_windows
        frame_windows_index = global_window_index + 1 if \
            self._frame_window_list is not None else None

        use_manual_window = False

        if window_index < n_dicom_windows:
            assert self._dicom_window_list is not None
            window = self._dicom_window_list[window_index]

        elif window_index == global_window_index:
            assert self._global_window is not None
            window = self._global_window

        elif frame_windows_index is not None and \
                window_index == frame_windows_index:
            assert self._frame_window_list is not None
            frame_index = \
                self._frame_navigation.get_current_index()
            assert frame_index is not None
            window = self._frame_window_list[frame_index]
        else:
            # Manual window
            window = self._manual_window
            use_manual_window = True

        update_window = True

        if not use_manual_window:
            assert window is not None

        elif window is None:
            # Manual window is selected but not available:
            # Keep window that is already in view
            update_window = False

        if update_window:
            self._display_window_control.set_window(
                window.center,
                window.width)

        # Enable editing if manual window is selected
        self._display_window_control.enable_window_editing(
            use_manual_window)

        self._on_window_index_change(window_index)

    def _update_manual_window(self):

        window = DisplayWindow(*self.get_window())

        self._manual_window = window
        self._on_manual_window_change(window)

    def get_window(self):

        return self._display_window_control.get_window()
