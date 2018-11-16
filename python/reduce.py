"""
Reduce the data to a graph having one node per cell
"""
import matplotlib.pyplot as plt
import numpy as np
from os.path import basename
from fisher import _test_file_name
from reader import load_merfish
from utils import is_sorted, group_index
from graph import delaunay_graph, plot_edges, euclidean_edge_length


if __name__ == '__main__':
    fname = _test_file_name()
    df = load_merfish(fname)
    print('Loading', basename(fname), end=' ... ', flush=True)
    a = np.array(df[['barcode_id', 'cellID', 'abs_position']])
    print('[ok]')

    print('Sorting cells', end=' ... ', flush=True)
    cell_order = np.argsort(a['cellID'])
    a = a[cell_order]
    cell_idx = group_index(a['cellID'])
    assert len(cell_idx) < 1e5
    print('[ok]')

    def iter_cells(axis='abs_position'):
        return np.split(a[axis], cell_idx[1:])

    centers = np.array([p.mean(axis=0) for p in iter_cells()])
    max_barcode = a['barcode_id'].max()+1
    gene_freq = np.zeros((len(cell_idx), max_barcode))
    for i, p in enumerate(iter_cells('barcode_id')):
        gene_freq[i, :] = np.bincount(p, minlength=gene_freq.shape[1]) / len(p)

    if True:
        total_freq = gene_freq.mean(axis=0)
        plt.figure("barcode frequencies")
        plt.bar(range(len(total_freq)), total_freq)
        plt.xlabel("barcode_id")
        plt.ylabel("relative frequency")
        plt.figure("sorted barcode frequencies")
        total_freq.sort()
        plt.bar(range(len(total_freq)), total_freq)
        plt.xlabel("barcode_id")
        plt.ylabel("relative frequency")


    # plt.plot(*a['abs_position'].T, '.', alpha=0.1)
    edges = delaunay_graph(centers)
    lens = euclidean_edge_length(edges, centers)
    thres = lens.mean() + 1.5*lens.std()
    edges = edges[lens <= thres]
    centers = np.fliplr(centers)

    if True:
        plt.figure("graph")
        plt.plot(*centers.T, '.', color='orange')
        plot_edges(edges, centers)
        plt.axis('equal')
        plt.show()
