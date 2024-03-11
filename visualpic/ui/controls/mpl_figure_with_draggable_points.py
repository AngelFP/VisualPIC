"""
This file is part of VisualPIC.

The module contains the class for a matplotlib figure with draggable points.
The code is based on 'http://stackoverflow.com/questions/21654008/'.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""


from matplotlib.patches import Ellipse
from matplotlib.lines import Line2D
from matplotlib.figure import Figure
import numpy as np


class FigureWithDraggablePoints(Figure):

    """
    Figure subclass which can display draggable points joined by lines. It can
    also display a background histogram. This is useful for editing the opacity
    and colormap of volumetric fields.
    """

    def __init__(self, nrows=1, ncols=1, figsize=None, dpi=None,
                 facecolor=None, edgecolor=None, linewidth=0.0, frameon=None,
                 subplotpars=None, tight_layout=None, xlabels=None,
                 ylabels=None, share_x_axis=False, share_y_axis=False,
                 hist=None, hist_edges=None, patch_color='r'):
        """Initialize figure"""
        self.patch_color = patch_color
        self.drag_points = {}
        self.histograms = {}
        super().__init__(
            figsize=figsize, dpi=dpi, facecolor=facecolor,
            edgecolor=edgecolor, linewidth=linewidth,
            frameon=frameon, subplotpars=subplotpars,
            tight_layout=tight_layout)
        self.create_axes(nrows, ncols, xlabels, ylabels, share_x_axis,
                         share_y_axis, hist, hist_edges)

    def create_axes(self, nrows, ncols, xlabels, ylabels, share_x_axis,
                    share_y_axis, hist, hist_edges):
        for i in np.arange(nrows)+1:
            for j in np.arange(ncols)+1:
                n = (i-1)*ncols + j
                ax = self.add_subplot(nrows, ncols, n)
                ax.set_xlim(0, 255)
                ax.set_ylim(0, 1)
                if (share_y_axis
                        and n not in np.arange(0, ncols*nrows, ncols)+1):
                    ax.tick_params(axis='y', which='both', labelleft=False)
                elif share_y_axis:
                    if ylabels is not None:
                        ax.set_ylabel(ylabels[(n-1)/ncols])
                else:
                    if ylabels is not None:
                        ax.set_ylabel(ylabels[n-1])
                if (share_x_axis
                        and n not in np.arange(
                            ncols * nrows - ncols, ncols * nrows) + 1):
                    ax.tick_params(axis='x', which='both', labelbottom=False)
                elif share_x_axis:
                    if xlabels is not None:
                        ax.set_xlabel(xlabels[n-1-ncols*nrows+ncols])
                else:
                    if xlabels is not None:
                        ax.set_xlabel(xlabels[n-1])
                if hist is not None:
                    self.plot_histogram(n-1, hist_edges, hist)

    def plot_histogram(self, naxes, hist_edges, hist):
        hist_width = 256/len(hist)
        if naxes not in self.histograms:
            self.histograms[naxes] = self.axes[naxes].bar(
                hist_edges[:-1], hist, width=hist_width, facecolor="#dbdbdb",
                align="edge")
        else:
            for i, rect in enumerate(self.histograms[naxes]):
                rect.set_height(hist[i])
                rect.set_x(hist_edges[i])
            if naxes == len(self.histograms)-1:
                self.canvas.draw()

    def set_points(self, naxis, x, y):
        self.remove_points(naxis)
        self.add_points(naxis, x, y)
        self.canvas.draw_idle()

    def add_points(self, naxis, x, y):
        self.drag_points[naxis] = list()
        if isinstance(self.patch_color, list):
            p_color = self.patch_color[naxis]
        else:
            p_color = self.patch_color
        for i in np.arange(len(x)):
            dPoint = DraggablePoint(
                self, naxis, x[i], y[i], 0.05, color=p_color)
            self.drag_points[naxis].append(dPoint)
            self.axes[naxis].add_patch(dPoint)
            dPoint.addLinesAndConnect()

    def remove_points(self, naxis):
        if naxis in self.drag_points:
            for point in reversed(self.drag_points[naxis]):
                if type(point) is DraggablePoint:
                    point.remove()
            for line in reversed(self.axes[naxis].lines):
                line.remove()

    def set_axes_labels(self, naxes, axis, label_pos, labels):
        if axis == "x":
            self.axes[naxes].set_xticks(label_pos)
            self.axes[naxes].set_xticklabels(labels)
        elif axis == "y":
            self.axes[naxes].set_yticks(label_pos)
            self.axes[naxes].set_yticklabels(labels)
        self.canvas.draw()

    def get_points(self, naxis):
        x = list()
        y = list()
        for dPoint in self.drag_points[naxis]:
            x.append(dPoint.x)
            y.append(dPoint.y)
        return np.array(x), np.array(y)


class DraggablePoint(Ellipse):

    lock = None  # only one can be animated at a time

    def __init__(self, parent_figure, naxes, x=0.1, y=0.1, size_y=2,
                 color='r'):
        self.parent_figure = parent_figure
        self.naxes = naxes
        self.x = x
        self.y = y
        self.color = color
        self.background = None
        size_x = self.determine_proportional_x_size(size_y)
        size_x, size_y = self.get_scaled_size(size_x, size_y)
        super().__init__((x, y), size_x, size_y, fc=self.color, alpha=0.5,
                         edgecolor=self.color)

    def determine_proportional_x_size(self, y_size):
        x_min, x_max = self.parent_figure.axes[self.naxes].get_xlim()
        y_min, y_max = self.parent_figure.axes[self.naxes].get_ylim()
        ax_width_range = x_max - x_min
        ax_height_range = y_max - y_min
        ax_width = self.parent_figure.axes[self.naxes].get_window_extent(
        ).width
        ax_height = self.parent_figure.axes[self.naxes].get_window_extent(
        ).height
        coef = (ax_width_range/ax_width) * (ax_height/ax_height_range)
        size_x = y_size * coef
        return size_x

    def get_scaled_size(self, size_x, size_y):
        standard_height = 800
        ax_height = self.parent_figure.axes[self.naxes].get_window_extent(
        ).height
        coef = ax_height/standard_height
        return size_x/coef, size_y/coef

    def addLinesAndConnect(self):
        self.index = self.parent_figure.drag_points[self.naxes].index(self)
        if len(self.parent_figure.drag_points[self.naxes]) > 1:
            lineX = [self.parent_figure.drag_points[self.naxes]
                     [self.index-1].x, self.x]
            lineY = [self.parent_figure.drag_points[self.naxes]
                     [self.index-1].y, self.y]

            self.line = Line2D(lineX, lineY, color=self.color, alpha=0.5)
            self.parent_figure.axes[self.naxes].add_line(self.line)
        self.connect()

    def connect(self):
        'connect to all the events we need'

        self.cidpress = self.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = self.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)

    def on_press(self, event):

        if event.inaxes != self.axes:
            return
        if DraggablePoint.lock is not None:
            return
        contains, attrd = self.contains(event)
        if not contains:
            return
        self.press = (self.center), event.xdata, event.ydata
        DraggablePoint.lock = self

        # draw everything but the selected rectangle and store the pixel buffer
        canvas = self.figure.canvas
        axes = self.axes
        self.set_animated(True)
        if self.index > 0:
            self.line.set_animated(True)
        if self.index < len(self.parent_figure.drag_points[self.naxes])-1:
            self.parent_figure.drag_points[
                self.naxes][self.index + 1].line.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.axes.bbox)

        # now redraw just the rectangle
        axes.draw_artist(self)

        # and blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_motion(self, event):

        if DraggablePoint.lock is not self:
            return
        if event.inaxes != self.axes:
            return
        self.center, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.center = (self.center[0]+dx, self.center[1]+dy)

        canvas = self.figure.canvas
        axes = self.axes
        # restore the background region
        canvas.restore_region(self.background)

        # redraw just the current rectangle
        axes.draw_artist(self)
        if self.index > 0:
            axes.draw_artist(self.line)
        if self.index < len(self.parent_figure.drag_points[self.naxes])-1:
            axes.draw_artist(
                self.parent_figure.drag_points[self.naxes][
                    self.index + 1].line)

        self.x = self.center[0]
        self.y = self.center[1]

        if self.index > 0:
            lineX = [self.parent_figure.drag_points[self.naxes]
                     [self.index - 1].x, self.x]
            lineY = [self.parent_figure.drag_points[self.naxes]
                     [self.index - 1].y, self.y]
            self.line.set_data(lineX, lineY)

        if self.index < len(self.parent_figure.drag_points[self.naxes])-1:
            lineX = [self.x, self.parent_figure.drag_points[self.naxes]
                     [self.index + 1].x]
            lineY = [self.y, self.parent_figure.drag_points[self.naxes]
                     [self.index + 1].y]
            self.parent_figure.drag_points[
                self.naxes][self.index + 1].line.set_data(lineX, lineY)

        # blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_release(self, event):
        'on release we reset the press data'
        if DraggablePoint.lock is not self:
            return

        self.press = None
        DraggablePoint.lock = None

        # turn off the rect animation property and reset the background
        self.set_animated(False)
        if self.index > 0:
            self.line.set_animated(False)
        if self.index < len(self.parent_figure.drag_points[self.naxes])-1:
            self.parent_figure.drag_points[
                self.naxes][self.index + 1].line.set_animated(False)

        self.background = None

        # redraw the full figure
        self.figure.canvas.draw()

        self.x = self.center[0]
        self.y = self.center[1]

    def disconnect(self):
        'disconnect all the stored connection ids'

        self.figure.canvas.mpl_disconnect(self.cidpress)
        self.figure.canvas.mpl_disconnect(self.cidrelease)
        self.figure.canvas.mpl_disconnect(self.cidmotion)
