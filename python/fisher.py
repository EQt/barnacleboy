"""
Play around with merfish binaries, ie
compute some statistics,
plot distributions,
check assumptions,
etc.
"""
import numpy as np
from os import path
from reader import read_header, print_struct, load_merfish


def _test_file_name() -> str:
    """File name to the test file (on my computer)"""
    return path.join(path.dirname(__file__),
                     "..", "..", "raw", "rep2", "assigned_blist.bin")


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('fname', nargs='*', default=[_test_file_name()])
    p.add_argument('-p', '--plot_hist', action='store_true')
    p.add_argument('-c', '--c_struct', action='store_true')
    p.add_argument('-s', '--stats', action='store_true')
    p.add_argument('-5', '--hdf5', action='store_true')
    p.add_argument('-C', '--check', action='store_true')
    args = p.parse_args()

    for fname in args.fname:
        if args.c_struct:
            header = read_header(fname)
            # header.layout.c_struct()
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
