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

import numpy as np
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
        self.main_window = parent
        self.volume = volume
        self.cmap_handler = volume.cmap_handler
        self.register_ui_events()
        self.create_canvas_and_figure()
        self.register_time_step_events()
        self.fill_ui()

    def closeEvent(self, *args, **kwargs):
        self.unregister_time_step_events()
        super(EditVolumeVTKWindow, self).closeEvent(*args, **kwargs)

    def create_canvas_and_figure(self):
        time_step = self.main_window.get_current_time_step()
        hist, hist_edges = self.volume.get_field_histogram(time_step)
        fld_name = self.volume.get_field_name()
        fld_units = self.volume.get_field_units()
        xlabel = fld_name + " [$" + fld_units + "$]"
        self.opacity_figure = FigureWithPoints(1, 1, hist=hist,
                                               hist_edges=hist_edges,
                                               patch_color='tab:blue',
                                               xlabels=[xlabel],
                                               ylabels=["Opacity"])
        self.opacity_figure.patch.set_facecolor("white")
        self.opacity_canvas = FigureCanvas(self.opacity_figure)
        self.opacityWidgetLayout.addWidget(self.opacity_canvas)
        self.opacity_canvas.draw()
        self.cmap_figure = FigureWithPoints(3, 1, hist=hist,
                                            hist_edges=hist_edges,
                                            share_x_axis=True,
                                            patch_color=['r', 'g', 'b'],
                                            xlabels=[xlabel],
                                            ylabels=["Red", "Green", "Blue"])
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
        self.set_axes_range(time_step)
        self.set_range_in_line_edits(time_step)

    def set_axes_range(self, time_step):
        nels = 5
        label_pos = np.linspace(0, 255, nels)
        labels_array = self.volume.get_field_range(time_step, 5)
        labels_list = labels_array.tolist()
        labels = [format(label, '.2e') for label in labels_list]
        self.opacity_figure.set_axes_labels(0, "x", label_pos, labels)
        self.cmap_figure.set_axes_labels(2, "x", label_pos, labels)

    def register_time_step_events(self):
        self.main_window.bind_time_step_to(self.set_histograms)
        self.main_window.bind_time_step_to(self.set_axes_range)
        self.main_window.bind_time_step_to(self.set_range_in_line_edits)

    def unregister_time_step_events(self):
        self.main_window.unbind_time_step_to(self.set_histograms)
        self.main_window.unbind_time_step_to(self.set_axes_range)
        self.main_window.unbind_time_step_to(self.set_range_in_line_edits)

    def set_histograms(self, time_step):
        hist, hist_edges = self.volume.get_field_histogram(time_step)
        self.opacity_figure.plot_histogram(0, hist_edges, hist)
        self.cmap_figure.plot_histogram(0, hist_edges, hist)
        self.cmap_figure.plot_histogram(1, hist_edges, hist)
        self.cmap_figure.plot_histogram(2, hist_edges, hist)

    def register_ui_events(self):
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(
            self.update_volume_properties)
        self.norm_pushButton.clicked.connect(self.range_button_clicked)
        self.optimize_pushButton.clicked.connect(self.get_optimized_opacity)
        self.cmap_comboBox.currentIndexChanged.connect(
            self.set_cmap_from_combobox)
        self.opacity_comboBox.currentIndexChanged.connect(
            self.set_opacity_from_combobox)
        self.save_opacity_pushButton.clicked.connect(self.save_opacity)
        self.import_opacity_pushButton.clicked.connect(
            self.import_opacity_from_file)
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

    def set_range_in_line_edits(self, time_step):
        labels_array = self.volume.get_field_range(time_step, 2)
        labels_list = labels_array.tolist()
        self.min_lineEdit.setText(format(labels_list[0], '.2e'))
        self.max_lineEdit.setText(format(labels_list[1], '.2e'))

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

    def get_optimized_opacity(self):
        time_step = self.main_window.get_current_time_step()
        fld_val, op_val = self.volume.get_optimized_opacity(time_step)
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

    def update_volume_properties(self):
        fld_val_op, op_val = self.opacity_figure.GetPoints(0)
        fld_val_cmap, r_val = self.cmap_figure.GetPoints(0)
        fld_val_cmap, g_val = self.cmap_figure.GetPoints(1)
        fld_val_cmap, b_val = self.cmap_figure.GetPoints(2)
        self.volume.set_opacity(fld_val_op, op_val)
        self.volume.set_cmap(fld_val_cmap, r_val, g_val, b_val)
        self.main_window.update_render()
        
    def range_button_clicked(self):
        min_val = float(self.min_lineEdit.text())
        max_val = float(self.max_lineEdit.text())
        self.set_field_range(min_val, max_val)

    def set_field_range(self, min_val, max_val):
        time_step = self.main_window.get_current_time_step()
        self.volume.set_cmap_range(min_val, max_val)
        self.main_window.make_render()
        self.set_axes_range(time_step)
        self.set_histograms(time_step)
        self.set_range_in_line_edits(time_step)
