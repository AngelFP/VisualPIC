"""
This file is part of VisualPIC.

The module contains the classes for 2D visualization with matplotlib.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""

import sys

from matplotlib.style import library
from PyQt5 import QtWidgets

from visualpic.ui.basic_plot_window import BasicPlotWindow
from .figure import VPFigure
from .field_subplot import FieldSubplot
from .particle_subplot import ParticlePlot


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
