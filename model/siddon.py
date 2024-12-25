"""
Implementation of Siddon's algorithm repurposed for tracing lines
on an image
"""

from dataclasses import dataclass

import numpy as np


_float = np.float32
_int = np.int32

EPSILON = np.finfo(_float).eps
DIR_POS = _int(1)
DIR_NEG = _int(-1)
ALPHA_MIN = _float(0.0)
ALPHA_MAX = _float(1.0)


def compute_path(im_shape, line_ij, closed=False):

    segments = list(zip(line_ij[:-1], line_ij[1:]))

    if closed:
        segments.append([line_ij[-1], line_ij[0]])

    path_i = []
    path_j = []
    for r1_ij, r2_ij in segments:

        path_elements_i, path_elements_j = \
            compute_path_core(im_shape, r1_ij, r2_ij)

        path_i.extend(path_elements_i)
        path_j.extend(path_elements_j)

    return path_i, path_j


def compute_path_core(im_shape, r1_ij, r2_ij):

    pixel_width_ij = [1, 1]

    # Vertical and horizontal setups
    setup_ij = [None] * 2
    setup_ij[0] = _dim_setup(im_shape[0], r1_ij[0], r2_ij[0])
    if setup_ij[0] is None:
        return
    setup_ij[1] = _dim_setup(im_shape[1], r1_ij[1], r2_ij[1])
    if setup_ij[1] is None:
        return

    # Values of alpha producing the points where the line enters
    # and exits the plane
    alpha_min = np.max([
        setup_ij[0].alpha_min,
        setup_ij[1].alpha_min,
        ALPHA_MIN])
    alpha_max = np.min([
        setup_ij[0].alpha_max,
        setup_ij[1].alpha_max,
        ALPHA_MAX])

    if alpha_min >= alpha_max:
        return

    # Find the variations of alpha necessary to travel between
    # neighboring inter-pixel planes for a given dimension
    d_alpha_ij = \
        [pixel_width / np.abs(setup.diff)
         for pixel_width, setup in
         zip(pixel_width_ij, setup_ij)]

    # Initialize position
    # Find the pixel where the line enters the plane
    position_ij = \
        [_get_start_ind(pixel_width,
                        dim_size,
                        r1,
                        setup.diff,
                        alpha_min)
         for pixel_width, dim_size, r1, setup in
         zip(pixel_width_ij, im_shape, r1_ij, setup_ij)]

    # For each non-cancelled dimension, get the value of alpha
    # for which the line touches the second plane along that
    # dimension after entering the plane
    alpha_ij = \
        [_prepare_dim(pixel_width, r1, setup, position, d_alpha)
         for pixel_width, r1, setup, position, d_alpha in
         zip(pixel_width_ij,
             r1_ij,
             setup_ij,
             position_ij,
             d_alpha_ij)]

    # Default empty path if the line doesn't intersect the plane
    path_elements_i = []
    path_elements_j = []

    previous_alpha = alpha_min
    while previous_alpha < alpha_max:

        # Update next_alpha to the next value for which the line
        # touches a plane between neighboring pixels
        next_alpha = min(alpha_max, alpha_ij[0], alpha_ij[1])

        # Write new path element after making sure it is within
        # the boundaries of the plane
        if position_ij[0] >= 0 and \
           position_ij[0] <= im_shape[0] - 1 and \
           position_ij[1] >= 0 and \
           position_ij[1] <= im_shape[1] - 1:

            path_elements_i.append(position_ij[0])
            path_elements_j.append(position_ij[1])

            if abs(alpha_ij[0] - next_alpha) < EPSILON:

                alpha_ij[0] += d_alpha_ij[0]
                position_ij[0] += setup_ij[0].direction

            if abs(alpha_ij[1] - next_alpha) < EPSILON:

                alpha_ij[1] += d_alpha_ij[1]
                position_ij[1] += setup_ij[1].direction

        previous_alpha = next_alpha

    return path_elements_i, path_elements_j


@dataclass
class _Setup:
    """
    Setup variables for a given dimension dim
    """

    # The line going from r1 to r2 is parameterized as:
    #  r(alpha) = r1 + (r2 - r1) * alpha = r1 + diff * alpha
    # => alpha goes from 0 to 1 when moving from r1 to r2

    # Value of alpha for a given value of r:
    #   alpha = (r - r1) / diff
    diff: _float

    # +1 or -1 depending on whether r2 is reached from
    # r1 by increasing dim (+1) or decreasing dim (-1)
    direction: _int

    # Values of alpha for which the line intersects the planes
    # of constant dim at the edges of the tracing area
    # => alpha_min for the one closest to r1
    # => alpha_max for the one farthest from r2
    alpha_min: _float
    alpha_max: _float

    next_alpha: _float


def _dim_setup(dim_size, r1: _float, r2: _float):

    low_plane = _float(-0.5)
    high_plane = _float(dim_size - 0.5)

    diff = r2 - r1

    if abs(diff) > EPSILON:

        if diff > 0:

            # Line travelling from low to high values
            direction = DIR_POS
            alpha_min = (low_plane - r1) / diff
            alpha_max = (high_plane - r1) / diff

        else:
            # Line travelling from high to low values
            direction = DIR_NEG
            alpha_min = (high_plane - r1) / diff
            alpha_max = (low_plane - r1) / diff

        # Indicates that the dimension is not "cancelled"
        next_alpha = ALPHA_MIN

    else:
        # The line has no component along the current dimension

        if r1 < low_plane or r1 > high_plane:

            # The line doesn't intersect the plane: Skip it!
            return

        # The line intersects the plane: Set special values
        diff = EPSILON
        direction = DIR_NEG

        # Widest allowed range of alpha so that those values
        # do not interfere in the later computation
        alpha_min = ALPHA_MIN
        alpha_max = ALPHA_MAX

        # Indicates that the dimension is "cancelled"
        next_alpha = ALPHA_MAX

    return _Setup(
        diff,
        direction,
        alpha_min,
        alpha_max,
        next_alpha)


def _get_start_ind(pixel_width, dim_size, r1, diff, alpha_min):

    low_plane = -0.5

    ind = np.int32(np.floor(
        (r1 + diff * alpha_min - low_plane) /
        pixel_width))

    # Make sure the initial coordinates are within the plane
    ind = np.max([0, np.min([ind, dim_size - 1])])

    return ind


def _prepare_dim(pixel_width, r1, setup, position, d_alpha):

    alpha = setup.next_alpha

    if alpha < ALPHA_MAX:

        length = -0.5 + pixel_width * position - r1

        alpha = length / setup.diff

    if setup.direction > 0:

        alpha += d_alpha

    return alpha
