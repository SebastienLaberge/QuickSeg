"""
Utility functions for implementing lasso tools
"""

from typing import Optional

import numpy as np

from matplotlib._blocking_input import blocking_input_loop
from matplotlib.backend_bases import MouseButton, Event
from matplotlib.lines import Line2D

from scipy.ndimage import binary_fill_holes

from QuickSeg.model.siddon import compute_path


_float = np.float32

# Point defined as coordinates (i, j) => (vertical, horizonta)
Point = tuple[_float, _float]

# Line defined as a list of points
Line = list[Point]

# TODO: Make this a settable parameter
DISTANCE = 1

# TODO: Set depending on line type
COLOR = '#0f0a'

LINE_WIDTH = 3
MARKER_SIZE = 7


def trace_line(fig) -> Optional[Line]:

    line_data_x = []
    line_data_y = []
    line = None

    def handler(event: Event):

        nonlocal line_data_x, line_data_y, line

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
        current_position_xy = \
            np.array([event.xdata, event.ydata],
                     dtype=_float)

        tracing_started = line is not None

        if escape_pressed:

            # TODO: Figure out why the line disappears even if
            # the following statement is removed
            if tracing_started:

                line.remove()
                fig.canvas.draw()

            fig.canvas.stop_event_loop()
            return

        if left_button_pressed and in_axes:

            line_data_x = [current_position_xy[0]]
            line_data_y = [current_position_xy[1]]

            line = Line2D(
                line_data_x,
                line_data_y,
                linestyle='-',
                linewidth=LINE_WIDTH,
                color=COLOR,
                markersize=MARKER_SIZE,
                marker='.',
                markerfacecolor=COLOR)

            axes.add_line(line)

            fig.canvas.draw()

        elif mouse_moved and tracing_started:

            if in_axes:

                last_position_xy = np.array(
                    [line_data_x[-1], line_data_y[-1]],
                    dtype=_float)

                delta_position_xy = \
                    current_position_xy - last_position_xy

                distance = np.linalg.norm(delta_position_xy)

                if distance >= DISTANCE:

                    n = np.floor(distance / DISTANCE)
                    d = DISTANCE * delta_position_xy / distance

                    for k in np.arange(1, n + 1, dtype=_float):

                        line_data_x.append(
                            last_position_xy[0] + k * d[0])

                        line_data_y.append(
                            last_position_xy[1] + k * d[1])

                    line.set_data(line_data_x, line_data_y)

                    fig.canvas.draw()
            else:
                # TODO: Add logic for out of bounds
                pass

        elif left_button_released:

            if tracing_started:

                line.remove()
                fig.canvas.draw()

            fig.canvas.stop_event_loop()

    events = ["button_press_event",
              "button_release_event",
              "motion_notify_event",
              "key_press_event"]

    # Necessary to record keyboard events correctly
    fig.canvas.setFocus()

    blocking_input_loop(fig, events, -1, handler)

    return list(zip(line_data_y, line_data_x))


def trace_line_on_mask(im_shape, line_ij: Line) -> np.array:

    path_i, path_j = compute_path(im_shape, line_ij, True)

    # Trace path on mask
    mask = np.zeros(im_shape, dtype=bool)
    mask[path_i, path_j] = True

    # Fill path
    binary_fill_holes(mask, output=mask)

    return mask
