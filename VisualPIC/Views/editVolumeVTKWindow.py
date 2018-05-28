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
from VisualPIC.Views.SaveOpacityDialog import SaveOpacityDialog
from VisualPIC.Views.SaveColormapDialog import SaveColormapDialog


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
        self.register_ui_events()
        self.create_canvas_and_figure()
        self.fill_ui()

    def create_canvas_and_figure(self):
        self.opacity_figure = FigureWithPoints(1,1)
        self.opacity_figure.patch.set_facecolor("white")
        self.opacity_canvas = FigureCanvas(self.opacity_figure)
        self.opacityWidgetLayout.addWidget(self.opacity_canvas)
        self.opacity_canvas.draw()
        self.cmap_figure = FigureWithPoints(3,1)
        self.cmap_figure.patch.set_facecolor("white")
        self.cmap_canvas = FigureCanvas(self.cmap_figure)
        self.colorsWidgetLayout.addWidget(self.cmap_canvas)
        self.cmap_canvas.draw()
        
        x, y = self.volume.get_opacity_values()
        self.opacity_figure.set_points(0, x, y)

        fld_val, r_val, g_val, b_val = self.volume.get_cmap_values()
        self.cmap_figure.set_points(0, fld_val, r_val)
        self.cmap_figure.set_points(1, fld_val, g_val)
        self.cmap_figure.set_points(2, fld_val, b_val)

    def register_ui_events(self):
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.UpdateVolumeProperties)
        self.normalizationButton.clicked.connect(self.NormalizationButton_Clicked)
        self.norm_pushButton.clicked.connect(self.CustomNormalizationButton_Clicked)
        self.cmap_comboBox.currentIndexChanged.connect(self.set_cmap_from_combobox)
        self.opacity_comboBox.currentIndexChanged.connect(self.set_opacity_from_combobox)
        self.save_opacity_pushButton.clicked.connect(self.save_opacity)
        self.import_opacity_pushButton.clicked.connect(self.import_opacity_from_file)
        self.save_cmap_pushButton.clicked.connect(self.save_cmap)
        self.import_cmap_pushButton.clicked.connect(self.import_cmap_from_file)

    def fill_ui(self):
        self.update_list_of_cmaps()
        self.update_list_of_opacities()

    def update_list_of_cmaps(self):
        self.is_updating_ui = True
        self.cmap_comboBox.clear()
        self.cmap_comboBox.addItems(self.get_cmap_list())
        self.is_updating_ui = False

    def get_cmap_list(self):
        op_list = self.cmap_handler.get_available_cmaps()
        op_list.insert(0, "Current colormap")
        return op_list

    def update_list_of_opacities(self):
        self.is_updating_ui = True
        self.opacity_comboBox.clear()
        self.opacity_comboBox.addItems(self.get_opacity_list())
        self.is_updating_ui = False

    def get_opacity_list(self):
        op_list = self.cmap_handler.get_available_opacities()
        op_list.insert(0, "Current opacity")
        return op_list

    def import_opacity_from_file(self):
        home_path = str(Path.home())
        file_path = QFileDialog.getOpenFileName(
            self, "Select file to open:", home_path, "Data files (*.h5)")
        file_path = file_path[0]
        if file_path != "":
            self.cmap_handler.add_opacity_from_file(file_path)
            self.update_list_of_opacities()
            self.opacity_comboBox.setCurrentIndex(
                self.opacity_comboBox.count() - 1)

    def import_cmap_from_file(self):
        home_path = str(Path.home())
        file_path = QFileDialog.getOpenFileName(
            self, "Select file to open:", home_path, "Data files (*.h5)")
        file_path = file_path[0]
        if file_path != "":
            self.cmap_handler.add_cmap_from_file(file_path)
            self.update_list_of_cmaps()
            self.cmap_comboBox.setCurrentIndex(
                self.cmap_comboBox.count() - 1)
    
    def set_cmap_from_combobox(self):
        if not self.is_updating_ui:
            cmap_name = self.cmap_comboBox.currentText()
            if cmap_name != "Current colormap":
                fld_val, r_val, g_val, b_val = self.cmap_handler.get_cmap_data(
                    cmap_name)
            else:
                fld_val, r_val, g_val, b_val = self.volume.get_cmap_values()
            self.cmap_figure.set_points(0, fld_val, r_val)
            self.cmap_figure.set_points(1, fld_val, g_val)
            self.cmap_figure.set_points(2, fld_val, b_val)

    def set_opacity_from_combobox(self):
        if not self.is_updating_ui:
            op_name = self.opacity_comboBox.currentText()
            if op_name != "Current opacity":
                fld_val, op_val = self.cmap_handler.get_opacity_data(op_name)
            else:
                fld_val, op_val = self.volume.get_opacity_values()
            self.opacity_figure.set_points(0, fld_val, op_val)

    def save_opacity(self):
        fld_val, op_val = self.opacity_figure.GetPoints(0)
        op_dialog = SaveOpacityDialog(fld_val, op_val)
        op_dialog.exec_()

    def save_cmap(self):
        fld_val, r_val = self.cmap_figure.GetPoints(0)
        fld_val, g_val = self.cmap_figure.GetPoints(1)
        fld_val, b_val = self.cmap_figure.GetPoints(2)
        cmap_dialog = SaveColormapDialog(fld_val, r_val, g_val, b_val)
        cmap_dialog.exec_()

    def UpdateVolumeProperties(self):
        fld_val_op, op_val = self.opacity_figure.GetPoints(0)
        fld_val_cmap, r_val = self.cmap_figure.GetPoints(0)
        fld_val_cmap, g_val = self.cmap_figure.GetPoints(1)
        fld_val_cmap, b_val = self.cmap_figure.GetPoints(2)
        self.volume.set_opacity(fld_val_op, op_val)
        self.volume.set_cmap(fld_val_cmap, r_val, g_val, b_val)
        self.mainWindow.UpdateRender()

    def NormalizationButton_Clicked(self):
        timeStep = self.mainWindow.GetCurrentTimeStep()
        self.volume.SetCMapRangeFromCurrentTimeStep(timeStep)

    def CustomNormalizationButton_Clicked(self):
        min = float(self.min_lineEdit.text())
        max = float(self.max_lineEdit.text())
        self.volume.SetCMapRange(min, max)