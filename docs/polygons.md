# Polygons in Python

## How to determine?

Computing the convex hull is not an option as the cell boundaries usually contain concave parts, too.
As suggested by Kevin Dwyer in a [blog](http://blog.thehumangeo.com/2014/05/12/drawing-boundaries-in-python/), one could start with a Delaunay triangulation and eliminate the edges above a certain threshold.

Maybe the [`shapely`](http://toblerity.org/shapely/manual.html) module might be helpful.
