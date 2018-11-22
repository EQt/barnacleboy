"""
How to plot polygons or a triangulation quickly in `matplotlib`
"""
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from scipy.spatial import Delaunay

import graph
from fisher import _test_file_name
from reader import load_merfish


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('fname', type=str, default=None, nargs='?')
    args = p.parse_args()

    fname = _test_file_name() if args.fname is None else args.fname
    df = load_merfish(fname)

    coords = np.array(df['abs_position'])

    ## Almost the same time for them...
    # tri = graph.delaunay_graph(coords)
    # tri = Delaunay(coords)
    # tri = matplotlib.tri.Triangulation(coords[:, 0], coords[:, 1])
