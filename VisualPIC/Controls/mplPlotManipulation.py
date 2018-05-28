# Code based on: http://stackoverflow.com/questions/21654008/matplotlib-drag-overlapping-points-interactively

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.lines import Line2D
from matplotlib.figure import Figure
import numpy as np


class FigureWithPoints(Figure):
    def __init__(self, nrows=1, ncols=1, figsize = None, dpi = None, facecolor = None, edgecolor = None, linewidth = 0.0, frameon = None, subplotpars = None, tight_layout = None):
        super().__init__(figsize, dpi, facecolor, edgecolor, linewidth, frameon, subplotpars, tight_layout)
        for i in np.arange(nrows)+1:
            for j in np.arange(ncols)+1:
                n = (i-1)*ncols + j
                self.add_subplot(nrows, ncols, n)
        for ax in self.axes:
            ax.set_xlim(0,255)
            ax.set_ylim(0,1)

    def set_points(self, naxis, x, y):
        self.remove_points(naxis)
        self.add_points(naxis, x, y)
        self.canvas.draw_idle()

    def add_points(self, naxis, x, y):
        for i in np.arange(len(x)):
            dPoint = DraggablePoint(self.axes[naxis], x[i], y[i], 0.05)
            self.axes[naxis].add_patch(dPoint)
            dPoint.addLinesAndConnect()

    def remove_points(self, naxis):
        for point in reversed(self.axes[naxis].patches):
            point.remove()
        self.axes[naxis].clear()

    def remove_all_points(self):
        for ax in self.axes:
            for point in reversed(ax.patches):
                point.remove()
            ax.clear()
        self.canvas.draw_idle()

    def GetPoints(self, naxis):
        x = list()
        y = list()
        for dPoint in self.axes[naxis].patches:
            x.append(dPoint.x)
            y.append(dPoint.y)
        return np.array(x), np.array(y)


class DraggablePoint(Ellipse):

    lock = None #  only one can be animated at a time
    def __init__(self, parent_axes, x=0.1, y=0.1, size_y=2):
        self.parent_axes = parent_axes
        self.x = x
        self.y = y
        self.background = None
        size_x = self.determine_proportional_x_size(size_y)
        size_x, size_y = self.get_scaled_size(size_x, size_y)
        super().__init__((x, y), size_x, size_y, fc='r', alpha=0.5, edgecolor='r')

    def determine_proportional_x_size(self, y_size):
        x_min, x_max = self.parent_axes.get_xlim()
        y_min, y_max = self.parent_axes.get_ylim()
        ax_width_range = x_max - x_min
        ax_height_range = y_max - y_min
        ax_width = self.parent_axes.get_window_extent().width
        ax_height = self.parent_axes.get_window_extent().height
        coef = (ax_width_range/ax_width) * (ax_height/ax_height_range)
        size_x = y_size * coef
        return size_x

    def get_scaled_size(self, size_x, size_y):
        standard_height = 800
        ax_height = self.parent_axes.get_window_extent().height
        coef = ax_height/standard_height
        return size_x/coef, size_y/coef


    def addLinesAndConnect(self):
        self.index = self.parent_axes.patches.index(self)
        if len(self.parent_axes.patches) > 1:
            lineX = [self.parent_axes.patches[self.index-1].x, self.x]
            lineY = [self.parent_axes.patches[self.index-1].y, self.y]

            self.line = Line2D(lineX, lineY, color='r', alpha=0.5)
            self.parent_axes.add_line(self.line)
        self.connect()

    def connect(self):

        'connect to all the events we need'

        self.cidpress = self.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):

        if event.inaxes != self.axes: return
        if DraggablePoint.lock is not None: return
        contains, attrd = self.contains(event)
        if not contains: return
        self.press = (self.center), event.xdata, event.ydata
        DraggablePoint.lock = self

        # draw everything but the selected rectangle and store the pixel buffer
        canvas = self.figure.canvas
        axes = self.axes
        self.set_animated(True)
        if self.index > 0:
            self.line.set_animated(True)
        if self.index < len(self.parent_axes.patches)-1:
            self.parent_axes.patches[self.index+1].line.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.axes.bbox)

        # now redraw just the rectangle
        axes.draw_artist(self)

        # and blit just the redrawn area
        canvas.blit(axes.bbox)


    def on_motion(self, event):

        if DraggablePoint.lock is not self:
            return
        if event.inaxes != self.axes: return
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
        if self.index < len(self.parent_axes.patches)-1:
            axes.draw_artist(self.parent_axes.patches[self.index + 1].line)

        self.x = self.center[0]
        self.y = self.center[1]
        
        if self.index > 0:
            lineX = [self.parent_axes.patches[self.index - 1].x, self.x]
            lineY = [self.parent_axes.patches[self.index - 1].y, self.y]
            self.line.set_data(lineX, lineY)

        if self.index < len(self.parent_axes.patches)-1:
            lineX = [self.x, self.parent_axes.patches[self.index + 1].x]
            lineY = [self.y, self.parent_axes.patches[self.index + 1].y]
            self.parent_axes.patches[self.index + 1].line.set_data(lineX, lineY)

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
        if self.index < len(self.parent_axes.patches)-1:
            self.parent_axes.patches[self.index + 1].line.set_animated(False)

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