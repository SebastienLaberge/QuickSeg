"""
Main application view
"""

from PyQt5.QtWidgets import QGridLayout, QMainWindow, QWidget

from QuickSeg.view.display_area import \
    DisplayArea
from QuickSeg.view.display_control_panel import \
    DisplayControlPanel
from QuickSeg.view.seg_algos_panel import \
    SegmentationAlgorithmsPanel
from QuickSeg.view.seg_selection_panel import \
    SegmentationSelectionPanel
from QuickSeg.view.seg_tools_panel import \
    SegmentationToolsPanel
from QuickSeg.view.series_selection_panel import \
    SeriesSelectionPanel


class MainView(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Main window name
        self.setWindowTitle("QuickSeg")

        # Instantiate panels
        self.display_area = DisplayArea()
        self.display_control_panel = DisplayControlPanel()
        self.series_selection_panel = SeriesSelectionPanel()
        self.seg_selection_panel = SegmentationSelectionPanel()
        self.seg_algos_panel = SegmentationAlgorithmsPanel()
        self.seg_tools_panel = SegmentationToolsPanel()

        # Panel layout
        central_layout = QGridLayout()
        central_layout.addWidget(
            self.display_area,
            0, 0, 5, 6)
        central_layout.addWidget(
            self.display_control_panel,
            5, 0, 1, 6)
        central_layout.addWidget(
            self.series_selection_panel,
            0, 6, 4, 2)
        central_layout.addWidget(
            self.seg_selection_panel,
            0, 8, 4, 2)
        central_layout.addWidget(
            self.seg_algos_panel,
            4, 6, 2, 2)
        central_layout.addWidget(
            self.seg_tools_panel,
            4, 8, 2, 2)

        central_widget = QWidget(self)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)
