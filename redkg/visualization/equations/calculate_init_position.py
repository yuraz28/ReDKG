"""Calculate initial position module."""

from typing import Any

import numpy as np


def calculate_init_position(vertex_num: int, center: tuple[float, float] = (0, 0), scale: float = 1.0) -> Any:
    """Calculate initial position function."""
    return (np.random.rand(vertex_num, 2) * 2 - 1) * scale + center
