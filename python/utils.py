import sys
import numpy as np
from typing import List


def is_sorted(arr) -> bool:
    """Check whether an array is sorted"""
    if arr.dtype.kind == 'u':
        return all(np.diff(arr.astype(int)) >= 0)
    return all(np.diff(arr) >= 0)


def group_index(arr) -> List:
    """Assumption: idx is sorted!"""
    diff = np.diff(arr.astype(int) if arr.dtype.kind == 'u' else arr)
    idx, = np.where(diff > 0)
    return [0] + (idx + 1).tolist()


def unique_elements(arr) -> List:
    """Assumes that arr is sorted"""
    return arr[group_index(arr)]


class Status:
    """
    Show status message when beginning and [ok] when done on `sys.stdout`.

    Example:
    >>> with Status("call slow"):
    >>>     slow(bli, bla)
    """
    indent = 40

    def __init__(self, msg, out=sys.stdout):
        self.msg = msg
        self.out = out

    def __enter__(self):
        print(self.msg.ljust(type(self).indent), end='...', flush=True,
              file=self.out)

    def __exit__(self, *args):
        print(' [ok]', file=self.out)


def prime_factors(n):
    """https://stackoverflow.com/a/22808285"""
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors
