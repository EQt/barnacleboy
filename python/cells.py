"""
Visualize some merfish cells.
"""
import numpy as np
from reader import load_merfish


if __name__ == '__main__':
    import argparse
    from os.path import basename
    from fisher import _test_file_name

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('cell', nargs='*', default=["2", "3", "4"])
    p.add_argument('-f', '--fname', type=str, default=_test_file_name())
    args = p.parse_args()

    cell_ids = [int(i) for i in args.cell]
    print(f"Analyzing {basename(args.fname)}")
    df = load_merfish(args.fname)

    df_cell_ids = np.array(df["cellID"])
    mask = df_cell_ids == cell_ids[0]
    for i in cell_ids[1:]:
        mask |= df_cell_ids == i
    print(f"Selected {mask.sum()} points") 
