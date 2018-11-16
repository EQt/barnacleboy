import numpy as np
from utils import is_sorted


def test_reshape():
    """Check that my assumptions on how reshape on a 3d array work"""
    a = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]], [[9, 10], [11, 12]]])
    assert a.shape == (3, 2, 2)


def test_is_sorted1():
    a = np.array([1, 2, 0], dtype=np.uint8)
    assert not is_sorted(a)


def test_is_sorted2():
    a = np.array([0, 2, 2], dtype=np.uint8)
    assert is_sorted(a)


def test_slow():
    if False:
        a = load_merfish(fname)
        assert not is_sorted(a['cellID'])
        cell_order = np.argsort(a['cellID'])
        assert not is_sorted(cell_order)
        assert is_sorted(a['cellID'][cell_order])
