"""
Work in progress (ie playground) of Elias
"""
import matplotlib.pyplot as plt
import numpy as np
from fisher import _test_file_name
from reader import load_merfish


if __name__ == '__main__':
    fname = _test_file_name()
    a = load_merfish(fname)
    c1 = a[a['cellID'] == 13]

    nuc = c1[c1['inNucleus'] == 1]
    cyt = c1[c1['inNucleus'] == 0]

    plt.plot(*nuc['abs_position'].T, 'r.')
    plt.plot(*cyt['abs_position'].T, 'b.')
    plt.show()
