"""
Visualize the cell centers by their Voronoi diagram.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from scipy import spatial
from typing import Union


def polygon_area(points: Union[np.ndarray, Polygon]) -> float:
    """
    Compute the 2d area of a polygon given by the vertices `points`.

    https://en.wikipedia.org/wiki/Shoelace_formula
    """
    if isinstance(points, Polygon):
        p = points
        return 0.5 * abs(np.dot(p.xy[:-1, 0], p.xy[1:, 1]) -
                         np.dot(p.xy[:-1, 1], p.xy[1:, 0]))

    assert points.ndim == 2
    assert points.shape[1] == 2
    if len(points) <= 1:
        return 0.0
    x, y = points.T
    s1 = np.dot(x[:-1], y[1:])
    s2 = x[-1]*y[0]
    s3 = np.dot(x[1:], y[:-1])
    s4 = x[0] * y[-1]
    return 0.5 * abs(s1 + s2 - s3 - s4)


def test_polygon_zero():
    """Point/line polygon with vanishing area"""
    assert polygon_area(np.zeros((0, 2))) == 0
    assert polygon_area(np.zeros((1, 2))) == 0
    assert polygon_area(np.zeros((2, 2))) == 0


def test_polygon_area1():
    """Example from https://en.wikipedia.org/wiki/Shoelace_formula"""
    points = np.array([(2, 1), (4, 5), (7, 8)])
    assert polygon_area(points) == 3
    assert polygon_area(Polygon(points)) == 3


def test_polygon_area_more_complex():
    """Example from https://en.wikipedia.org/wiki/Shoelace_formula"""
    points = np.array([(3, 4), (5, 11), (12, 8), (9, 5), (5, 6)])
    assert polygon_area(points) == 30
    assert polygon_area(Polygon(points)) == 30


def plot_voronoi(points, colors, ax=None, cmap=None, c=15):
    vor = spatial.Voronoi(points)
    assert len(vor.point_region) == len(points)
    assert vor.point_region.min() >= 1
    assert vor.point_region.max() <= len(points)

    polys = list()
    for i in vor.point_region:
        simplex = vor.regions[i]
        simplex = np.asarray(simplex)
        if np.any(simplex < 0) or len(simplex) <= 0:
            polys.append(Polygon(vor.vertices[[i]]))
        else:
            polys.append(Polygon(vor.vertices[simplex]))

    areas = np.fromiter(map(polygon_area, polys), dtype=float)
    alpha = 1/np.clip(areas, 3, np.inf)
    alpha = alpha.clip(0, alpha.mean() + 1.5*alpha.std())

    xmin, ymin = points.min(axis=0)
    xmax, ymax = points.max(axis=0)
    offset = 0.001 * (xmax - xmin)

    if cmap is None:
        cmap = plt.get_cmap()
    col = cmap(colors)
    col[:, -1] = (c * alpha / alpha.max()).clip(0, 1)

    patch = PatchCollection(polys)
    patch.set_facecolor(col)

    if ax is None:
        ax = plt.gca()
    ax.add_collection(patch)
    ax.set_xlim([xmin - offset, xmax + offset])
    ax.set_ylim([ymin - offset, ymax + offset])
    ax.set_aspect('equal')


def plot_scatter(points, colors, cmap=None, alpha=0.1, s=150):
    """... to have usable defaults"""
    args = dict(alpha=alpha, s=s, edgecolors='none', cmap=cmap)
    plt.scatter(points[:, 0], points[:, 1], c=colors, **args)
    plt.gca().set_facecolor('k')
    plt.gca().set_aspect('equal')


def plot_clouds(points, colors):
    for s, a in [(350, 0.075), (160, 0.12), (60, 0.2), (5, 0.7)]:
        plot_scatter(points, colors, s=s, alpha=a)


def transform_colors(colors, logarithmic=False, eps=0.1, quant=0.99):
    if logarithmic:
        colors = (np.log(np.maximum(colors, eps)))
        colors /= colors.max()
    else:
        colors /= colors.max()
        assert colors.min() >= 0
        assert colors.max() <= 1.01, f'{colors.max()}'

    thres = np.percentile(colors, 100*quant)
    colors[colors > thres] = thres
    return colors


if __name__ == '__main__':
    import argparse
    from data import moffit_example

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('fname', type=str, nargs='?',
                   default=moffit_example())
    p.add_argument('-e', '--eps', type=float, default=0.1)
    p.add_argument('-l', '--logarithmic', action='store_true')
    p.add_argument('-c', '--cmap', type=str, default=None)
    p.add_argument('-q', '--quantile', type=float, default=0.99)
    args = p.parse_args()

    eps = args.eps
    logarithmic = args.logarithmic
    # plt.set_cmap('summer')
    # plt.set_cmap('coolwarm')
    # plt.set_cmap('RdYlBu')
    plt.set_cmap(args.cmap)

    df = pd.read_csv(args.fname)
    points = df[df.columns[:2]].values
    colors = transform_colors(df[df.columns[2]].values.copy(),
                              logarithmic=args.logarithmic,
                              eps=args.eps,
                              quantile=args.quantile)
    plot_clouds(points, colors)
    plt.colorbar()
    plt.figure()
    plot_voronoi(points, colors, c=15)
    plot_scatter(points, colors, s=3, alpha=0.9)
    plt.colorbar()
    plt.show()
