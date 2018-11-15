"""
Visualize MERFISH data
"""
import numpy as np
import matplotlib.pyplot as plt
from os import path
from numba import njit
from reader import load_merfish
from fisher import _test_file_name


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('fname', nargs='*', default=[_test_file_name()])
    p.add_argument('-p', '--microns-per-pixel', type=float, default=2)
    p.add_argument('-t', '--threshold-percentile', type=float, default=0.01)
    args = p.parse_args()

    mpp = args.microns_per_pixel
    cut = args.threshold_percentile

    @njit(cache=True)
    def fill_img(img, x, y, v):
        for xi, yi, ai in zip(x, y, v):
            img[xi, yi] += ai

    for fname in args.fname:
        out = path.basename(fname) + '.png'
        a = load_merfish(fname)
        coords = a['abs_position']
        min_x, min_y = coords.min(axis=0)
        max_x, max_y = coords.max(axis=0)

        width = int(np.ceil((max_x - min_x) / mpp))
        height = int(np.ceil((max_y - min_y) / mpp))
        vmax = np.quantile(a['total_magnitude'], 1-cut)

        print(f'Coordinates [{min_x:.3f}, {max_x:.3f}]',
              f'x [{min_y:.3f}, {max_y:.3f}]',
              f'values [0, {vmax:.3f}]')
        x = ((coords[:, 0] - min_x) / mpp).astype(int)
        y = ((coords[:, 1] - min_y) / mpp).astype(int)
        v = np.minimum(a['total_magnitude'] / vmax, 1.0)

        print(f'Filling image {width}x{height}')
        img = np.zeros((width, height), dtype=float)
        fill_img(img, x, y, v)
        print(f'Saving to "{out}"')
        plt.imsave(out, img, cmap='gray', vmin=0, vmax=1.0)
