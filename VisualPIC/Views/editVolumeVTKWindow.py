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
from pathlib import Path

from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QDialogButtonBox, QFileDialog
import matplotlib.patches as patches
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas)

from VisualPIC.Controls.mplPlotManipulation import FigureWithPoints
from VisualPIC.DataPlotting.vtkColorMaps import VTKColorMapCreator
from VisualPIC.Views.SaveOpacityDialog import SaveOpacityDialog


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
        self.fill_ui()

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
        
        x, y = self.volume.get_opacity_values()
        self.opacityFigure.set_points(0, x, y)

    def RegisterUIEvents(self):
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.UpdateVolumeProperties)
        self.normalizationButton.clicked.connect(self.NormalizationButton_Clicked)
        self.norm_pushButton.clicked.connect(self.CustomNormalizationButton_Clicked)
        self.colorMap_comboBox.currentIndexChanged.connect(self.SetColorMap)
        self.opacity_comboBox.currentIndexChanged.connect(self.set_opacity_from_combobox)
        self.save_opacity_pushButton.clicked.connect(self.save_opacity)
        self.import_pushButton.clicked.connect(self.import_from_file)

    def fill_ui(self):
        self.update_list_of_colormaps()
        self.update_list_of_opacities()

    def update_list_of_colormaps(self):
        self.isUpdatingUI = True
        self.colorMap_comboBox.clear()
        self.colorMap_comboBox.addItems(VTKColorMapCreator.GetColorMapListOfNames())
        self.isUpdatingUI = False

    def update_list_of_opacities(self):
        self.isUpdatingUI = True
        self.opacity_comboBox.clear()
        self.opacity_comboBox.addItems(self.get_opacity_list())
        self.isUpdatingUI = False

    def import_from_file(self):
        home_path = str(Path.home())
        file_path = QFileDialog.getOpenFileName(
            self, "Select file to open:", home_path, "Data files (*.h5)")
        file_path = file_path[0]
        if file_path != "":
            self.cmap_handler.add_opacity_from_file(file_path)
            self.update_list_of_opacities()
            self.opacity_comboBox.setCurrentIndex(
                self.opacity_comboBox.count() - 1)

    def get_opacity_list(self):
        op_list = self.cmap_handler.get_available_opacities()
        op_list.insert(0, "Current opacity")
        return op_list

    def SetColorMap(self):
        if not self.isUpdatingUI:
            cmapPoints = VTKColorMapCreator.GetColorMapPoints(self.colorMap_comboBox.currentText())
            self.volume.SetColorPoints(cmapPoints)
            self.mainWindow.UpdateRender()

    def set_opacity_from_combobox(self):
        if not self.isUpdatingUI:
            op_name = self.opacity_comboBox.currentText()
            if op_name != "Current opacity":
                fld_val, op_val = self.cmap_handler.get_opacity_data(op_name)
            else:
                fld_val, op_val = self.volume.get_opacity_values()
            self.opacityFigure.set_points(0, fld_val, op_val)

    def save_opacity(self):
        fld_val, op_val = self.opacityFigure.GetPoints(0)
        op_dialog = SaveOpacityDialog(fld_val, op_val)
        op_dialog.exec_()

    def greenColor(self):
        self.volume.SetGreenColor()
        self.mainWindow.UpdateRender()

    def blueColor(self):
        self.volume.SetViridis()
        self.mainWindow.UpdateRender()
        #End of temporary code

    def UpdateVolumeProperties(self):
        fld_val, op_val = self.opacityFigure.GetPoints(0)
        self.volume.set_opacity(fld_val, op_val)
        self.mainWindow.UpdateRender()

    def NormalizationButton_Clicked(self):
        timeStep = self.mainWindow.GetCurrentTimeStep()
        self.volume.SetCMapRangeFromCurrentTimeStep(timeStep)

    def CustomNormalizationButton_Clicked(self):
        min = float(self.min_lineEdit.text())
        max = float(self.max_lineEdit.text())
        self.volume.SetCMapRange(min, max)