"""
How to plot polygons or a triangulation quickly in `matplotlib`
"""
import matplotlib.pyplot as plt
import numpy as np
from numba import njit

from data import _test_file_name
from reader import load_merfish


def fill_exlusive(img, x, y, cell, full=-2, empty=-1):
    @njit
    def _fill(img, x, y, cell, full, empty):
        for i, (xi, yi) in enumerate(zip(x, y)):
            ci = cell[i]
            if not (img[xi, yi] == empty or img[xi, yi] == ci):
                ci = full
            img[xi, yi] = ci

    img = empty
    _fill(img, x, y, cell, full, empty)
    return img


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('fname', type=str, default=None, nargs='?')
    args = p.parse_args()

    fname = _test_file_name() if args.fname is None else args.fname
    df = load_merfish(fname)
    color_alpha = 0.2

    coords = np.array(df['abs_position'])
    cells = np.array(df['cellID'])

    ## Almost the same time for them and all of them too slow...
    # from scipy.spatial import Delaunay
    # import matplotlib
    # import graph
    #
    # tri = graph.delaunay_graph(coords)
    # tri = Delaunay(coords)
    # tri = matplotlib.tri.Triangulation(coords[:, 0], coords[:, 1])


    from img import quantize_coordinates, fill_img, generate_colortable
    x, y = quantize_coordinates(coords, 3.0)
    width, height = x.max()+1, y.max()+1

    colortab = generate_colortable() * color_alpha
    cells_c = np.mod(cells, len(colortab))
    v4 = colortab[cells_c]
    img = np.zeros((width, height, v4.shape[-1]), dtype=float)
    fill_img(img, x, y, v4)
    img = np.minimum(img, 1.0)
    npixels = (img > 0).any(axis=-1).sum()
    print(f'Reduction from {len(x):,d} to {npixels:,d}')
    if False:
        mask = (img > 0).any(axis=-1)
        xeff, yeff = np.where(mask)

    plt.imshow(img, interpolation='none')
    plt.show()
