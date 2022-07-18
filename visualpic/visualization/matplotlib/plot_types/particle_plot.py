import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
from aptools.plotting.plot_types import scatter_histogram

from .utils import add_projection, create_vertical_colorbars


def particle_plot(
        x, y, q=None, x_name=None, y_name=None, x_units=None, y_units=None,
        q_units=None, x_lim=None, y_lim=None, x_projection=True, y_projection=True, bins=300, raster=False,
        cmap='plasma_r', cbar=False, cbar_ticks=3, cbar_width=0.05, subplot_spec=None, fig=None):

    if cbar:
        n_cols = 2
        width_ratios = [1, cbar_width]
    else:
        n_cols = 1
        width_ratios = None

    use_pyplot = False
    if fig is None:
        fig = plt.gcf()
        use_pyplot = True
    if subplot_spec is None:
        grid = gs.GridSpec(
            1, n_cols, width_ratios=width_ratios, figure=fig, wspace=0.05)
    else:
        grid = gs.GridSpecFromSubplotSpec(
            1, n_cols, subplot_spec, width_ratios=width_ratios, wspace=0.05)

    ax = fig.add_subplot(grid[0])
    img = scatter_histogram(x, y, bins=bins, weights=q, range=[x_lim, y_lim], cmap=cmap, rasterized=raster, ax=ax)

    x_label = '${}$ [${}$]'.format(x_name, x_units)
    y_label = '${}$ [${}$]'.format(y_name, y_units)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    if x_projection:
        add_projection(x, bins, ax, grid[0], fig)
    if y_projection:
        add_projection(y, bins, ax, grid[0], fig, orientation='vertical')

    # generate colorbar
    if q is not None and cbar:
        cbar_label = '$Q$ [${}$]'.format(q_units)
        create_vertical_colorbars(img, cbar_label, grid[1], fig, n_ticks=cbar_ticks)

    if use_pyplot:
        plt.sci(img)
    return img
