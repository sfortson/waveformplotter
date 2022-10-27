"""Helper functions using the scipy signal package."""

from typing import Any, List

import numpy as np
from scipy import signal


def decimate(downsample_signal: List[Any], downsampling_factor: int) -> np.ndarray:
    """Downsample the signal after applying an anti-aliasing filter.

    :param downsample_signal: The signal to be downsampled, as an N-dimensional array.
    :type downsample_signal: List[Any]
    :param downsampling_factor: The downsampling factor.
    :type downsampling_factor: int
    :return: The down-sampled signal.
    :rtype: np.ndarray
    """
    return signal.decimate(downsample_signal, downsampling_factor, None, "iir", -1)
