"""
Controller for selecting an image orientation
"""

from typing import Callable

from QuickSeg.view.orientation_panel import OrientationPanel


class OrientationController:

    def __init__(self,
                 orientation_panel: OrientationPanel,
                 update_series: Callable,
                 refresh_image: Callable):

        self._orientation_panel = orientation_panel
        self._update_series = update_series
        self._refresh_image = refresh_image

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):

        self._orientation_panel.orientation_combobox.\
            currentIndexChanged.connect(
                self._slot_change_orientation)

    def _slot_change_orientation(self):

        self._update_series(False)
        self._refresh_image()

    def get_current_orientation(self) -> str:

        return self._orientation_panel.get_current_orientation()
