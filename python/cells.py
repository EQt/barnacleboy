"""
Visualize some merfish cells.
"""
import numpy as np
import matplotlib.pyplot as plt
from typing import List
from reader import load_merfish


def is_sorted(arr):
    if arr.dtype.kind == 'u':
        all(np.diff(arr.astype(int)) >= 0)
    return all(np.diff(arr) >= 0)


def group_index(arr) -> List:
    """Assumption: idx is sorted!"""
    diff = np.diff(arr.astype(int) if arr.dtype.kind == 'u' else arr)
    idx, = np.where(diff > 0)
    return [0] + (idx + 1).tolist()


def unique_elements(arr) -> List:
    """Assumes that arr is sorted"""
    return arr[group_index(arr)]


def load_cells(fname: str, cell_ids: List, verbose=True):
    cell_ids = [int(i) for i in cell_ids]

    if verbose:
        print(f"Analyzing {basename(fname)}")
    df = load_merfish(fname)

    df_cell_ids = np.array(df["cellID"])
    mask = df_cell_ids == cell_ids[0]
    for i in cell_ids[1:]:
        mask |= df_cell_ids == i
    df = df[mask]
    df.sort(order='cellID')
    if True:
        assert is_sorted(df['cellID'])
    if verbose:
        print(f"Selected {len(df)} points")
    return df


if __name__ == '__main__':
    import argparse
    from os.path import basename
    from fisher import _test_file_name

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('cell', nargs='*', default=["2", "3", "4"])
    p.add_argument('-f', '--fname', type=str, default=_test_file_name())
    args = p.parse_args()

    df = load_cells(args.fname, args.cell)
    cell_idx = group_index(df['cellID'])
    if True:
        for cdf in np.split(df, cell_idx[1:]):
            print(cdf['cellID'][0])
