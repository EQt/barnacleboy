"""
Let's have a quick look onto the data
"""
import pandas as pd
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
        print(f"{len(animal_df.Bregma.unique())} slices for Animal_ID == {animal}")


def plot_all_cells(df, animal_id=1, bregma=0.26):
    """Plot cell location (of all genes)"""
    animal1 = df[df.Animal_ID == animal_id]
    slice1 = animal1[animal1.Bregma == bregma]

    plt.figure(f"animal {animal_id}, bregma {bregma}")
    plt.plot(slice1.Centroid_X, slice1.Centroid_Y, '.')


def print_cell_classes(fname):
    df = read_csv(fname, usecols=['Cell_class'])
    print('cell classes:')
    for c in sorted(df.Cell_class.unique()):
        print('  ', c)


if __name__ == '__main__':
    print_columns(fname)
    df = read_csv(fname,
                  usecols=['Bregma', 'Centroid_X', 'Centroid_Y', 'Animal_ID'],
                  dtype={
                      'Bregma': float,
                      'Centroid_X': float,
                      'Centroid_Y': float,
                      'Animal_ID': int})
    print('loaded')
    plot_all_cells(df)
    plt.show()
