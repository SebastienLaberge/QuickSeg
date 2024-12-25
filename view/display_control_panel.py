"""
View for the display control panel
"""

from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout

from QuickSeg.view.display_window_control import \
    DisplayWindowControl
from QuickSeg.view.navigation_panel import NavigationPanel
from QuickSeg.view.orientation_panel import OrientationPanel
from QuickSeg.view.panel import Panel
from QuickSeg.view.zoom_panel import ZoomPanel


# TODO
# [DONE] 1) Change slice
# [DONE] 2) Change frame if applicable
# [DONE] 3) Change display window
# 4) Zoom
# 5) Display SAR with given interval
# 6) Disable panel when there are no selected series
# 7) Disable frame navigation for volumes with no timestamps
# 8) Display timestamp


class DisplayControlPanel(Panel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.slice_navigation = NavigationPanel("Slice")
        self.frame_navigation = NavigationPanel("Frame")
        self.orientation_panel = OrientationPanel()
        self.zoom_panel = ZoomPanel()
        self.display_window = DisplayWindowControl()

        navigation_layout = QVBoxLayout()
        navigation_layout.addWidget(self.slice_navigation)
        navigation_layout.addWidget(self.frame_navigation)

        orientation_and_zoom_layout = QVBoxLayout()
        orientation_and_zoom_layout.addWidget(
            self.orientation_panel)
        orientation_and_zoom_layout.addWidget(
            self.zoom_panel)

        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.addLayout(navigation_layout)
        layout.addLayout(orientation_and_zoom_layout)
        layout.addWidget(self.display_window)

        self.setLayout(layout)
