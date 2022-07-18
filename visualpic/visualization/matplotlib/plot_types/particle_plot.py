"""This module contains methods for plotting particles"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
from aptools.plotting.plot_types import scatter_histogram

from .utils import add_projection, create_vertical_colorbars


def particle_plot(
        x, y, q=None, x_name=None, y_name=None, x_units=None, y_units=None,
        q_units=None, x_lim=None, y_lim=None, x_projection=True,
        y_projection=True, bins=300, raster=False, cmap='plasma_r',
        cbar=False, cbar_ticks=3, cbar_width=0.05, subplot_spec=None,
        fig=None):
    """Make a particle plot.

    Parameters
    ----------
    x : ndarray
        1D array containing the particle coordinate to be plotted in the x
        axis.
    y : ndarray
        1D array containing the particle coordinate to be plotted in the y
        axis.
    q : ndarray, optional
        Charge of each particle, by default None
    x_name : str, optional
        Name of the coordinate plotted in the x axis, by default None
    y_name : str, optional
        Name of the coordinate plotted in the y axis, by default None
    x_units : str, optional
        Units of the x coordinate, by default None
    y_units : str, optional
        Units of the y coordinate, by default None
    q_units : str, optional
        Units of the particle charge, by default None
    x_lim : list, optional
        Range limits of the x axis (i.e., [xmin, xmax]), by default None
    y_lim : list, optional
        Range limits of the y axis (i.e., [ymin, ymax]), by default None
    x_projection : bool, optional
        Whether to include a projection of the x coordinate, by default True
    y_projection : bool, optional
        Whether to include a projection of the y coordinate, by default True
    bins : int, optional
        Number of bins to be used in the projections, by default 300
    raster : bool, optional
        Whether to rasterize the particle scatter plot, by default False
    cmap : str, optional
        Colormap to be used for the scatter plot, by default 'plasma_r'
    cbar : bool, optional
        Whether to show a colorbar, by default False
    cbar_ticks : int, optional
        Number of colorbar ticks, by default 3
    cbar_width : float, optional
        Width of the colorbar, by default 0.05
    subplot_spec : a matplotlib SubplotSpec, optional
        SubplotSpec where the plot will be drawn.
    fig : A matplotlib Figure, optional
        Figure where the plot will be drawn.

    Returns
    -------
    A matplotlib AxesImage
    """
    # Determine number of columns and their width ratio.
    if cbar:
        n_cols = 2
        width_ratios = [1, cbar_width]
    else:
        n_cols = 1
        width_ratios = None

    # If a figure is not provided, create one with pyplot.
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

    # Make scatter plot.
    ax = fig.add_subplot(grid[0])
    img = scatter_histogram(
        x, y, bins=bins, weights=q, range=[x_lim, y_lim], cmap=cmap,
        rasterized=raster, ax=ax)

    # Add axis labels.
    x_label = '${}$ [${}$]'.format(x_name, x_units)
    y_label = '${}$ [${}$]'.format(y_name, y_units)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    # Add projections.
    if x_projection:
        add_projection(x, bins, ax, grid[0], fig)
    if y_projection:
        add_projection(y, bins, ax, grid[0], fig, orientation='vertical')

    # Generate colorbars.
    if q is not None and cbar:
        cbar_label = '$Q$ [${}$]'.format(q_units)
        create_vertical_colorbars(
            img, cbar_label, grid[1], fig, n_ticks=cbar_ticks)

    # Set current image.
    if use_pyplot:
        plt.sci(img)
    return img
