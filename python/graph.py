"""
Graphs in the Euclidean plain
"""
import numpy as np
from numba import njit


def euclidean_edge_length(edges: np.ndarray, coord: np.ndarray) -> np.ndarray:
    """
    Result: array (shape `(m,)`)
    """
    ec = coord[edges]
    dx = ec[:, 0, 0] - ec[:, 1, 0]
    dy = ec[:, 0, 1] - ec[:, 1, 1]
    return np.sqrt(dx**2 + dy**2)


def delaunay_graph(coord: np.ndarray) -> np.ndarray:
    """
    Compute the edges of a Delaunay triangulation of the points
    given by `coord` (shape `nx2`).

    Result: adjacency list (array of shape `mx2`)
    """
    from scipy.spatial import Delaunay

    assert coord.ndim == 2
    assert coord.shape[1] == 2, f"coord have to be 2d array"

    @njit(cache=True)
    def compute_edges(edges, indptr, indices):
        m = len(edges)
        i = 0
        e = 0
        for p in range(2*m):
            while p >= indptr[i+1]:
                i += 1
            j = indices[p]
            if i < j:
                edges[e, 0] = i
                edges[e, 1] = j
                e += 1

    tri = Delaunay(coord)
    indptr, indices = tri.vertex_neighbor_vertices

    m = len(indices)
    assert m % 2 == 0
    m //= 2     # number of edges
    edges = np.empty((m, 2), dtype=int)
    compute_edges(edges, indptr, indices)
    return edges


def plot_edges(edges: np.ndarray, coord: np.ndarray, ax=None, **args):
    from matplotlib.collections import LineCollection
    import matplotlib.pyplot as plt

    xmin, ymin = coord.min(axis=0)
    xmax, ymax = coord.max(axis=0)
    offset = 0.001 * (xmax - xmin)

    lc = LineCollection(coord[edges], **args)
    if ax is None:
        ax = plt.gca()
    ax.add_collection(lc)
    ax.set_xlim([xmin - offset, xmax + offset])
    ax.set_ylim([ymin - offset, ymax + offset])
    ax.set_aspect('equal')


def store_graph(fname: str, edges: np.ndarray, values: np.ndarray,
                coord: np.ndarray):
    import h5py

    with h5py.File(fname, 'w') as io:
        io.create_dataset('edges', data=edges, compression=5)
        io.create_dataset('input', data=values, compression=5)
        io.create_dataset('coord', data=coord, compression=5)


if __name__ == '__main__':
    import argparse
    import pandas as pd
    import matplotlib.pyplot as plt
    from scipy import stats
    from data import moffit_example

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('fname', nargs='?', type=str, default=moffit_example)
    p.add_argument('-p', '--plot', action='store_true')
    p.add_argument('-o', '--out', type=str, default=None,
                   help='Write an HDF5 instance')
    args = p.parse_args()

    fname = args.fname() if callable(args.fname) else args.fname
    df = pd.read_csv(fname)
    values = df[df.columns[-1]]
    coord = df[df.columns[:2]].values

    edges = delaunay_graph(coord)
    edges = delaunay_graph(coord)
    lens = euclidean_edge_length(edges, coord)
    thres = lens.mean() + 1.2*lens.std()
    edges = edges[lens <= thres]

    zeros = values <= 0
    zr = zeros.sum() / len(values)
    print(len(edges), 'edges')
    print(f"zero = {zr * 100:.2f}%")

    if args.plot:
        plt.figure("graph")
        plot_edges(edges, coord)
        plt.plot(*coord[zeros].T, 'r.')
        plt.figure(f"input: {df.columns[-1]}, zeros cutted")
        val = stats.trim1(values, 0.01)
        plt.hist(val[val > 0], bins=100, log=True, histtype='step')
        plt.show()

    if args.out:
        store_graph(args.out, edges, values, coord)
