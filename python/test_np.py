import numpy as np


def test_reshape():
    """Check that my assumptions on how reshape on a 3d array work"""
    a = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]], [[9, 10], [11, 12]]])
    assert a.shape == (3, 2, 2)
