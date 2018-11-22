# Polygon Cell Boundaries (in Python)

## `cellboundaries.mat`

- **TODO** What information is there?
- **TODO** How do they compute it?


## How to determine?

Computing the convex hull is not an option as the cell boundaries usually contain concave parts, too.
As suggested by Kevin Dwyer in a [blog](http://blog.thehumangeo.com/2014/05/12/drawing-boundaries-in-python/), one could start with a Delaunay triangulation and eliminate the edges above a certain threshold.

Maybe the [`shapely`](http://toblerity.org/shapely/manual.html) module might be helpful.

[Alpha Concaveness](http://www.iis.sinica.edu.tw/page/jise/2012/201205_10.pdf)


## Plotting (`matplotlib`)

There is `matplotlib.patches.Polygon` which can be drawn by adding it to an axes instance (e.g. `plt.gca`) using the method `add_patch`.
For multiple instances however, this would be rather slow.
