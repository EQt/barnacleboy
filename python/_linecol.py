"""
Test how LineCollection works in matplotlib
"""
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt


n1, n2 = 3, 5
n = n1 * n2


coord = np.array([[i, j] for i in range(n1) for j in range(n2)], dtype=float)

plt.plot(*coord.T, '.')
for i in range(n1):
    for j in range(n2):
        plt.text(i, j, f"({i}, {j})")

edges = np.array([[0, 1],
                  [2, 3]])
lc = LineCollection(coord[edges])
plt.gca().add_collection(lc)
