"""
Extract header information from a Merfish binary file
"""
from os import path
import sys
import re
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


def sizeof_file(fname):
    from os import stat

    return stat(fname).st_size


def dtype_typ(c):
    if c == 'float':
        return np.float32
    return eval('np.' + c)


def create_dtype(infos):
    return np.dtype([(d, dtype_typ(c), f) for d, f, c in zip(*infos)])


def fread(io, typ):
    """
    Read from (buffered) IO reader in the c type typ
    """
    if typ == "bool":
        return bool.from_bytes(io.read(1), sys.byteorder)
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
    print(f"struct {name}", file=out)
    print("{", file=out)
    for d, f, c in zip(*infos):
        print("   ", c.ljust(7), d + (f"[{f}]" if f > 1 else "") + ";", file=out)
    print(f"}};   // sizeof({name}) == {sizeof_struct(infos)}", file=out)


def load_merfish(fname):
    infos, offset = read_header(fname)
    array = np.memmap(fname, offset=offset, dtype=create_dtype(infos))
    return array


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('fname', nargs='*',
                   default=[path.join(path.dirname(__file__),
                                      "..", "..", "raw", "rep2", "assigned_blist.bin")])
    p.add_argument('-p', '--plot_hist', action='store_true')
    p.add_argument('-c', '--c_struct', action='store_true')
    p.add_argument('-s', '--stats', action='store_true')
    p.add_argument('-5', '--hdf5', action='store_true')
    p.add_argument('-C', '--check', action='store_true')
    args = p.parse_args()

    for fname in args.fname:
        if args.c_struct:
            infos, _ = read_header(fname)
            print_struct(infos)
            break
        array = load_merfish(fname)

        if args.hdf5:
            import h5py

            out = path.basename(fname) + ".h5"
            with h5py.File(out, 'w') as io:
                for f in array.dtype.fields:
                    print('writing', f, '...', end='', flush=True)
                    io.create_dataset(f, data=array[f], compression=1)
                    print()
            break

        def print_range(i, indent=20):
            min_x, min_y = array[i].min(axis=0)
            max_x, max_y = array[i].max(axis=0)
            print(i.ljust(indent), '= [', min_x, ',', max_x, '] x [',
                  min_y, ',', max_y, ']')

        if args.stats:
            pp = ['pixel_centroid',
                  'abs_position',
                  'weighted_pixel_centroid']
            indent = max(map(len, pp)) + 1
            for i in pp:
                print_range(i, indent=indent)

            print(f"in nuclues: {array['inNucleus'].mean()*100:.2f}%")

        if args.check:
            assert array['inNucleus'].min() >= 0
            assert array['inNucleus'].max() <= 1
            # not ordered...
            assert any(np.diff(array['cellID'].astype(int)) < 0)

        if args.plot_hist:
            import matplotlib.pyplot as plt
            from scipy import stats

            magnitude = stats.trim1(array['total_magnitude'], 0.001)
            plt.figure(f"{fname}: total_magnitude")
            plt.hist(magnitude, log=True, bins=300)

            cut = 0.0001
            plt.figure(f"{fname}: distNucleus (trim1 {cut*100}%)")
            plt.hist(stats.trim1(array['distNucleus'], cut),
                     bins=300, log=True, density=True)

            plt.figure(f"{fname}: error_bit")
            plt.hist(array['error_bit'],
                     log=True, density=True, rwidth=0.7, align='left', bins=range(0, 17))

            plt.figure(f"{fname}: area")
            plt.hist(array['area'], log=True, density=True, bins=100)

            if False:
                plt.plot(array['pixel_centroid'][:, 0],
                         array['abs_position'][:, 0], '.', alpha=0.1)

            if False:
                cx = array['pixel_centroid'][:500, 0]
                cy = array['pixel_centroid'][:500, 1]
                plt.figure('centroid')
                plt.plot(cx, cy, '.')

                ax = array['abs_position'][:500, 0]
                ay = array['abs_position'][:500, 1]
                plt.figure('abs_position (flip x)')
                plt.plot(-ax, ay, '.')

            if False:
                a = np.array(array['abs_position'][:, 0])
                b = np.array(array['pixel_centroid'][:, 0], dtype=float)
                a -= a.mean()
                b -= b.mean()
                plt.plot(a / b)

            if False:
                for  cellID in [13, 42, 11, 9]:
                    mask = array['cellID'] == cellID
                    print(f"cell {cellID} contains {mask.sum()} elements")
                    a = np.array(array['abs_position'][:, 0][mask], dtype=float)
                    # b = np.array(array['pixel_centroid'][:, 0][mask], dtype=float)
                    b = np.array(array['weighted_pixel_centroid'][:, 0][mask], dtype=float)
                    a -= a.mean()
                    b -= b.mean()
                    print((a / b).std() * 100)
                    # plt.plot((a / b).std())
                    # plt.figure(f"cell {cellID}")
                    plt.hist(a / b, log=True, bins=100, histtype='step', density=True)

            # distPeriphery
            plt.show()
