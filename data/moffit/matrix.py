"""
Load the matrix provided on GEO (gene expression omnibus)

Quotes:
* "matrix.mtx contains the aggreggated counts from all samples"

* "genes.tsv contains the name associated with each measured gene."

* "barcodes.tsv contains the name associated with each cell for all samples"
"""
import scipy.io
import pandas as pd

gse = "GSE113576"
fname = f"./raw/{gse}_matrix.mtx.gz"


if False:
    mat = scipy.io.mmread(fname)
    n, m = mat.shape
    nnz = mat.nnz
    assert mat.dtype.name == 'int64'
else:
    n, m, nnz = pd.read_csv(fname, sep=' ', skiprows=2, nrows=1, header=None).values[0]
    # vals = pd.read_csv(fname, sep=' ', skiprows=3, header=None)

assert n == 27998
assert m == 31299
assert round(nnz / (n*m), 3) == 0.096

genes = pd.read_csv(f"./raw/{gse}_genes.tsv.gz", sep='\t', header=None)
assert len(genes) == n

barcodes = pd.read_csv(f"./raw/{gse}_barcodes.tsv.gz", sep='\t', header=None)
assert len(barcodes) == m

