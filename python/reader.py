"""
Read merfish binary file information

Author: Elias Kuthe <elias.kuthe@udo.edu>
"""
import re
import sys
import numpy as np
from typing import List


def sizeof_int(typ: str) -> int:
    """
    >>> sizeof_int("uint32")
    4

    >>> sizeof_int("int8")
    1
    """
    n, = re.findall(r'\d+$', typ)
    n = int(n)
    assert n % 8 == 0
    return n // 8


def sizeof_type(typ: str) -> int:
    """
    >>> sizeof_type("double")
    8
    """
    sizes = {'single': 4,
             'float': 4,
             'double': 8,
             'char': 1}
    if typ in sizes:
        return sizes[typ]
    if 'int' in typ:
        return sizeof_int(typ)
    raise NotImplementedError(typ)


def sizeof_file(fname: str):
    """
    Compute the size of a file located at `fname`
    """
    from os import stat

    return stat(fname).st_size


def dtype_typ(c: str):
    """
    Create a corresponding np.dtype to `c`
    """
    if c == 'float':
        return np.float32
    return eval('np.' + c)


def create_dtype(infos):
    return np.dtype([(d, dtype_typ(c), f) for d, f, c in zip(*infos)])


def fread(io, typ, byteorder=sys.byteorder):
    """
    Read from (buffered) IO reader in the c type typ, eg
    """
    if typ == "bool":
        return bool.from_bytes(io.read(1), byteorder)
    elif "int" in typ:
        signed = typ[0] != "u"
        size = sizeof_int(typ)
        return int.from_bytes(io.read(size), sys.byteorder, signed=signed)
    else:
        raise NotImplementedError(f"Don't know how to read '{typ}'")


class RecordDef:
    """Layout definition of a merfish record"""
    fields: List[str]
    ctype: List[str]
    lens: List[int]

    def __iter__(self):
        return iter(zip(self.fields, self.lens, self.ctype))

    def sizeof(self) -> int:
        """
        Size of a record/struct in memory.
        Currently, ie version 1 (November 2018), that is 194 bytes
        """
        return sum(f * sizeof_type(c) for d, f, c in self)

    def c_struct(self, out=sys.stdout, name="Record", indent=4, type_align=8):
        """
        Print a C struct definition to file `out`
        (eg to generate a header to be used in C/C++ code).
        """
        def ctype(c):
            if c.startswith('int') or c.startswith('uint'):
                return c + '_t'
            return c

        print(f"struct {name}", file=out)
        print("{", file=out)
        for d, f, c in self:
            print(" " * (indent-1),
                  ctype(c).ljust(type_align),
                  d + (f"[{f}]" if f > 1 else "") + ";",
                  file=out)
        print(f"}};   /* sizeof({name}) == {self.sizeof()} */", file=out)


class Header:
    """Binary merfish header"""
    version: int = -1
    is_corrupt: bool = True
    num_entries: int = -1
    header_len: int = -1
    offset: int = -1
    layout: RecordDef = RecordDef()


def read_header(fname: str, check_file_size=True):
    """
    Read merfish binary header information.
    Usually that are the first 439 bytes.
    """
    h = Header()
    with open(fname, 'rb') as io:
        h.version = fread(io, "uint8")
        assert h.version == 1
        h.is_corrupt = fread(io, "bool")
        assert not h.is_corrupt
        h.num_entries = fread(io, "uint32")
        h.header_len = fread(io, "uint32")
        layout_str = io.read(h.header_len).decode()
        h.offset = io.tell()
    layout = layout_str.split(',')
    ctype = layout[2::3]
    h.layout.ctype = [s if s != 'single' else 'float' for s in ctype]
    h.layout.fields = layout[::3]
    h.layout.lens = [int(s.split(' ')[-1]) for s in layout[1::3]]
    if check_file_size:
        sizeof_record = h.layout.sizeof()
        a = h.offset + sizeof_record * h.num_entries
        b = sizeof_file(fname)
        assert a == b, f"{a} != {b} in {fname}"
    return h


def load_merfish(fname: str):
    """
    Return memory-mapped file access that can be treated as a numpy array.
    Usually you want to slice some of the elements and create a new array
    before further processing information as the mmap is read only, e.g
    ```
    a = np.array(load_merfish("bla.bin")[["barcode", "cellID"]]
    ```

    A full description of all columns can be obtained via
    `load_merfish("bla.bin").dtype.fields`.
    """
    infos, offset = read_header(fname)
    array = np.memmap(fname, offset=offset, dtype=create_dtype(infos))
    return array
