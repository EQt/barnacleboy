"""
Visualize MERFISH data
"""
import numpy as np
import matplotlib.pyplot as plt
from os import path
from numba import njit
from reader import load_merfish
from data import _test_file_name


@njit(cache=True)
def fill_img(img, x, y, v):
    for i, (xi, yi) in enumerate(zip(x, y)):
        img[xi, yi] += v[i]


def generate_colortable(name='Set1') -> np.ndarray:
    """
    See "Qualitative colormaps"
    https://matplotlib.org/tutorials/colors/colormaps.html
    """
    cmap = plt.get_cmap(name)
    ncolors = cmap.N
    colortab = np.hstack([np.array(cmap.colors), np.ones((ncolors, 1))])
    return colortab


def quantize_coordinates(coords, mpp, verbose=True):
    min_x, min_y = coords.min(axis=0)
    max_x, max_y = coords.max(axis=0)

    x = ((coords[:, 0] - min_x) / mpp).astype(int)
    y = ((coords[:, 1] - min_y) / mpp).astype(int)

    width = int(np.ceil((max_x - min_x) / mpp))
    height = int(np.ceil((max_y - min_y) / mpp))
    assert x.max() == width  -1, f'x.max = {x.max()}, width = {width}'
    assert y.max() == height -1, f'y.max = {y.max()}, height = {height}'

    if verbose:
        print(f'Coordinates [{min_x:.3f}, {max_x:.3f}]',
              f'x [{min_y:.3f}, {max_y:.3f}]')

    return x, y


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('fname', nargs='*', default=[_test_file_name()])
    p.add_argument('-p', '--microns-per-pixel', type=float, default=2)
    p.add_argument('-t', '--threshold-percentile', type=float, default=0.01)
    p.add_argument('-b', '--barcode', type=int, default=2)
    p.add_argument('-a', '--alpha', type=float, default=0.25)
    p.add_argument('-s', '--show', action='store_true')
    args = p.parse_args()

    mpp = args.microns_per_pixel
    cut = args.threshold_percentile

    for fname in args.fname:
        out = path.basename(fname) + '.png'
        a = load_merfish(fname)
        coords = a['abs_position']
        x, y = quantize_coordinates(coords, mpp)
        width, height = x.max()+1, y.max()+1
        vmax = np.percentile(a['total_magnitude'], 100*(1-cut))

        print(f'Values [0, {vmax:.3f}]')
        v = np.minimum(a['total_magnitude'] / vmax, 1.0)

        colortab = generate_colortable() * args.alpha
        cells = np.mod(a['cellID'], len(colortab))
        v4 = colortab[cells]

        print(f'Filling image {width}x{height}')
        img = np.zeros((width, height, v4.shape[-1]), dtype=float)
        fill_img(img, x, y, v4)
        img = np.minimum(img, 1.0)

        if args.show:
            plt.imshow(img, interpolation='none')
            plt.show()
        else:
            print(f'Saving to "{out}"')
            plt.imsave(out, img, cmap='gray', vmin=0, vmax=1.0)
