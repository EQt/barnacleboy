"""
Visualize some merfish cells.
"""
import numpy as np
from reader import load_merfish


def is_sorted(arr):
    if arr.dtype.kind == 'u':
        all(np.diff(arr.astype(int)) >= 0)
    return all(np.diff(arr) >= 0)


if __name__ == '__main__':
    import argparse
    from os.path import basename
    from fisher import _test_file_name

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('cell', nargs='*', default=["2", "3", "4"])
    p.add_argument('-f', '--fname', type=str, default=_test_file_name())
    args = p.parse_args()

    fname = args.fname
    cell_ids = [int(i) for i in args.cell]

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
    print(f"Selected {len(df)} points")

    
