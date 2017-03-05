# Code from: http://stackoverflow.com/questions/21654008/matplotlib-drag-overlapping-points-interactively

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.lines import Line2D
from matplotlib.figure import Figure


class FigureWithPoints(Figure):
    def __init__(self, figsize = None, dpi = None, facecolor = None, edgecolor = None, linewidth = 0.0, frameon = None, subplotpars = None, tight_layout = None):
        self.listOfPoints = list()
        super().__init__(figsize, dpi, facecolor, edgecolor, linewidth, frameon, subplotpars, tight_layout)
        self.add_subplot(111)
        self.axes[0].set_xlim(0,255)
        self.axes[0].set_ylim(0,1)

    def AddPoints(self, points):
        for point in points:
            dPoint = DraggablePoint(self, point[0], point[1])
            self.listOfPoints.append(dPoint)
            self.axes[0].add_patch(dPoint)
            dPoint.addLinesAndConnect()

    def GetPoints(self):
        points = list()
        for dPoint in self.listOfPoints:
            points.append([dPoint.x, dPoint.y])
        return points


class DraggablePoint(Ellipse):

    lock = None #  only one can be animated at a time
    def __init__(self, parent, x=0.1, y=0.1, size=2):
        super().__init__((x, y), size*3, size/50, fc='r', alpha=0.5, edgecolor='r')
        self.parent = parent
        self.axes = parent.axes[0]
        self.x = x
        self.y = y
        self.background = None

    def addLinesAndConnect(self):
        self.index = self.parent.listOfPoints.index(self)
        if len(self.parent.listOfPoints) > 1:
            lineX = [self.parent.listOfPoints[self.index-1].x, self.x]
            lineY = [self.parent.listOfPoints[self.index-1].y, self.y]

            self.line = Line2D(lineX, lineY, color='r', alpha=0.5)
            self.figure.axes[0].add_line(self.line)
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
        if self.index < len(self.parent.listOfPoints)-1:
            self.parent.listOfPoints[self.index+1].line.set_animated(True)
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
        if self.index < len(self.parent.listOfPoints)-1:
            axes.draw_artist(self.parent.listOfPoints[self.index + 1].line)

        self.x = self.center[0]
        self.y = self.center[1]
        
        if self.index > 0:
            lineX = [self.parent.listOfPoints[self.index - 1].x, self.x]
            lineY = [self.parent.listOfPoints[self.index - 1].y, self.y]
            self.line.set_data(lineX, lineY)

        if self.index < len(self.parent.listOfPoints)-1:
            lineX = [self.x, self.parent.listOfPoints[self.index + 1].x]
            lineY = [self.y, self.parent.listOfPoints[self.index + 1].y]
            self.parent.listOfPoints[self.index + 1].line.set_data(lineX, lineY)

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
        if self.index < len(self.parent.listOfPoints)-1:
            self.parent.listOfPoints[self.index + 1].line.set_animated(False)

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