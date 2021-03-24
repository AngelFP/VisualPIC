import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
from aptools.plotting.plot_types import scatter_histogram

from .plot_utils import add_projection, create_vertical_colorbars


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


def field_plot(
        field_data, field_name=None, field_units=None, extent=None, xlabel=None,
        ylabel=None, vmin=None, vmax=None, aspect='auto', cmap=None, cbar=True,
        cbar_ticks=3, cbar_width=0.05, stacked=True, share_x=True, share_y=True,
        share_labels=True, subplot_spec=None, fig=None):
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
            1, n_cols, width_ratios=width_ratios, wspace=0.05, figure=fig)
    else:
        grid = gs.GridSpecFromSubplotSpec(
            1, n_cols, subplot_spec, width_ratios=width_ratios, wspace=0.05)

    img_list = []

    if stacked:
        plt_ax = fig.add_subplot(grid[0])
        for i, fld in enumerate(field_data):
            img = plt_ax.imshow(fld, aspect=aspect, vmin=vmin[i], vmax=vmax[i],
                                extent=extent, cmap=cmap[i])
            img_list.append(img)
        if xlabel is not None:
            plt_ax.set_xlabel(xlabel)
        if ylabel is not None:
            plt_ax.set_ylabel(ylabel)
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
            img_list.append(img)
            if i + 1 < len(field_data) and share_labels:
                ax.tick_params(axis='x', which='both', labelbottom=False)
            elif xlabel is not None:
                ax.set_xlabel(xlabel)
            if ylabel is not None:
                ax.set_ylabel(ylabel)

    # generate colorbar labels
    cbar_labels = []
    for fld_name, fld_units in zip(field_name, field_units):
        label_parts = []
        if fld_name is not None and fld_name.strip():
            label_parts.append('${}$'.format(fld_name))
        if fld_units is not None and fld_units.strip():
            label_parts.append('[${}$]'.format(fld_units))
        cbar_labels.append(' '.join(label_parts))

    if use_pyplot:
        plt.sci(img)
    if cbar:
        create_vertical_colorbars(img_list, cbar_labels, grid[1], fig, n_ticks=cbar_ticks)
    return img