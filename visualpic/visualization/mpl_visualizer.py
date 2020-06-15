import sys
from functools import partial

import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
from matplotlib.figure import Figure
from matplotlib import ticker
from matplotlib.colorbar import Colorbar
from matplotlib.style import library
import numpy as np
from PyQt5 import QtWidgets
from aptools.plotting.plot_types import scatter_histogram

from visualpic.ui.basic_plot_window import BasicPlotWindow
from visualpic.helper_functions import (get_common_timesteps,
                                        get_common_array_elements)


aptools_rc_params = {'axes.linewidth': 0.5,
                     'axes.labelsize': 8,
                     'xtick.major.size': 2,
                     'ytick.major.size': 2,
                     'xtick.major.width': 0.5,
                     'ytick.major.width': 0.5,
                     'xtick.labelsize': 8,
                     'ytick.labelsize': 8,
                     'xtick.direction': 'in',
                     'ytick.direction': 'in',
                     'xtick.top': True,
                     'ytick.right': True,
                     'legend.borderaxespad': 1}#,
                    #  'figure.constrained_layout.use': True}
rc_dark = {**library['dark_background'], **aptools_rc_params}


class MplVisualizer():

    def __init__(self):
        self._figure_list = []
        self._current_figure = None

    def figure(self, fig_idx=None):
        if fig_idx is not None:
            fig = self._figure_list[fig_idx]
        else:
            fig = VPFigure()
            self._figure_list.append(fig)
        self._set_current_figure(fig)
        return fig

    def field_plot(
            self, field, field_units=None, axes_units=None, time_units=None,
            slice_dir=None, slice_pos=0.5, m='all', theta=0, vmin=None,
            vmax=None, cmap=None, stacked=True, cbar=True):
        fig = self._get_current_figure()
        subplot = FieldSubplot(
            field, field_units=field_units, axes_units=axes_units,
            time_units=time_units, slice_dir=slice_dir, slice_pos=slice_pos,
            m=m, theta=theta, vmin=vmin, vmax=vmax, cmap=cmap, stacked=stacked,
            cbar=cbar)
        fig.add_subplot(subplot)

    def particle_plot(
            self, species, x='x', y='y', x_units=None, y_units=None,
            q_units=None, time_units=None, cbar=True):
        fig = self._get_current_figure()
        subplot = ParticlePlot(
            species, x=x, y=y, x_units=x_units, y_units=y_units,
            q_units=q_units, time_units=time_units, cbar=cbar)
        fig.add_subplot(subplot)

    def show(self, timestep=0):
        app = QtWidgets.QApplication(sys.argv)
        for figure in self._figure_list:
            figure.generate(timestep)
        self.windows = []
        for figure in self._figure_list:
            self.windows.append(BasicPlotWindow(figure, self))
        app.exec_()

    def _set_current_figure(self, figure):
        self._current_figure = figure

    def _get_current_figure(self):
        if self._current_figure is None:
            return self.figure()
        else:
            return self._current_figure


class VPFigure():

    def __init__(self, **kwargs):
        self._subplot_list = []
        with plt.rc_context(rc_dark):
            self._mpl_figure = Figure(tight_layout=True)
        self._current_timestep = -1

    def add_subplot(self, subplot):
        self._subplot_list.append(subplot)

    def generate(self, timestep):
        self._mpl_figure.clear()
        gs = self._mpl_figure.add_gridspec(1, len(self._subplot_list))
        self._current_timestep = timestep
        for i, subplot in enumerate(self._subplot_list):
            # ax = self._mpl_figure.add_subplot(gs[i])
            subplot.plot(timestep, gs[i], self._mpl_figure)
        # self._mpl_figure.tight_layout()

    def get_available_timesteps(self):
        ts_list = []
        for subplot in self._subplot_list:
            ts_list.append(subplot.get_available_timesteps())
        return get_common_array_elements(ts_list)


class Subplot():

    def __init__(self, datasets):
        if not isinstance(datasets, list):
            datasets = [datasets]
        self._datasets = datasets

    def get_available_timesteps(self):
        return get_common_timesteps(self._datasets)

    def plot(self, timestep, subplot_spec, fig):
        with plt.rc_context(rc_dark):
            self._make_plot(timestep, subplot_spec, fig)

    def _make_plot(self, timestep, subplot_spec, fig):
        raise NotImplementedError()


class FieldSubplot(Subplot):

    def __init__(
            self, fields, field_units=None, axes_units=None, time_units=None,
            slice_dir=None, slice_pos=0.5, m='all', theta=0, vmin=None,
            vmax=None, cmap=None, stacked=True, cbar=True):

        # Convert necessary arguments into lists
        if not isinstance(fields, list):
            fields = [fields]
        if not isinstance(field_units, list):
            field_units = [field_units] * len(fields)
        if not isinstance(slice_pos, list):
            slice_pos = [slice_pos] * len(fields)
        if not isinstance(m, list):
            m = [m] * len(fields)
        if not isinstance(theta, list):
            theta = [theta] * len(fields)

        self._field_arguments = []
        for i in range(len(fields)):
            self._field_arguments.append(
                {
                    'field_units': field_units[i],
                    'axes_units': axes_units,
                    'time_units': time_units,
                    'slice_i': slice_pos[i],
                    'slice_dir_i': slice_dir,
                    'm': m[i],
                    'theta': theta[i]
                })
        self._plot_arguments = {
            'vmin': vmin,
            'vmax': vmax,
            'cmap': cmap,
            'cbar': cbar,
            'stacked': stacked
        }
        super().__init__(fields)

    def _make_plot(self, timestep, subplot_spec, fig):
        field_data = []
        field_name = []
        field_units = []
        for field, field_args in zip(self._datasets, self._field_arguments):
            fld_data, fld_md = field.get_data(timestep, **field_args)
            field_data.append(fld_data)
            field_name.append(field.get_name())
            field_units.append(fld_md['field']['units'])
        axis_labels = fld_md['field']['axis_labels'][::-1]
        x_units = fld_md['axis'][axis_labels[0]]['units']
        y_units = fld_md['axis'][axis_labels[1]]['units']
        x_label = '${}$ [${}$]'.format(axis_labels[0], x_units)
        y_label = '${}$ [${}$]'.format(axis_labels[1], y_units)
        x_min = fld_md['axis'][axis_labels[0]]['array'][0]
        x_max = fld_md['axis'][axis_labels[0]]['array'][-1]
        y_min = fld_md['axis'][axis_labels[1]]['array'][0]
        y_max = fld_md['axis'][axis_labels[1]]['array'][-1]
        field_plot(field_data, field_name=field_name, field_units=field_units,
                extent=[x_min, x_max, y_min, y_max], xlabel=x_label,
                ylabel=y_label,
                subplot_spec=subplot_spec, fig=fig, **self._plot_arguments)


class ParticlePlot(Subplot):

    def __init__(
        self, species, x='x', y='y', x_units=None, y_units=None,
        q_units=None, time_units=None, cbar=False):
        self._components = [x, y, 'q']
        self._component_units = [x_units, y_units, q_units]
        self._species_parameters = {
            'components_list': self._components,
            'data_units': self._component_units,
            'time_units': time_units
        }
        self._plot_parameters = {
            'cbar': cbar
        }
        super().__init__(species)

    def _make_plot(self, timestep, subplot_spec, fig):
        species = self._datasets[0]
        data = species.get_data(timestep, **self._species_parameters)
        x_name = self._components[0]
        y_name = self._components[1]
        x, x_md = data[x_name]
        y, y_md = data[y_name]
        x_units = x_md['units']
        y_units = y_md['units']
        if 'q' in self._components:
            q, q_md = data[self._components[2]]
            q_units = q_md['units']
        particle_plot(
            x, y, q, x_name=x_name, y_name=y_name, x_units=x_units,
            y_units=y_units, q_units=q_units, subplot_spec=subplot_spec,
            fig=fig, **self._plot_parameters)


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


def add_projection(x, bins, main_ax, subplot_spec, fig, orientation='horizontal'):
    x_proj, x_bins = np.histogram(x, bins=bins)
    x_pos = x_bins[1:] - (x_bins[1]-x_bins[0])

    if orientation == 'horizontal':
        gs_p = gs.GridSpecFromSubplotSpec(
            2, 1, subplot_spec, height_ratios=[1, 0.2])
        ax_p = fig.add_subplot(gs_p[-1])
    elif orientation == 'vertical':
        gs_p = gs.GridSpecFromSubplotSpec(
            1, 2, subplot_spec, width_ratios=[0.2, 1])
        ax_p = fig.add_subplot(gs_p[0])

    ax_p.patch.set_alpha(0)

    if orientation == 'horizontal':
        ax_p.plot(x_pos, x_proj, c='k', lw=0.5, alpha=0.5)
        ax_p.fill_between(x_pos, x_proj, facecolor='tab:gray',
                            alpha=0.3)
        xlim = main_ax.get_xlim()
        ax_p.set_xlim(xlim)
        ylim = list(ax_p.get_ylim())
        ylim[0] = 0
        ax_p.set_ylim(ylim)
    elif orientation == 'vertical':
        ax_p.plot(x_proj, x_pos, c='k', lw=0.5, alpha=0.5)
        ax_p.fill_betweenx(x_pos, x_proj, facecolor='tab:gray',
                            alpha=0.3)
        ylim = main_ax.get_ylim()
        ax_p.set_ylim(ylim)
        xlim = list(ax_p.get_xlim())
        xlim[0] = 0
        ax_p.set_xlim(xlim)
    ax_p.axis('off')
    # ax_p.spines['left'].set_position('zero')
    # ax_p.spines['left'].set_color('tab:grey')
    # ax_p.tick_params(axis='y', colors='tab:grey', labelsize=6,
    #                 direction="in", pad=-4)
    # ax_p.spines['right'].set_color('none')
    # ax_p.spines['top'].set_color('none')
    # ax_p.yaxis.set_ticks_position('left')
    # ax_p.xaxis.set_ticks_position('bottom')
    # ax_p.tick_params(axis='x', which='both', labelbottom=False)
    # for label in ax_p.yaxis.get_ticklabels():
    #     label.set_horizontalalignment('left')
    #     label.set_verticalalignment('bottom')


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


def create_vertical_colorbars(images, labels, subplot_spec, fig=None, n_ticks=3,
                              **kwargs):
    if not isinstance(images, list):
        images = [images]
    if not isinstance(labels, list):
        labels = [labels]
    n_cbars = len(images)
    cbar_gs = gs.GridSpecFromSubplotSpec(
        n_cbars, 1, subplot_spec=subplot_spec, **kwargs)
    if fig is None:
        fig = plt.gcf()
    for image, label, cbar_ss in zip(images, labels, cbar_gs):
        ax = fig.add_subplot(cbar_ss)
        tick_locator = ticker.MaxNLocator(nbins=n_ticks)
        Colorbar(ax, image, ticks=tick_locator, label=label)
