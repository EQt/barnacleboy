# Reducing File Size

The file format of the data was created adhoc just to dump the most important information.
So here we collect some ideas on how to store and access the data more efficiently.


## Redundancies

A lot of information could be deduced from others, e.g.

- `is_exact` from `error_bit`
- `barcode` from `barcode_id` (as long as the codebook, a 140 entry list, is stored somewhere)
- **TODO** Continue


## Sorting/Indexing

In a lot of scenarios, it would be beneficial to access only certain cells (ie `cellID`s).
Also from an information theoretical point it makes sense to sort the points by cellID.
(Additionally, eg. as a second criterion one could sort by `barcode_id`.)
Then it suffices to store the ranges of the cells (in an array of size number of cells plus one).


## Compression

First experiments (by using HDF5 with compression) show, that `gzip` and `bzip2` compression only save 15-20% of space.
So it is questionable whether that pays of for the additional complexity that a compression brings.
