"""
Utility functions for implementing manual zoom
"""

from typing import Optional

from matplotlib._blocking_input import blocking_input_loop
from matplotlib.backend_bases import MouseButton, Event
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from DicomSeriesManager.reorientation import (
    get_reoriented_im_shape,
    get_reoriented_PS)
from DicomSeriesManager.series import BaseSeries
from DicomSeriesManager.utils import get_slice_limits


Point = tuple[int, int]
Region = tuple[Point, Point]

GREEN = '#0f0'
LINE_WIDTH = 1


def select_region(fig: Figure) -> Optional[Region]:

    first_point = None
    second_point = None
    rect = None

    def handler(event: Event):

        nonlocal first_point, second_point, rect

        left_button_pressed = \
            event.name == "button_press_event" \
            and event.button == MouseButton.LEFT
        left_button_released = \
            event.name == "button_release_event" \
            and event.button == MouseButton.LEFT
        mouse_moved = event.name == "motion_notify_event"
        key_pressed = event.name == "key_press_event"
        escape_pressed = key_pressed and event.key in ['escape']

        axes = event.inaxes
        in_axes = axes is not None
        current_position_xy = (event.xdata, event.ydata)

        tracing_started = rect is not None

        if escape_pressed:

            if tracing_started:

                rect.remove()
                fig.canvas.draw()

            fig.canvas.stop_event_loop()

            return

        if left_button_pressed and in_axes:

            first_point = current_position_xy
            width = 0
            height = 0

            rect = Rectangle(
                first_point,
                width,
                height,
                linewidth=LINE_WIDTH,
                edgecolor=GREEN,
                facecolor='none')

            axes.add_patch(rect)

            fig.canvas.draw()

        elif mouse_moved and tracing_started:

            if in_axes:

                width = current_position_xy[0] - first_point[0]
                height = current_position_xy[1] - first_point[1]

                rect.set_width(width)
                rect.set_height(height)

                fig.canvas.draw()

            else:
                # TODO: Add logic for out of bounds
                pass

        elif left_button_released:

            if tracing_started:

                second_point = current_position_xy

                rect.remove()
                fig.canvas.draw()

            fig.canvas.stop_event_loop()

    events = ["button_press_event",
              "button_release_event",
              "motion_notify_event",
              "key_press_event"]

    # Necessary to record keyboard events correctly
    fig.canvas.setFocus()

    blocking_input_loop(fig, events, -1, handler)

    if first_point is None or second_point is None:

        return None

    if any(map(lambda x: x is None,
               [*first_point, *second_point])):

        return None

    def to_int(point: list[float]):

        return list(map(lambda x: int(round(x)), point))

    first_point = to_int(first_point)
    second_point = to_int(second_point)

    top_left = [min([first_point[0], second_point[0]]),
                min([first_point[1], second_point[1]])]

    bottom_right = [max([first_point[0], second_point[0]]),
                    max([first_point[1], second_point[1]])]

    return top_left, bottom_right


def convert_region_to_FOV(
        region: Region,
        previous_FOV: Optional[list[float]],
        series: BaseSeries,
        orientation: str) -> list[float]:

    im_shape = get_reoriented_im_shape(
        series.get_vol_shape(),
        orientation)

    pixel_spacing = \
        get_reoriented_PS(series.get_frame(), orientation)

    # First pixel i.e. the top-left pixel of the previous FOV
    # located with respect to that of the entire image
    if previous_FOV is None:

        # The previous FOV covers the entire image.
        first_pixel = [0, 0]
    else:
        previous_x_range, previous_y_range = \
            get_slice_limits(
                previous_FOV,
                im_shape,
                pixel_spacing)

        first_pixel = [previous_x_range[0], previous_y_range[0]]

    # Corners of the region defining the new FOV, located with
    # respect to the first pixel
    top_left, bottom_right = region

    # Central pixel of the entire image
    im_center = [im_shape[1] // 2, im_shape[0] // 2]

    # Dimensions of the new FOV
    dims = [bottom_right[i] - top_left[i] + 1 for i in range(2)]

    # Offset of the new FOV i.e. its central pixel located
    # with respect to the central pixel of the entire image
    offset = [first_pixel[i] +
              (top_left[i] + bottom_right[i] + 1) // 2 -
              im_center[i] for i in range(2)]

    FOV = [pixel_spacing[1] * dims[0],
           pixel_spacing[0] * dims[1],
           pixel_spacing[1] * offset[0],
           pixel_spacing[0] * offset[1]]

    return FOV
