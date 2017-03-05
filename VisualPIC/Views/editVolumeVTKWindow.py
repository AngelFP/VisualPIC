# -*- coding: utf-8 -*-

#Copyright 2016-2017 Angel Ferran Pousa
#
#This file is part of VisualPIC.
#
#VisualPIC is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#VisualPIC is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with VisualPIC.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os

from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QDialogButtonBox
import matplotlib.patches as patches
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas)

from VisualPIC.Controls.mplPlotManipulation import FigureWithPoints


if getattr(sys, 'frozen', False):
    # we are running in a bundle
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
guipath = os.path.join( bundle_dir, 'editVolumeVTKWindow.ui' )
Ui_EditVolumeVTKWindow, QEditVolumeVTKWindow = loadUiType(guipath)

class EditVolumeVTKWindow(QEditVolumeVTKWindow, Ui_EditVolumeVTKWindow):
    def __init__(self, volume, parent=None):
        super(EditVolumeVTKWindow, self).__init__()
        self.setupUi(self)
        self.mainWindow = parent
        self.volume = volume
        self.RegisterUIEvents()
        self.CreateCanvasAndFigure()

    def CreateCanvasAndFigure(self):
        self.opacityFigure = FigureWithPoints()
        self.opacityFigure.patch.set_facecolor("white")
        self.opacityCanvas = FigureCanvas(self.opacityFigure)
        self.opacityWidgetLayout.addWidget(self.opacityCanvas)
        self.opacityCanvas.draw()
        self.colorsFigure = FigureWithPoints()
        self.colorsFigure.patch.set_facecolor("white")
        self.colorsCanvas = FigureCanvas(self.colorsFigure)
        self.colorsWidgetLayout.addWidget(self.colorsCanvas)
        self.colorsCanvas.draw()
        
        points = self.volume.GetOpacityValues()
        self.opacityFigure.AddPoints(points)

    def RegisterUIEvents(self):
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.UpdateVolumeProperties)

    def UpdateVolumeProperties(self):
        self.volume.SetOpacityValues(self.opacityFigure.GetPoints())
        self.mainWindow.UpdateRender()