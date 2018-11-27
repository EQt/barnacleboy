"""
Load the matrix provided on GEO (gene expression omnibus)
"""
import scipy.io

fname = "./raw/GSE113576_matrix.mtx.gz"
mat = scipy.io.mmread(fname)

n, m = mat.shape
assert mat.dtype.name == 'int64'
assert n == 27998
assert m == 31299
assert round(mat.nnz / (n*m), 3) == 0.096
