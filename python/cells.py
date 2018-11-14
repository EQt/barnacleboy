"""
Visualize some merfish cells.
"""
import numpy as np
import matplotlib.pyplot as plt
from typing import List
from reader import load_merfish, read_header


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
    from os.path import basename

    cell_ids = [int(i) for i in cell_ids]

    if verbose:
        print("Analyzing", basename(fname))
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
    p.add_argument('-a', '--all-coords', action='store_true')
    p.add_argument('-c', '--convex', action='store_true')
    p.add_argument('-d', '--delaunay', action='store_true')
    p.add_argument('-g', '--graph', action='store_true')
    args = p.parse_args()

    df = load_cells(args.fname, args.cell)
    layout = read_header(args.fname).layout

    fname = basename(args.fname)
    cell_idx = group_index(df['cellID'])
    cell_ids = df['cellID'][cell_idx]

    if args.all_coords:
        coord_fields = [f for f, i in zip(layout.fields, layout.lens) if i == 2]
        for field in coord_fields:
            plt.figure(f"{fname}: '{field}' on cells {cell_ids}")
            for cdf in np.split(df, cell_idx[1:]):
                coord = cdf[field]
                plt.plot(coord[:, 0], coord[:, 1], '.')

    if args.convex:
        from scipy.spatial import ConvexHull

        field = 'abs_position'
        for cdf in np.split(df, cell_idx[1:]):
            coord = cdf[field]
            conv = ConvexHull(coord)
            v = coord[conv.vertices]
            plt.fill(v[:, 0], v[:, 1], alpha=0.5)
            plt.plot(coord[:, 0], coord[:, 1], '.')

    if args.delaunay:
        from scipy.spatial import Delaunay

        field = 'abs_position'
        for cdf in np.split(df, cell_idx[1:]):
            coord = cdf[field]
            tri = Delaunay(coord)
            plt.triplot(coord[:, 0], coord[:, 1], tri.simplices, alpha=0.5)
            plt.plot(coord[:, 0], coord[:, 1], '.')


    if args.graph:
        from scipy.spatial import Delaunay
        from matplotlib.collections import LineCollection

        field = 'abs_position'
        coord = df[field]
        tri = Delaunay(coord)
        # idx = np.array([[0,1], [0, 2], [1, 2]])
        idx = [[0, 1]]
        edges = tri.vertices[:, 0:2]
        if False:
            edges = tri.vertices[100:103, idx]
            plt.plot(*coord[edges.flatten()].T, '.')

        # assert len(edges.shape) == 3
        # assert edges.shape[2] == 2
        # edges = edges.reshape(edges.shape[0]*edges.shape[1], edges.shape[2])

        # edges.sort(axis=1)      # i < j
        # edges.sort(axis=0)      # sort by head node index
        # edges = edges[::2]      # exclude every second edge (duplicates)

        line_coord = coord[edges]
        lc = LineCollection(line_coord, alpha=0.5, color='black')

        for cdf in np.split(df, cell_idx[1:]):
            plt.plot(*cdf[field].T, '.')
        ax = plt.gca()
        ax.add_collection(lc)
        
    plt.show()


def test_reshape():
    a = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]], [[9, 10], [11, 12]]])
    assert a.shape == (3, 2, 2)
