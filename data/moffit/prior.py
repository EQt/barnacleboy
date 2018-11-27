"""
Let's have a quick look onto the data
"""
import pandas as pd

fname = 'raw/pixel.csv'

# show all columns
df = pd.read_csv(fname, nrows=10)
for c in df.columns:
    print(c)


# how many cells?
if False:
    df = pd.read_csv(fname, usecols=['Cell_ID'])
    print(f"#lines = {len(df):,d}")
    print(f"There are {len(df['Cell_ID'].unique()):,d} cells")
    # result: all cells are unique


# animal ...
df = pd.read_csv(fname, usecols=['Animal_sex', 'Animal_ID'])
print(f"{len(df.Animal_ID.unique())} different animals involved")
print(f"{(df.Animal_sex == 'Male').sum() / len(df) * 100:.2f}% are male")

# https://en.wikipedia.org/wiki/Bregma
#   Coordinate system in the skull
df = pd.read_csv(fname,
                 usecols=['Bregma', 'Centroid_X', 'Centroid_Y', 'Animal_ID'])
for animal in [1, 2, 3]:
    animal_df = df[df.Animal_ID == animal]
    assert animal_df.Bregma.is_monotonic_decreasing
    print(f"{len(animal1.Bregma.unique())} slices for Animal_ID == {animal}")


# cell classes ...
df = pd.read_csv(fname, usecols=['Cell_class'])
print('cell classes:')
for c in sorted(df.Cell_class.unique()):
    print('  ', c)
