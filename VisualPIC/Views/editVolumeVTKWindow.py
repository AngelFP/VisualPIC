# -*- coding: utf-8 -*-

#Copyright 2016-2018 Angel Ferran Pousa, DESY
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
from VisualPIC.DataPlotting.vtkColorMaps import VTKColorMapCreator


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
        self.cmap_handler = volume.cmap_handler
        self.RegisterUIEvents()
        self.CreateCanvasAndFigure()
        self.FillUI()

    def CreateCanvasAndFigure(self):
        self.opacityFigure = FigureWithPoints(1,1)
        self.opacityFigure.patch.set_facecolor("white")
        self.opacityCanvas = FigureCanvas(self.opacityFigure)
        self.opacityWidgetLayout.addWidget(self.opacityCanvas)
        self.opacityCanvas.draw()
        self.colorsFigure = FigureWithPoints(3,1)
        self.colorsFigure.patch.set_facecolor("white")
        self.colorsCanvas = FigureCanvas(self.colorsFigure)
        self.colorsWidgetLayout.addWidget(self.colorsCanvas)
        self.colorsCanvas.draw()
        
        x, y = self.volume.GetOpacityValues()
        self.opacityFigure.set_points(0, x, y)

    def RegisterUIEvents(self):
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.UpdateVolumeProperties)
        self.normalizationButton.clicked.connect(self.NormalizationButton_Clicked)
        self.norm_pushButton.clicked.connect(self.CustomNormalizationButton_Clicked)
        self.colorMap_comboBox.currentIndexChanged.connect(self.SetColorMap)
        self.opacity_comboBox.currentIndexChanged.connect(self.set_opacity_from_combobox)

    def FillUI(self):
        self.isUpdatingUI = True
        self.colorMap_comboBox.clear()
        self.colorMap_comboBox.addItems(VTKColorMapCreator.GetColorMapListOfNames())
        self.opacity_comboBox.addItems(self.cmap_handler.get_available_opacities())
        self.isUpdatingUI = False

    def SetColorMap(self):
        if not self.isUpdatingUI:
            cmapPoints = VTKColorMapCreator.GetColorMapPoints(self.colorMap_comboBox.currentText())
            self.volume.SetColorPoints(cmapPoints)
            self.mainWindow.UpdateRender()

    def set_opacity_from_combobox(self):
        if not self.isUpdatingUI:
            op_name = self.opacity_comboBox.currentText()
            fld_val, op_val = self.cmap_handler.get_opacity_data(op_name)
            self.opacityFigure.set_points(0, fld_val, op_val)

    def greenColor(self):
        self.volume.SetGreenColor()
        self.mainWindow.UpdateRender()

    def blueColor(self):
        self.volume.SetViridis()
        self.mainWindow.UpdateRender()
        #End of temporary code

    def UpdateVolumeProperties(self):
        fld_val, op_val = self.opacityFigure.GetPoints(0)
        self.volume.SetOpacityValues(fld_val, op_val)
        self.mainWindow.UpdateRender()

    def NormalizationButton_Clicked(self):
        timeStep = self.mainWindow.GetCurrentTimeStep()
        self.volume.SetCMapRangeFromCurrentTimeStep(timeStep)

    def CustomNormalizationButton_Clicked(self):
        min = float(self.min_lineEdit.text())
        max = float(self.max_lineEdit.text())
        self.volume.SetCMapRange(min, max)