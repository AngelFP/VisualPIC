"""This module contains methods for plotting fields"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gs

from .utils import create_vertical_colorbars


def field_plot(
        field_data, field_name="", field_units=None, extent=None,
        xlabel=None, ylabel=None, vmin=None, vmax=None, aspect='auto',
        cmap=None, cbar=True, cbar_ticks=3, cbar_width=0.05, stacked=True,
        share_x=True, share_y=True, share_labels=True, subplot_spec=None,
        fig=None):
    """Make a field plot.

    Parameters
    ----------
    field_data : ndarray or list of ndarrays
        Array or list of field arrays to be plotted.
    field_name : str of list of strings, optional
        Name of the field(s) to be plotted. The list should have the same
        length as `field_data`.
    field_units : str of list of strings, optional
        Units of the field(s) to be plotted. The list should have the same
        length as `field_data`.
    extent : list, optional
        List containing the edges of the x and y axis, i,e,
        [xmin, xmax, ymin, ymax].
    xlabel : str, optional
        Label of the x axis.
    ylabel : _type_, optional
        Label of the y axis.
    vmin : float or list of floats, optional
        Minimum of the colormap range.
    vmax : float or list of floats, optional
        Maximum of the colormap range.
    aspect : str, optional
        Aspect ratio of the axes. See matplotlib imshow.
    cmap : str or matplotlib Colormap, or a list of them.
        The colormap to use for each field.
    cbar : bool, optional
        Whether to include a colorbar, by default True.
    cbar_ticks : int, optional
        Number of colorbar ticks, by default 3
    cbar_width : float, optional
        Width of the colorbar, by default 0.05
    stacked : bool, optional
        Whether to stack the all fields in the same axes (on top of each
        other) or show them in individual axes, by default True.
    share_x : bool, optional
        Whether the axes should share the x axis. Only needed when
        `staked=False`. By default True.
    share_y : bool, optional
        Whether the axes should share the y axis. Only needed when
        `staked=False`. By default True.
    share_labels : bool, optional
        Whether the axes should share the labels. Only needed when
        `staked=False`. By default True.
    subplot_spec : a matplotlib SubplotSpec, optional
        SubplotSpec where the plot will be drawn.
    fig : A matplotlib Figure, optional
        Figure where the plot will be drawn.

    Returns
    -------
    A matplotlib AxesImage
    """
    # Check inputs.
    if not isinstance(field_data, list):
        field_data = [field_data]
    if not isinstance(field_name, list):
        field_name = [field_name] * len(field_data)
    if not isinstance(field_units, list):
        field_units = [field_units] * len(field_data)
    if not isinstance(vmin, list):
        vmin = [vmin] * len(field_data)
    if not isinstance(vmax, list):
        vmax = [vmax] * len(field_data)
    if not isinstance(cmap, list):
        cmap = [cmap] * len(field_data)

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

    # If a subplot spec is not provided, create a new GridSpec.
    if subplot_spec is None:
        grid = gs.GridSpec(
            1, n_cols, width_ratios=width_ratios, wspace=0.05, figure=fig)
    else:
        grid = gs.GridSpecFromSubplotSpec(
            1, n_cols, subplot_spec, width_ratios=width_ratios, wspace=0.05)

    # List that will contain the AxesImage(s) returned by imshow.
    axes_image_list = []

    # If `staked`, plot all field in the same Axes.
    if stacked:
        plt_ax = fig.add_subplot(grid[0])
        for i, fld in enumerate(field_data):
            img = plt_ax.imshow(fld, aspect=aspect, vmin=vmin[i], vmax=vmax[i],
                                extent=extent, cmap=cmap[i])
            axes_image_list.append(img)
        if xlabel is not None:
            plt_ax.set_xlabel(xlabel)
        if ylabel is not None:
            plt_ax.set_ylabel(ylabel)
    # Otherwise, make one Axes for each.
    else:
        plt_gs = gs.GridSpecFromSubplotSpec(len(field_data), 1, grid[0])
        main_ax = None
        for i, fld in enumerate(field_data):
            sharex = main_ax if share_x else None
            sharey = main_ax if share_y else None
            ax = fig.add_subplot(plt_gs[i], sharex=sharex, sharey=sharey)
            if main_ax is None:
                main_ax = ax
            img = ax.imshow(fld, aspect=aspect, vmin=vmin[i], vmax=vmax[i],
                            extent=extent, cmap=cmap[i])
            axes_image_list.append(img)
            if i + 1 < len(field_data) and share_labels:
                ax.tick_params(axis='x', which='both', labelbottom=False)
            elif xlabel is not None:
                ax.set_xlabel(xlabel)
            if ylabel is not None:
                ax.set_ylabel(ylabel)

    # Generate colorbar labels.
    cbar_labels = []
    for fld_name, fld_units in zip(field_name, field_units):
        label_parts = []
        if fld_name is not None and fld_name.strip():
            label_parts.append('${}$'.format(fld_name))
        if fld_units is not None and fld_units.strip():
            label_parts.append('[${}$]'.format(fld_units))
        cbar_labels.append(' '.join(label_parts))

    # Set current image.
    if use_pyplot:
        plt.sci(img)

    # Create colorbars.
    if cbar:
        create_vertical_colorbars(
            axes_image_list, cbar_labels, grid[1], fig, n_ticks=cbar_ticks)
    return img
