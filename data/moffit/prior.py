"""
Let's have a quick look onto the data
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
try:
    from dask.dataframe import read_csv as rcsv

    def read_csv(*args, **kwargs):
        return rcsv(*args, **kwargs).compute()

except ImportError:
    from pandas import read_csv


fname = 'raw/pixel.csv'


def print_columns(fname):
    """show all columns"""
    df = pd.read_csv(fname, nrows=10)
    for c in df.columns:
        print(c)

def gene_list(fname, last_col='Neuron_cluster_ID'):
    df = pd.read_csv(fname, nrows=1)
    for idx, c in enumerate(df.columns):
        if c == last_col:
            break
    return df.columns[idx+1:].tolist()


def count_cells() -> int:
    """how many cells?"""
    df = read_csv(fname, usecols=['Cell_ID'])
    ncells = len(df['Cell_ID'].unique())
    print(f"#lines = {len(df):,d}")
    print(f"There are {ncells:,d} cells")
    # result: all cells are unique
    return ncells


def print_gender(fname: str):
    """animal ..."""
    df = read_csv(fname, usecols=['Animal_sex', 'Animal_ID'])
    print(f"{len(df.Animal_ID.unique())} different animals involved")
    print(f"{(df.Animal_sex == 'Male').sum() / len(df) * 100:.2f}% are male")


def print_num_slices(animals=[1, 2, 3]):
    """
    https://en.wikipedia.org/wiki/Bregma
       Coordinate system in the skull
    """
    df = read_csv(fname,
                     usecols=['Bregma', 'Centroid_X', 'Centroid_Y', 'Animal_ID'])
    for animal in animals:
        animal_df = df[df.Animal_ID == animal]
        assert animal_df.Bregma.is_monotonic_decreasing
        print(f"{len(animal_df.Bregma.unique())} slices " +
              f"for Animal_ID == {animal}")


def plot_cells(df, animal_id=1, bregma=0.26, gene=None, log=True, eps=0.5, **args):
    """Plot cell location (of all genes)"""
    animal1 = df[df.Animal_ID == animal_id]
    slice1 = animal1[animal1.Bregma == bregma]

    plt.figure(f"animal {animal_id}, bregma {bregma}")
    if gene is not None:
        color = slice1[gene]
        if log:
            if eps < 0:
                color = np.log(np.maximum(color, -eps))
            else:
                color = np.log(eps+color)
        print('nan:', np.isnan(color).sum() / len(color))
        plt.scatter(slice1.Centroid_X, slice1.Centroid_Y, c=color, **args)
        plt.colorbar()
    else:
        plt.plot(slice1.Centroid_X, slice1.Centroid_Y, '.', **args)


def print_cell_classes(fname):
    df = read_csv(fname, usecols=['Cell_class'])
    print('cell classes:')
    for c in sorted(df.Cell_class.unique()):
        print('  ', c)


if __name__ == '__main__':
    # for g in gene_list(fname):
    #     print(g)
    gene = 'Pak3'
    dtype = {
        'Bregma': float,
        'Centroid_X': float,
        'Centroid_Y': float,
        'Animal_ID': int,
        gene: float
    }
    df = read_csv(fname, usecols=list(dtype.keys()), dtype=dtype)
    print('loaded')
    print(sorted(df['Bregma'].unique()))
    print(sorted(df['Animal_ID'].unique()))

    cmap = 'Spectral'
    cmap = 'PuOr'
    cmap = 'RdBu'
    cmap = 'RdYlBu'
    cmap = 'hot'
    cmap = 'coolwarm'
    cmap = None
    args = dict(alpha=0.1, s=150, edgecolors='none', cmap=cmap, eps=-0.5)

    for a in [1, 2, 3, 4, 11, 13, 23][:2]:
        for b in [-0.04, 0.01, 0.06, 0.11]:
            plot_cells(df, bregma=b, animal_id=a, gene=gene, **args)
    plt.show()
