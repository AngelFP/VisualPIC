"""
This file is part of VisualPIC.

The module contains the class for the Qt dialog for editing the visual 3D
field properties.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""


import sys
import os
from pathlib import Path

import numpy as np
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QDialogButtonBox, QFileDialog
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas)

from visualpic.ui.controls.mpl_figure_with_draggable_points import (
    FigureWithDraggablePoints)
from visualpic.ui.save_colormap_dialog import SaveColormapDialog
from visualpic.ui.save_opacity_dialog import SaveOpacityDialog
from visualpic.visualization.volume_appearance import Opacity, Colormap


if getattr(sys, 'frozen', False):
    # we are running in a bundle
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
guipath = os.path.join(bundle_dir, 'setup_field_volume_window.ui')
UI_SetupFieldVolumeWindow, QSetupFieldVolumeWindow = loadUiType(guipath)


class SetupFieldVolumeWindow(QSetupFieldVolumeWindow,
                             UI_SetupFieldVolumeWindow):
    def __init__(self, volume, parent=None):
        super(SetupFieldVolumeWindow, self).__init__(parent=parent)
        self.setupUi(self)
        self.setWindowTitle('Edit field ({})'.format(volume.get_name()))
        self.histogram_bins = 50
        self.main_window = parent
        self.volume = volume
        self.style_handler = volume.style_handler
        self.register_ui_events()
        self.create_canvas_and_figure()
        self.fill_ui()

    def showEvent(self, *args, **kwargs):
        self.register_time_step_events()
        super(SetupFieldVolumeWindow, self).showEvent(*args, **kwargs)

    def closeEvent(self, *args, **kwargs):
        self.unregister_time_step_events()
        super(SetupFieldVolumeWindow, self).closeEvent(*args, **kwargs)

    def create_canvas_and_figure(self):
        time_step = self.main_window.vtk_vis.current_time_step
        fld_name = self.volume.get_name()
        fld_units = self.volume.get_field_units()
        xlabel = fld_name
        if len(fld_units) > 0:
            xlabel += " [$" + fld_units + "$]"

        # Scalar opacity
        hist, hist_edges = self.volume.get_field_data_histogram(
            time_step, self.histogram_bins)
        self.opacity_figure = FigureWithDraggablePoints(
            1, 1, hist=hist, hist_edges=hist_edges, patch_color='tab:blue',
            xlabels=[xlabel], ylabels=["Opacity"], tight_layout=True)
        # self.opacity_figure.patch.set_facecolor("white")
        self.opacity_canvas = FigureCanvas(self.opacity_figure)
        self.opacityWidgetLayout.addWidget(self.opacity_canvas)
        self.opacity_canvas.draw()
        vol_op = self.volume.get_opacity(time_step)
        fld_val, op_val = vol_op.get_opacity_values()
        self.opacity_figure.set_points(0, fld_val, op_val)

        # Colormaps
        self.cmap_figure = FigureWithDraggablePoints(
            3, 1, hist=hist, hist_edges=hist_edges, share_x_axis=True,
            patch_color=['r', 'g', 'b'], xlabels=[xlabel],
            ylabels=["Red", "Green", "Blue"], tight_layout=True)
        # self.cmap_figure.patch.set_facecolor("white")
        self.cmap_canvas = FigureCanvas(self.cmap_figure)
        self.colorsWidgetLayout.addWidget(self.cmap_canvas)
        self.cmap_canvas.draw()
        vol_cmap = self.volume.get_colormap()
        fld_val, r_val, g_val, b_val = vol_cmap.get_cmap_values()
        self.cmap_figure.set_points(0, fld_val, r_val)
        self.cmap_figure.set_points(1, fld_val, g_val)
        self.cmap_figure.set_points(2, fld_val, b_val)

        # Gradient opacity
        hist, hist_edges = self.volume.get_field_data_gradient_histogram(
            time_step, self.histogram_bins)
        xlabel = '$|\\nabla {}|$ [arb. u.]'.format(fld_name)
        self.gradient_opacity_figure = FigureWithDraggablePoints(
            1, 1, hist=hist, hist_edges=hist_edges, patch_color='tab:blue',
            xlabels=[xlabel], ylabels=["Opacity"], tight_layout=True)
        # self.opacity_figure.patch.set_facecolor("white")
        self.gradient_opacity_canvas = FigureCanvas(
            self.gradient_opacity_figure)
        self.gradient_opacityWidgetLayout.addWidget(
            self.gradient_opacity_canvas)
        self.gradient_opacity_canvas.draw()
        vol_op = self.volume.get_gradient_opacity(time_step)
        fld_val, op_val = vol_op.get_opacity_values()
        self.gradient_opacity_figure.set_points(0, fld_val, op_val)

        self.set_axes_range(time_step)

    def set_axes_range(self, time_step):
        nels = 5
        label_pos = np.linspace(0, 255, nels)
        vmin, vmax = self.volume.get_range(time_step)
        labels_array = np.linspace(vmin, vmax, nels)
        labels_list = labels_array.tolist()
        labels = [format(label, '.2e') for label in labels_list]
        self.opacity_figure.set_axes_labels(0, "x", label_pos, labels)
        self.cmap_figure.set_axes_labels(2, "x", label_pos, labels)

    def register_time_step_events(self):
        self.main_window.add_timestep_change_callback(self.set_histograms)
        self.main_window.add_timestep_change_callback(self.set_axes_range)
        self.main_window.add_timestep_change_callback(
            self.set_range_in_line_edits)

    def unregister_time_step_events(self):
        self.main_window.remove_timestep_change_callback(self.set_histograms)
        self.main_window.remove_timestep_change_callback(self.set_axes_range)
        self.main_window.remove_timestep_change_callback(
            self.set_range_in_line_edits)

    def set_histograms(self, time_step):
        hist, hist_edges = self.volume.get_field_data_histogram(
            time_step, self.histogram_bins)
        self.opacity_figure.plot_histogram(0, hist_edges, hist)
        self.cmap_figure.plot_histogram(0, hist_edges, hist)
        self.cmap_figure.plot_histogram(1, hist_edges, hist)
        self.cmap_figure.plot_histogram(2, hist_edges, hist)
        hist, hist_edges = self.volume.get_field_data_gradient_histogram(
            time_step, self.histogram_bins)
        self.gradient_opacity_figure.plot_histogram(0, hist_edges, hist)

    def register_ui_events(self):
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(
            self.update_volume_properties)
        # Scalar opacity tab
        self.optimize_pushButton.clicked.connect(self.get_optimized_opacity)
        self.opacity_comboBox.currentIndexChanged.connect(
            self.set_opacity_from_combobox)
        self.save_opacity_pushButton.clicked.connect(self.save_opacity)
        self.import_opacity_pushButton.clicked.connect(
            self.import_opacity_from_file)
        # Gradient opacity tab
        self.optimize_gradient_opacity_pushButton.clicked.connect(
            self.get_optimized_gradient_opacity)
        self.gradient_opacity_comboBox.currentIndexChanged.connect(
            self.set_gradient_opacity_from_combobox)
        self.save_gradient_opacity_pushButton.clicked.connect(
            self.save_gradient_opacity)
        self.import_gradient_opacity_pushButton.clicked.connect(
            self.import_gradient_opacity_from_file)
        # Colormap tab
        self.cmap_comboBox.currentIndexChanged.connect(
            self.set_cmap_from_combobox)
        self.save_cmap_pushButton.clicked.connect(self.save_cmap)
        self.import_cmap_pushButton.clicked.connect(self.import_cmap_from_file)
        # Range tab
        self.norm_pushButton.clicked.connect(self.range_button_clicked)

    def fill_ui(self):
        self.update_list_of_cmaps()
        self.update_list_of_opacities()
        self.set_range_in_line_edits(
            self.main_window.vtk_vis.current_time_step)

    def update_list_of_cmaps(self):
        self.is_updating_ui = True
        self.cmap_comboBox.clear()
        self.cmap_comboBox.addItems(self.get_cmap_list())
        self.is_updating_ui = False

    def set_range_in_line_edits(self, time_step):
        range = self.volume.get_range(time_step)
        self.min_lineEdit.setText(format(range[0], '.2e'))
        self.max_lineEdit.setText(format(range[1], '.2e'))

    def get_cmap_list(self):
        op_list = self.style_handler.get_available_cmaps()
        op_list.insert(0, "Current colormap")
        return op_list

    def update_list_of_opacities(self):
        self.is_updating_ui = True
        opacity_list = self.get_opacity_list()
        self.opacity_comboBox.clear()
        self.opacity_comboBox.addItems(opacity_list)
        self.gradient_opacity_comboBox.clear()
        self.gradient_opacity_comboBox.addItems(opacity_list)
        self.is_updating_ui = False

    def get_opacity_list(self):
        op_list = self.style_handler.get_available_opacities()
        op_list.insert(0, "Current opacity")
        return op_list

    def import_opacity_from_file(self):
        home_path = str(Path.home())
        file_path = QFileDialog.getOpenFileName(
            self, "Select file to open:", home_path, "Data files (*.h5)")
        file_path = file_path[0]
        if file_path != "":
            self.style_handler.add_opacity_from_file(file_path)
            self.update_list_of_opacities()
            self.opacity_comboBox.setCurrentIndex(
                self.opacity_comboBox.count() - 1)

    def import_gradient_opacity_from_file(self):
        home_path = str(Path.home())
        file_path = QFileDialog.getOpenFileName(
            self, "Select file to open:", home_path, "Data files (*.h5)")
        file_path = file_path[0]
        if file_path != "":
            self.style_handler.add_opacity_from_file(file_path)
            self.update_list_of_opacities()
            self.gradient_opacity_comboBox.setCurrentIndex(
                self.gradient_opacity_comboBox.count() - 1)

    def import_cmap_from_file(self):
        home_path = str(Path.home())
        file_path = QFileDialog.getOpenFileName(
            self, "Select file to open:", home_path, "Data files (*.h5)")
        file_path = file_path[0]
        if file_path != "":
            self.style_handler.add_cmap_from_file(file_path)
            self.update_list_of_cmaps()
            self.cmap_comboBox.setCurrentIndex(
                self.cmap_comboBox.count() - 1)

    def set_cmap_from_combobox(self):
        if not self.is_updating_ui:
            cmap_name = self.cmap_comboBox.currentText()
            if cmap_name != "Current colormap":
                cmap_vals = self.style_handler.get_cmap_values(cmap_name)
                fld_val, r_val, g_val, b_val = cmap_vals
            else:
                vol_cmap = self.volume.get_colormap()
                fld_val, r_val, g_val, b_val = vol_cmap.get_cmap_values()
            self.cmap_figure.set_points(0, fld_val, r_val)
            self.cmap_figure.set_points(1, fld_val, g_val)
            self.cmap_figure.set_points(2, fld_val, b_val)

    def set_opacity_from_combobox(self):
        if not self.is_updating_ui:
            op_name = self.opacity_comboBox.currentText()
            if op_name != "Current opacity":
                fld_val, op_val = self.style_handler.get_opacity_values(
                    op_name)
            else:
                time_step = self.main_window.vtk_vis.current_time_step
                vol_op = self.volume.get_opacity(time_step)
                fld_val, op_val = vol_op.get_opacity_values()
                self.opacity_figure.set_points(0, fld_val, op_val)
            self.opacity_figure.set_points(0, fld_val, op_val)

    def set_gradient_opacity_from_combobox(self):
        if not self.is_updating_ui:
            op_name = self.gradient_opacity_comboBox.currentText()
            if op_name != "Current opacity":
                fld_val, op_val = self.style_handler.get_opacity_values(
                    op_name)
            else:
                time_step = self.main_window.vtk_vis.current_time_step
                vol_op = self.volume.get_gradient_opacity(time_step)
                fld_val, op_val = vol_op.get_opacity_values()
                self.gradient_opacity_figure.set_points(0, fld_val, op_val)
            self.gradient_opacity_figure.set_points(0, fld_val, op_val)

    def get_optimized_opacity(self):
        time_step = self.main_window.vtk_vis.current_time_step
        opacity = self.volume.get_optimized_opacity(time_step)
        fld_val, op_val = opacity.get_opacity_values()
        self.opacity_figure.set_points(0, fld_val, op_val)

    def get_optimized_gradient_opacity(self):
        time_step = self.main_window.vtk_vis.current_time_step
        opacity = self.volume.get_optimized_opacity(time_step,
                                                    gradient_opacity=True)
        fld_val, op_val = opacity.get_opacity_values()
        self.gradient_opacity_figure.set_points(0, fld_val, op_val)

    def save_opacity(self):
        fld_val, op_val = self.opacity_figure.get_points(0)
        op_dialog = SaveOpacityDialog(fld_val, op_val, parent=self)
        op_dialog.exec_()

    def save_gradient_opacity(self):
        fld_val, op_val = self.gradient_opacity_figure.get_points(0)
        op_dialog = SaveOpacityDialog(fld_val, op_val, parent=self)
        op_dialog.exec_()

    def save_cmap(self):
        fld_val, r_val = self.cmap_figure.get_points(0)
        fld_val, g_val = self.cmap_figure.get_points(1)
        fld_val, b_val = self.cmap_figure.get_points(2)
        cmap_dialog = SaveColormapDialog(fld_val, r_val, g_val, b_val,
                                         parent=self)
        cmap_dialog.exec_()

    def update_volume_properties(self):
        fld_vals, op_val = self.opacity_figure.get_points(0)
        fld_vals_grad, grad_op_val = self.gradient_opacity_figure.get_points(0)
        fld_vals_cmap, r_val = self.cmap_figure.get_points(0)
        fld_vals_cmap, g_val = self.cmap_figure.get_points(1)
        fld_vals_cmap, b_val = self.cmap_figure.get_points(2)
        opacity = Opacity(name='custom', op_values=op_val, fld_values=fld_vals)
        gradient_opacity = Opacity(name='custom', op_values=grad_op_val,
                                   fld_values=fld_vals_grad)
        cmap = Colormap(name='custom', r_values=r_val, g_values=g_val,
                        b_values=b_val, fld_values=fld_vals_cmap)
        self.volume.set_opacity(opacity)
        self.volume.set_gradient_opacity(gradient_opacity)
        self.volume.set_colormap(cmap)
        self.main_window.interactor.Render()

    def range_button_clicked(self):
        min_val = float(self.min_lineEdit.text())
        max_val = float(self.max_lineEdit.text())
        self.set_field_range(min_val, max_val)

    def set_field_range(self, min_val, max_val):
        time_step = self.main_window.vtk_vis.current_time_step
        self.volume.set_range(min_val, max_val)
        self.main_window.render_timestep(time_step)
        self.set_axes_range(time_step)
        self.set_histograms(time_step)
        self.set_range_in_line_edits(time_step)
