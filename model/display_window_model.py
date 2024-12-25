"""
Model for representing and extracting display windows
"""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Optional, Sequence, Tuple, Self

import numpy as np

from DicomSeriesManager.series import BaseSeries


EXPLANATION_TAG = 'WindowCenterWidthExplanation'
CENTER_TAG = 'WindowCenter'
WIDTH_TAG = 'WindowWidth'


@dataclass
class DisplayWindow:

    center: float
    width: float
    explanation: Optional[str] = None

    @classmethod
    def extract_dicom_window_list(cls, series: BaseSeries) \
            -> Sequence[Self]:

        # Get first slice (on first frame if multivolume)
        exemplar = series.get_dataset(0, 0)

        explanation_index = 0

        def yield_explanation():
            while True:
                nonlocal explanation_index
                explanation_index += 1
                yield f"DICOM Window {explanation_index}"

        def make_iter(arg: Any):

            return arg if isinstance(arg, Iterable) else [arg]

        explanation_list = getattr(exemplar, EXPLANATION_TAG) \
            if hasattr(exemplar, EXPLANATION_TAG) else \
            yield_explanation()
        center_list = make_iter(getattr(exemplar, CENTER_TAG))
        width_list = make_iter(getattr(exemplar, WIDTH_TAG))

        return [cls(float(center), float(width), explanation)
                for explanation, center, width in
                zip(explanation_list, center_list, width_list)]

    @classmethod
    def extract_tight_windows(
            cls,
            series: BaseSeries) \
            -> Tuple[Self, Optional[Sequence[Self]]]:

        def get_frame_minmax(frame):

            def get_slice_minmax(ind, frame):

                dataset = series.get_dataset(ind, frame)
                pixel_array = dataset.pixel_array
                return pixel_array.min(), pixel_array.max()

            n_slices = series.get_number_of_slices(frame)
            slice_minmax_list = [get_slice_minmax(ind, frame)
                                 for ind in range(n_slices)]

            slice_min_list, slice_max_list = \
                zip(*slice_minmax_list)

            slice_min = np.array(slice_min_list).min()
            slice_max = np.array(slice_max_list).max()

            return slice_min, slice_max

        n_frames = series.get_number_of_frames()
        frame_minmax_list = [get_frame_minmax(frame)
                             for frame in range(n_frames)]

        exemplar = series.get_dataset(0, 0)
        rescale_slope = float(exemplar.RescaleSlope)
        rescale_intercept = float(exemplar.RescaleIntercept)

        def apply_rescale(value: Any):

            return rescale_slope * value + rescale_intercept

        frame_minmax_rescaled_list = \
            [list(map(apply_rescale, [frame_min, frame_max]))
             for frame_min, frame_max in frame_minmax_list]

        frame_min_rescaled_list, frame_max_rescaled_list = \
            zip(*frame_minmax_rescaled_list)

        global_rescaled_min = min(frame_min_rescaled_list)
        global_rescaled_max = max(frame_max_rescaled_list)

        def get_window(min_value: Any, max_value: Any):

            center = (min_value + max_value) / 2
            width = max_value - min_value
            return cls(center, width)

        global_window = \
            get_window(global_rescaled_min, global_rescaled_max)

        frame_window_list = \
            [get_window(frame_min, frame_max)
             for frame_min, frame_max in
             frame_minmax_rescaled_list] \
            if series.is_multivolume() else None

        return global_window, frame_window_list
