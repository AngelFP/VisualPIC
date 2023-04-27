"""
This file is part of VisualPIC.

The module contains the classes for 2D visualization with matplotlib.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""

import sys

try:
    from PyQt5 import QtWidgets
    qt_installed = True
except:
    qt_installed = False

if qt_installed:
    from visualpic.ui.basic_plot_window import BasicPlotWindow
from .plot_containers import VPFigure, FieldSubplot, ParticleSubplot
from .rc_params import rc_params


class MplVisualizer():
    """Class taking care of visualizing the data with matplotlib."""

    def __init__(self):
        self._figure_list = []
        self._current_figure = None

    def figure(self, fig_idx=None):
        """Set current figure in which to plot.

        Parameters
        ----------
        fig_idx : int, optional
            Index of the figure, by default None

        Returns
        -------
        VPFigure
        """
        if fig_idx is not None:
            n_figs = len(self._figure_list)
            if n_figs < fig_idx + 1:
                for i in range(fig_idx + 1 - n_figs):
                    self._figure_list.append(VPFigure(rc_params=rc_params))
            fig = self._figure_list[fig_idx]
        else:
            fig = VPFigure(rc_params=rc_params)
            self._figure_list.append(fig)
        self._set_current_figure(fig)
        return fig

    def field_plot(
            self, field, field_units=None, axes_units=None, time_units=None,
            slice_dir=None, slice_pos=0.5, m='all', theta=0., vmin=None,
            vmax=None, cmap=None, stacked=True, cbar=True):
        """Add a field plot to the figure.

        Parameters
        ----------
        field : Field or list of Fields
            The VisualPIC field(s) to plot.
        field_units : str, optional
            Desired field units, by default None
        axes_units : str, optional
            Desired axes units, by default None
        time_units : str, optional
            Desired time units, by default None
        slice_dir : str, optional
            Direction along which to slice the field, by default None
        slice_pos : float, optional
            Location of the slice in the `slice_dir` axes. Value between
            0 an 1, by default 0.5.
        m : str or int, optional
            For fields in `thetaMode` geometry, azimuthal mode to show, by
            default 'all'.
        theta : float, optional
            For fields in `thetaMode` geometry, angle at which to show the
            fields, by default 0.
        vmin : float or list of floats, optional
            Minimum of the colormap range.
        vmax : float or list of floats, optional
            Maximum of the colormap range.
        cmap : str or matplotlib Colormap, or a list of them.
            The colormap to use for each field.
        stacked : bool, optional
            Whether to stack the all fields in the same axes (on top of each
            other) or show them in individual axes, by default True.
        cbar : bool, optional
            Whether to include a colorbar, by default True.
        """
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
        """Add a particle plot to the figure.

        Parameters
        ----------
        species : Species
            The VisualPIC species to show.
        x : str, optional
            Name of the coordinate plotted in the x axis, by default 'x'
        y : str, optional
            Name of the coordinate plotted in the y axis, by default 'y'
        x_units : str, optional
            Units of the x coordinate
        y_units : str, optional
            Units of the x coordinate
        q_units : str, optional
            Units of the particle charge
        time_units : str, optional
            Units of the time.
        cbar : bool, optional
            Whether to show a colorbar, by default True
        """
        fig = self._get_current_figure()
        subplot = ParticleSubplot(
            species, x=x, y=y, x_units=x_units, y_units=y_units,
            q_units=q_units, time_units=time_units, cbar=cbar)
        fig.add_subplot(subplot)

    def show(self, timestep=0, ts_is_index=True):
        """Show figure(s).

        Parameters
        ----------
        timestep : int, optional
            Time step at which to show the data, by default 0
        ts_is_index : bool
            Indicates whether the value provided in 'timestep' is the index of
            the time step (True) or the numerical value of the time step
            (False).
        """
        # Check if pyqt5 is installed.
        if not qt_installed:
            raise ModuleNotFoundError(
                "Cannot show visualizer because PyQt5 is not installed. "
                "Please install by running `python -m pip install pyqt5`.")
        # Show window.
        app = QtWidgets.QApplication(sys.argv)
        for figure in self._figure_list:
            figure.generate(timestep, ts_is_index)
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
