import click
import numpy as np

from reader import load_merfish


@click.command()
@click.argument("FILE", type=click.File())
@click.option("--plot", is_flag=True, help="Plot field of views")
def fov(file: click.File, plot: bool):
    """Calculate field-of-view dimensions and overlap.
    """
    data = load_merfish(file.name)[['fov_id', 'abs_position']]
    shapes = []
    fov_width, fov_height = 0, 0
    fovs = data['fov_id']
    # this is slow. I don't mind, tho.
    for fov_id in np.unique(fovs):
        mask = fovs == fov_id
        d = data['abs_position'][mask]
        (min_x, min_y), (max_x, max_y) = d.min(axis=0), d.max(axis=0)
        shapes.append(dict(type='rect', x0=min_x, x1=max_x, y0=min_y, y1=max_y))
        fov_width = max(max_x - min_x, fov_width)
        fov_height = max(max_y - min_y, fov_height)
    (xmin, ymin), (xmax, ymax) = data['abs_position'].min(axis=0), data['abs_position'].max(axis=0)
    abs_width, abs_height = xmax - xmin, ymax - ymin

    num_fovs_x, remainder_x = divmod(abs_width, fov_width)
    num_fovs_y, remainder_y = divmod(abs_height, fov_height)
    print(f"{abs_width} x {abs_height}")
    print(f"{num_fovs_x} fovs with width  {fov_width} and remainder {remainder_x}")
    print(f"{num_fovs_y} fovs with height {fov_height} and remainder {remainder_y}")
    if plot:
        from plotly.offline import plot as oplot
        from plotly.graph_objs import Figure, Layout
        oplot(Figure(data=[], layout=Layout(shapes=shapes,
                                            xaxis={'range': [xmin - 1, xmax + 1]},
                                            yaxis={'range': [ymin - 1, ymax + 1]})))


if __name__ == "__main__":
    fov()
