"""
Work in progress (ie playground) of Elias
"""
import matplotlib.pyplot as plt
import numpy as np
from fisher import _test_file_name
from reader import load_merfish


if __name__ == '__main__':
    fname = _test_file_name()
    cell_id = 13

    a = load_merfish(fname)
    c1 = a[a['cellID'] == cell_id]

    nuc = c1[c1['inNucleus'] == 1]
    cyt = c1[c1['inNucleus'] == 0]
    center = c1['abs_position'].mean(axis=0)

    if True:
        plt.figure("nucleus")
        plt.plot(*nuc['abs_position'].T, 'r.')
        plt.plot(*cyt['abs_position'].T, 'b.')
        plt.plot(*center.T, 'k.', markersize=30, alpha=0.1)

    barcode_freq = np.bincount(c1['barcode_id'])
    barcode_rank = np.argsort(barcode_freq)

    if True:
        bid = barcode_rank[-1]
        cb = c1[c1['barcode_id'] == bid]
        plt.figure(f"barcode {bid}: n={len(cb)}")
        plt.scatter(*cb['abs_position'].T, c=cb['total_magnitude'], s=30*cb['area'],
                    alpha=0.7)

    plt.show()
