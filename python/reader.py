import re
import sys
import numpy as np


def sizeof_int(typ):
    n, = re.findall(r'\d+$', typ)
    n = int(n)
    assert n % 8 == 0
    return n // 8


def sizeof_type(typ):
    sizes = {'single': 4,
             'float': 4,
             'double': 8,
             'char': 1}
    if typ in sizes:
        return sizes[typ]
    if 'int' in typ:
        return sizeof_int(typ)
    raise NotImplementedError(typ)


def sizeof_struct(infos):
    return sum(f * sizeof_type(c) for d, f, c in zip(*infos))


def sizeof_file(fname: str):
    """
    Compute the size of a file located at `fname`
    """
    from os import stat

    return stat(fname).st_size


def dtype_typ(c):
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


def read_header(fname):
    with open(fname, 'rb') as io:
        header_version = fread(io, "uint8")
        assert header_version == 1
        is_corrupt = fread(io, "bool")
        assert not is_corrupt
        num_entries = fread(io, "uint32")
        header_len = fread(io, "uint32")
        layout_str = io.read(header_len).decode()
        offset = io.tell()
    layout = layout_str.split(',')
    ctype = layout[2::3]
    ctype = [s if s != 'single' else 'float' for s in ctype]
    descr = layout[::3]
    factor = [int(s.split(' ')[-1]) for s in layout[1::3]]
    infos = (descr, factor, ctype)
    sizeof_record = sizeof_struct(infos)
    assert offset + sizeof_record * num_entries == sizeof_file(fname)
    return infos, offset


def print_struct(infos, out=sys.stdout, name="Record"):
    """
    """
    print(f"struct {name}", file=out)
    print("{", file=out)
    for d, f, c in zip(*infos):
        print("   ", c.ljust(7), d + (f"[{f}]" if f > 1 else "") + ";", file=out)
    print(f"}};   // sizeof({name}) == {sizeof_struct(infos)}", file=out)


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
