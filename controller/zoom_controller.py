"""
Controller for zooming on an image
"""

from typing import Callable, Optional

from QuickSeg.model.zoom_utils import select_region

from QuickSeg.view.display_area import DisplayArea
from QuickSeg.view.zoom_panel import ZoomPanel


class ZoomController:

    def __init__(self,
                 zoom_panel: ZoomPanel,
                 refresh_image: Callable,
                 set_FOV: Callable,
                 display_area: DisplayArea):

        self._zoom_panel = zoom_panel
        self._refresh_image = refresh_image
        self._set_FOV = set_FOV
        self._display_area = display_area

        self._current_FOV = None

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):

        self._zoom_panel.select_region_button.\
            pressed.connect(self._select_region)

        self._zoom_panel.zoom_out_button.\
            pressed.connect(self._zoom_out)

    def _select_region(self):

        region = select_region(self._display_area.get_fig())

        if region is None:
            return

        self._set_FOV(region)
        self._refresh_image()

    def _zoom_out(self):

        self._set_FOV(None)
        self._refresh_image()

    def get_current_FOV(self) -> Optional[list[float]]:

        return self._current_FOV

    def set_current_FOV(self, current_FOV: Optional[list[float]]):

        self._current_FOV = current_FOV
