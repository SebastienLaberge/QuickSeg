"""
Controller for navigating through a series (slices or frames)
"""

from typing import Callable, Optional, Sequence, Tuple, Union

from QuickSeg.view.navigation_panel import \
    NavigationPanel
from QuickSeg.view.series_selection_panel import \
    SeriesSelectionPanel


# Size specificer: Either a single size or a list of sizes
# prefixed with an index to the current one
SizeSpecifier = Union[int, Tuple[int, Sequence[int]]]


class NavigationController:

    def __init__(self,
                 navigation_panel: NavigationPanel,
                 series_selection_panel: SeriesSelectionPanel,
                 refresh_image: Callable,
                 on_index_change: Callable,
                 update_window: Optional[Callable] = None):

        self._navigation_panel = navigation_panel
        self._series_selection_panel = series_selection_panel

        self._refresh_image = refresh_image
        self._on_index_change = on_index_change
        self._update_window = update_window

        # Current index (0-based)
        self._current_index: Optional[int] = None

        # Maximum values for index
        self._size_specifier: Optional[SizeSpecifier] = None

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):

        self._navigation_panel.current_index_edit.\
            returnPressed.connect(self._slot_index_selection)

        self._navigation_panel.previous_button.\
            clicked.connect(self._slot_previous)

        self._navigation_panel.next_button.\
            clicked.connect(self._slot_next)

    def _slot_index_selection(self):

        if not self._check_current_series_index():
            self._navigation_panel.set_current_index(None)
            return

        index = self._navigation_panel.get_current_index()

        # If value from view is invalid, restore current value
        if index is None:
            self._navigation_panel.\
                set_current_index(self._current_index)
            return

        # Pin value to allowed range
        if index < (min_index := 0):
            self.set_current_index(min_index)

        elif index > (max_index := self._get_max_index()):
            self.set_current_index(max_index)
        else:
            # Value from view is valid
            self.set_current_index(index, update_view=False)

        self._refresh_image()

    def _slot_previous(self):

        if not self._check_current_series_index():
            return

        previous_index = self._current_index - 1

        min_index = 0
        new_index = max(min_index, previous_index)

        self.set_current_index(new_index)

        self._refresh_image()

    def _slot_next(self):

        if not self._check_current_series_index():
            return

        next_index = self._current_index + 1

        max_index = self._get_max_index()
        new_index = min(max_index, next_index)

        self.set_current_index(new_index)

        self._refresh_image()

    def get_current_index(self):

        return self._current_index

    def set_current_index(self,
                          index: int,
                          update_view: bool = True,
                          update_window: bool = True):

        self._current_index = index

        if update_view:
            self._navigation_panel.set_current_index(index)

        self._on_index_change(index)

        if self._update_window is not None and update_window:
            self._update_window()

    def set_size_specifier_index(self, index: int):

        assert isinstance(self._size_specifier, tuple)

        size_specifier = (index, self._size_specifier[1])

        self.set_size_specifier(size_specifier)

    def set_size_specifier(self, size_specifier: SizeSpecifier):

        self._size_specifier = size_specifier

        max_index = self._get_max_index()

        if self._current_index > max_index:

            self.set_current_index(max_index)

        self._navigation_panel.set_max_index(max_index)

    def _get_max_index(self) -> int:

        def get_n_slices(size_specifier: tuple) -> int:

            index = size_specifier[0]
            sizes = size_specifier[1]

            assert 0 <= index < len(sizes)

            return sizes[index]

        n_slices = get_n_slices(self._size_specifier) \
            if isinstance(self._size_specifier, tuple) \
            else self._size_specifier

        return n_slices - 1

    def _check_current_series_index(self) -> bool:

        current_series_index = \
            self._series_selection_panel.\
            get_current_series_index()

        return current_series_index is not None
