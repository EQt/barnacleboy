"""
Compute a graph in the Euclidean plain
"""
import numpy as np
from numba import njit


def euclidean_edge_length(edges, coord):
    ec = coord[edges]
    dx = ec[:, 0, 0] - ec[:, 1, 0]
    dy = ec[:, 0, 1] - ec[:, 1, 1]
    return np.sqrt(dx**2 + dy**2)


def delaunay_graph(coord):
    from scipy.spatial import Delaunay

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
                e +=1

    tri = Delaunay(coord)
    indptr, indices = tri.vertex_neighbor_vertices

    m = len(indices)
    assert m % 2 == 0
    m //= 2
    # n = len(indptr) -1
    edges = np.empty((m, 2), dtype=int)
    compute_edges(edges, indptr, indices)
    return edges
