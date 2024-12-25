"""
View for the segmentation algorithms panel
"""

from QuickSeg.view.panel import Panel


# TODO
# 1) Select algorithm
# 2) Select parameters
#   -> SUV vs SAR + frame selection
#   -> Threshold selection
#   -> Morphological operations + Kernel size
#   -> Selected point (load or click)
# 3) Button to generate segmentation
# 4) Button to project segmentation on another modality


class SegmentationAlgorithmsPanel(Panel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
