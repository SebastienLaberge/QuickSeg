"""
Main application model
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

import numpy as np

from DicomSeriesManager.reader import DicomDirContent
from DicomSeriesManager.series import series_factory, BaseSeries

from QuickSeg.model.display_window_model import DisplayWindow


@dataclass
class SegItem:

    name: str
    path: Optional[Path]
    seg: np.array


@dataclass
class DisplayParameters:

    # Saved index values
    current_slice_index: dict[str, int] = \
        field(default_factory=lambda: {})
    current_frame_index: Optional[int] = None
    current_window_index: Optional[int] = None
    current_seg_index: Optional[int] = None

    # Saved manual window
    manual_window: Optional[DisplayWindow] = None

    # Saved FOV for each orientation
    current_FOV: dict[str, list[float]] = \
        field(default_factory=lambda: {})


@dataclass
class ExtractedWindows:

    dicom_window_list: Optional[Sequence[DisplayWindow]] = None
    global_window: Optional[DisplayWindow] = None
    frame_window_list: Optional[Sequence[DisplayWindow]] = None

    initialized: bool = False


@dataclass
class SeriesItem:

    name: str

    series: Optional[BaseSeries] = None

    seg_list: Sequence[SegItem] = \
        field(default_factory=lambda: [])

    display_params: DisplayParameters = \
        field(default_factory=DisplayParameters)

    extracted_display_window: ExtractedWindows = \
        field(default_factory=ExtractedWindows)


class Model:

    def __init__(self):

        self._dicom_dir_content: Optional[DicomDirContent] = None

        self._series_list: Sequence[SeriesItem] = []

    def read_dicom_dir(self, dicom_dir_path: str):

        dicom_dir_content = DicomDirContent(dicom_dir_path)

        self._replace_dicom_dir_content(dicom_dir_content)

    def save_dir_content(self, content_file_path: str):

        assert self._check_dicom_dir_content()

        self._dicom_dir_content.save(content_file_path)

    def load_dicom_dir_content(self, content_file_path: str):

        dicom_dir_content = \
            DicomDirContent.load(content_file_path)

        self._replace_dicom_dir_content(dicom_dir_content)

    def dicom_dir_is_loaded(self) -> bool:

        return self._dicom_dir_content is not None

    def get_series_info(self):

        return [(series_item.name,
                 series_item.series is not None)
                for series_item in self._series_list]

    def get_display_parameters(self, series_index: int) \
            -> DisplayParameters:

        assert self._check_series_index(series_index)

        series = self._series_list[series_index]

        return series.display_params

    def get_extracted_windows(self, series_index: int) \
            -> ExtractedWindows:

        assert self._check_series_index(series_index)

        series = self._series_list[series_index]

        return series.extracted_display_window

    def goc_series(self, series_index: int) -> BaseSeries:

        assert self._check_dicom_dir_content()
        assert self._check_series_index(series_index)

        series = self._series_list[series_index].series

        if series is None:

            series = series_factory(
                self._dicom_dir_content,
                series_index)

            self._series_list[series_index].series = series

        return series

    def delete_series(self, series_index):

        assert self._check_dicom_dir_content()
        assert self._check_series_index(series_index)

        del self._series_list[series_index]
        del self._dicom_dir_content.series_list[series_index]

    def add_new_seg(self, seg_name: str, series_index: int):

        assert self._check_series_index(series_index)

        series_item = self._series_list[series_index]

        # Create empty segmentation with the right shape
        vol_shape = series_item.series.get_vol_shape()
        seg = np.zeros(vol_shape, dtype=np.uint8)

        seg_list_item = SegItem(seg_name, None, seg)

        series_item.seg_list.append(seg_list_item)

        return len(series_item.seg_list) - 1

    def save_seg(self,
                 seg_file_path: str,
                 series_index: int,
                 seg_index: int):

        assert self._check_series_index(series_index)
        assert self._check_seg_index(series_index, seg_index)

        series_item = self._series_list[series_index]

        seg = series_item.seg_list[seg_index].seg

        np.save(seg_file_path, seg)

    def load_seg(self, seg_path: str, series_index: int) \
            -> Optional[int]:

        assert self._check_series_index(series_index)

        series_item = self._series_list[series_index]

        # TODO: Check that no segmentation has the current path
        # Add warning and notify callers
        # if seg_path in [seg.path for seg in series.seg_list]:
        #    return None

        # Load segmentation
        seg = np.load(seg_path)

        if seg.dtype != np.uint8:
            # TODO: Add warning window
            return None

        seg_shape = np.array(seg.shape)
        vol_shape = series_item.series.get_vol_shape()
        if not np.array_equal(seg_shape, vol_shape):
            # TODO: Add warning window
            return None

        # Create segmentation list item
        seg_file_stem = Path(seg_path).stem
        seg_item = \
            SegItem(seg_file_stem, seg_path, seg)

        # Add segmentation to list
        series_item.seg_list.append(seg_item)

        return len(series_item.seg_list) - 1

    def get_seg_names(self, series_index: int) \
            -> Sequence[str]:

        assert self._check_series_index(series_index)

        return [seg_item.name for seg_item in
                self._series_list[series_index].seg_list]

    def get_seg_name(self, series_index: int, seg_index: int) \
            -> str:

        assert self._check_series_index(series_index)
        assert self._check_seg_index(series_index, seg_index)

        series_item = self._series_list[series_index]

        return series_item.seg_list[seg_index].name

    def get_seg(self, series_index: int, seg_index: int) \
            -> Optional[np.array]:

        assert self._check_series_index(series_index)

        if not self._check_seg_index(series_index, seg_index):
            return None

        series_item = self._series_list[series_index]

        return series_item.seg_list[seg_index].seg

    def delete_seg(self, series_index: int, seg_index: int):

        assert self._check_series_index(series_index)
        assert self._check_seg_index(series_index, seg_index)

        del self._series_list[series_index].seg_list[seg_index]

    def _replace_dicom_dir_content(self, dicom_dir_content):

        self._dicom_dir_content = dicom_dir_content

        def make_series_list_item(series_files):

            series_description = \
                series_files.info['SeriesDescription']

            return SeriesItem(series_description)

        self._series_list = \
            [make_series_list_item(series_files)
             for series_files in
             self._dicom_dir_content.series_list]

    def _check_dicom_dir_content(self):

        return self._dicom_dir_content is not None

    def _check_series_index(self, series_index: int) -> bool:

        n_series = len(self._series_list)

        return 0 <= series_index < n_series

    def _check_seg_index(self,
                         series_index: int,
                         seg_index: int) -> bool:

        # Assumes that _check_series_index(series_index) has been
        # previously executed and has returned True.
        n_segs = len(self._series_list[series_index].seg_list)

        return seg_index is not None and \
            0 <= seg_index < n_segs
