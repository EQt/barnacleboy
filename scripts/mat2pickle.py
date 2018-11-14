#!/env/python3
import h5py
import numpy as np
import gzip
import pickle
import oct2py
import click


def group_to_map(group: h5py.Group, map: dict):
    for k, v in group.items():
        if isinstance(v, h5py.Group):
            m = map.get(k, {})
            map[k] = m
            group_to_map(v, m)
        elif isinstance(v, h5py.Dataset):
            map[k] = np.array(v.value)
        else:
            print(f"Unknown type for {k}: {type(v)}")


def map_by_id(cellId: str, feature: str, data: dict, map: dict):
    for k, v in data.items():
        if isinstance(v, np.ndarray):
            if k in {'type', 'dims'}:
                continue
            cellmap = map.get(cellId, {})
            map[cellId] = cellmap
            v = v.tolist()
            if isinstance(v, list) and len(v) == 1:
                v = v[()]
            if feature.endswith("Boundary"):
                v = list(zip(v[0], v[1]))
            cellmap[feature] = v
        else:
            map_by_id(k if k.startswith('_') else cellId,
                      feature if (k in {'type', 'value'} or k.startswith('_')) else k,
                      v,
                      map)


@click.command()
@click.argument("file", type=click.Path(file_okay=True, dir_okay=False, exists=True))
@click.option("-o", "--out", type=click.Path(file_okay=True, dir_okay=False))
@click.option("-m", "--mode", type=click.Choice(['h5', 'mat']), default='mat')
def convert(file, mode, out):
    if mode == 'mat':
        h5path = file + '.h5'
        with oct2py.Oct2Py() as oc:
            m = oc.load(file)
            oc.push("m", m)
            oc.eval(f"save -hdf5 {h5path} m")
    else:
        h5path = file
    data = {}
    with h5py.File(h5path, 'r') as f:
        group_to_map(f, data)
    # if mode == 'mat':
    #     os.remove(h5path)
    map2 = {}
    map_by_id("cell", "feature", data, map2)

    opener = gzip.open if out.endswith('.gz') else open
    with opener(out, 'wb') as writer:
        pickle.dump(map2, writer)


if __name__ == "__main__":
    convert()
