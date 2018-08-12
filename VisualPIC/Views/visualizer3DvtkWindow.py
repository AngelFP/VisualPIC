# -*- coding: utf-8 -*-

#Copyright 2016-2018 Angel Ferran Pousa
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

import os
import sys
from pkg_resources import resource_filename

from PyQt5.uic import loadUiType
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import vtk

from VisualPIC.DataHandling.dataContainer import DataContainer
from VisualPIC.Tools.visualizer3Dvtk import Visualizer3Dvtk
from VisualPIC.Controls.volumeVTKItem import VolumeVTKItem
from VisualPIC.Views.createVTKAnimationWindow import CreateVTKAnimationWindow


if getattr(sys, 'frozen', False):
    # we are running in a bundle
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
guipath = os.path.join(bundle_dir, 'Visualizer3Dvtk.ui')

Ui_Visualizer3DvtkWindow, QVisualizer3DvtkWindow = loadUiType(guipath)

	
class Visualizer3DvtkWindow(QVisualizer3DvtkWindow, Ui_Visualizer3DvtkWindow):
    def __init__(self, data_container):
        super(Visualizer3DvtkWindow, self).__init__()
        self.setupUi(self)
        self.set_ui_icons()
        self.vtk_3d_visualizer = Visualizer3Dvtk(data_container)
        self.register_ui_events()
        self.create_vtk_widget()
        self.current_time_step = -1
        self.time_steps = np.array([])
        self.time_step_change_observers = list()
        self.updating_ui = False
        self.fill_ui()
        self.create_time_step_callbacks()

    def set_ui_icons(self):
        window_icon_path = resource_filename(
            'VisualPIC.Icons', 'logo.png')
        prev_button_icon_path = resource_filename(
            'VisualPIC.Icons', 'icon-ios7-arrow-left-128.png')
        next_button_icon_path = resource_filename(
            'VisualPIC.Icons', 'icon-ios7-arrow-right-128.png')
        self.setWindowIcon(QtGui.QIcon(window_icon_path))
        self.prevStep_Button.setIcon(QtGui.QIcon(prev_button_icon_path))
        self.nextStep_Button.setIcon(QtGui.QIcon(next_button_icon_path))

    def closeEvent(self, *args, **kwargs):
        """ This fixes bug described in 
        (http://vtk.1045678.n5.nabble.com/Multiple-vtkRenderWindows-Error-
        during-cleanup-wglMakeCurrent-failed-in-Clean-tt5747036.html)
        """
        self.vtk_widget.GetRenderWindow().Finalize()
        super(Visualizer3DvtkWindow, self).closeEvent(*args, **kwargs)
        
    def create_vtk_widget(self):
        self.vtk_widget = self.vtk_3d_visualizer.get_vtk_widget(
            self.plot_Widget)
        self.plotWidget_layout.addWidget(self.vtk_widget)
    
    def register_ui_events(self):
        self.addToRender_Button.clicked.connect(
            self.add_to_render_button_clicked)
        self.timeStep_Slider.sliderReleased.connect(
            self.time_step_slider_released)
        self.timeStep_Slider.valueChanged.connect(
            self.time_step_slider_value_changed)
        self.nextStep_Button.clicked.connect(self.next_button_clicked)
        self.prevStep_Button.clicked.connect(self.prev_button_clicked)
        self.render_pushButton.clicked.connect(self.render_button_clicked)
        self.brightness_horizontalSlider.sliderReleased.connect(
            self.set_volume_brightness)
        self.contrast_horizontalSlider.sliderReleased.connect(
            self.set_volume_contrast)
        self.screenshotButton.clicked.connect(self.screenshot_button_clicked)
        self.black_bg_radioButton.toggled.connect(self.change_background)
        self.white_bg_radioButton.toggled.connect(self.change_background)
        self.logo_checkBox.toggled.connect(self.set_logo_visibility)
        self.axes_checkBox.toggled.connect(self.set_axes_visibility)
        self.cbar_checkBox.toggled.connect(self.set_colorbars_visibility)
        self.quality_comboBox.currentIndexChanged.connect(
            self.set_render_quality)

    def set_colorbars_visibility(self, value):
        if not self.updating_ui:
            self.vtk_3d_visualizer.set_colorbar_visibility(value)
            self.update_render()

    def set_logo_visibility(self, value):
        if not self.updating_ui:
            self.vtk_3d_visualizer.set_logo_widget_visibility(value)
            self.update_render()

    def set_axes_visibility(self, value):
        if not self.updating_ui:
            self.vtk_3d_visualizer.set_axes_widget_visibility(value)
            self.update_render()

    def set_render_quality(self):
        if not self.updating_ui:
            str_value = self.quality_comboBox.currentText()
            self.vtk_3d_visualizer.set_render_quality(str_value)
            self.update_render()

    def set_volume_brightness(self):
        slider_value = self.brightness_horizontalSlider.value()
        slider_max = self.brightness_horizontalSlider.maximum()
        slider_min = self.brightness_horizontalSlider.minimum()
        # rescale value to a range between 0 and 1
        brightness = (slider_value-slider_min)/(slider_max-slider_min)
        color_level = (1-brightness)
        self.vtk_3d_visualizer.set_color_level(color_level)
        self.update_render()

    def set_volume_contrast(self):
        slider_value = self.contrast_horizontalSlider.value()
        slider_max = self.contrast_horizontalSlider.maximum()
        slider_min = self.contrast_horizontalSlider.minimum()
        # rescale value to a range between 0 and 1
        contrast = (slider_value-slider_min)/(slider_max-slider_min)
        if contrast == 1:
            contrast -= 1e-3
        color_window = -np.log(contrast)
        self.vtk_3d_visualizer.set_color_window(color_window)
        self.update_render()

    def change_background(self):
        if not self.updating_ui:
            if self.black_bg_radioButton.isChecked():
                self.vtk_3d_visualizer.set_renderer_background("Black")
            elif self.white_bg_radioButton.isChecked():
                self.vtk_3d_visualizer.set_renderer_background("White")
            self.update_render()

    def create_time_step_callbacks(self):
        self.bind_time_step_to(self.timeStep_Slider.setValue)

    def screenshot_button_clicked(self):
        animation_window = CreateVTKAnimationWindow(self)
        animation_window.exec_()

    def fill_ui(self):
        self.updating_ui = True
        self.fill_available_3d_fields_list()
        self.set_brightness_slider_value()
        self.set_contrast_slider_value()
        self.fill_render_quality_combobox()
        self.setup_axes_checkbox()
        self.setup_logo_checkbox()
        self.setup_background_color_radio_buttons()
        self.timeStep_Slider.setEnabled(False)
        self.nextStep_Button.setEnabled(False)
        self.prevStep_Button.setEnabled(False)
        self.updating_ui = False

    def setup_background_color_radio_buttons(self):
        option = self.vtk_3d_visualizer.get_current_background_color_option()
        if option == "White":
            self.white_bg_radioButton.setChecked(True)
        elif option == "Black":
            self.black_bg_radioButton.setChecked(True)

    def setup_axes_checkbox(self):
        self.axes_checkBox.setChecked(
            self.vtk_3d_visualizer.get_axes_visibility())

    def setup_logo_checkbox(self):
        self.logo_checkBox.setChecked(
            self.vtk_3d_visualizer.get_logo_visibility())

    def fill_render_quality_combobox(self):
        self.quality_comboBox.addItems(
            self.vtk_3d_visualizer.get_render_quality_options())
        index = self.quality_comboBox.findText(
            self.vtk_3d_visualizer.get_current_render_quality())
        self.quality_comboBox.setCurrentIndex(index)

    def set_brightness_slider_value(self):
        slider_max = self.brightness_horizontalSlider.maximum()
        slider_min = self.brightness_horizontalSlider.minimum()
        color_level = self.vtk_3d_visualizer.get_color_level()
        brightness = 1-color_level
        slider_value = slider_min + brightness*(slider_max-slider_min)
        self.brightness_horizontalSlider.setValue(slider_value)

    def set_contrast_slider_value(self):
        slider_max = self.contrast_horizontalSlider.maximum()
        slider_min = self.contrast_horizontalSlider.minimum()
        color_window = self.vtk_3d_visualizer.get_color_window()
        contrast = np.exp(-color_window)
        slider_value = slider_min + contrast*(slider_max-slider_min)
        self.contrast_horizontalSlider.setValue(slider_value)

    def fill_available_3d_fields_list(self):
        model = QtGui.QStandardItemModel()
        avFields = self.vtk_3d_visualizer.get_list_of_available_3d_fields()
        for field in avFields:
            text = field["field_name"]
            if field["species_name"] != "":
                text += " [" + field["species_name"] + "]"
            item = QtGui.QStandardItem(text)
            item.setCheckable(True)
            model.appendRow(item)
        self.availableFields_listView.setModel(model)

    def update_render(self):
        self.vtk_3d_visualizer.update_render()

    def get_current_time_step(self):
        return self.current_time_step

    def update_colorbars(self, time_step, update_data=True,
                         update_position=True):
        if self.cbar_checkBox.isChecked():
            self.vtk_3d_visualizer.create_colorbars(time_step, update_data,
                                                    update_position)
            self.update_render()

    """
    UI event handlers
    """
    def time_step_slider_released(self):
        self.set_time_step(self.timeStep_Slider.value())
            
    def time_step_slider_value_changed(self):
        self.timeStep_LineEdit.setText(str(self.timeStep_Slider.value()))
        
    def next_button_clicked(self):
        if len(self.time_steps) > 0:
            current_index = np.where(
                self.time_steps == self.current_time_step)[0][0]
            if current_index < len(self.time_steps)-1:
                self.set_time_step(self.time_steps[current_index + 1])
        
    def prev_button_clicked(self):
        if len(self.time_steps) > 0:
            current_index = np.where(
                self.time_steps == self.current_time_step)[0][0]
            if current_index > 0:
                self.set_time_step(self.time_steps[current_index - 1])

    def render_button_clicked(self):
        self.make_render()
        	
    def add_to_render_button_clicked(self):
        model = self.availableFields_listView.model()
        for index in range(model.rowCount()):
            item = model.item(index)
            if item.checkState() == QtCore.Qt.Checked:
                text = item.text()
                if "[" in text:
                    fieldName = text.split(" [")[0]
                    species_name = text.split(" [")[1][:-1]
                else:
                    fieldName = text
                    species_name = ""
                if self.vtk_3d_visualizer.add_volume_field(fieldName,
                                                         species_name):
                    wid = VolumeVTKItem(
                        self.vtk_3d_visualizer.get_volume_field(
                            fieldName, species_name), self)
                    wid2 = QtWidgets.QListWidgetItem()
                    wid2.setSizeHint(QtCore.QSize(100, 40))
                    self.fieldsToRender_listWidget.addItem(wid2)
                    self.fieldsToRender_listWidget.setItemWidget(wid2, wid)
        self.set_time_steps()
        if self.current_time_step == -1:
            self.set_time_step(self.time_steps[0], False)

    """
    Called from UI event handlers
    """        
    def make_render(self):
        self.vtk_3d_visualizer.make_render(self.current_time_step)

    def remove_field(self, item):
        self.vtk_3d_visualizer.remove_volume(item.volume)
        for i in np.arange(0, self.fieldsToRender_listWidget.count()):
            item_i = self.fieldsToRender_listWidget.item(i)
            if item == self.fieldsToRender_listWidget.itemWidget(item_i):
                self.fieldsToRender_listWidget.takeItem(i)
        self.update_colorbars(self.current_time_step, update_data=False,
                              update_position=True)
        self.set_time_steps()

    def set_time_steps(self):
        self.time_steps = self.vtk_3d_visualizer.get_time_steps()
        if len(self.time_steps) > 0:
            self.timeStep_Slider.setEnabled(True)
            self.nextStep_Button.setEnabled(True)
            self.prevStep_Button.setEnabled(True)
            min_time = min(self.time_steps)
            max_time = max(self.time_steps)
            self.timeStep_Slider.setMinimum(min_time)
            self.timeStep_Slider.setMaximum(max_time)
        else:
            self.timeStep_Slider.setEnabled(False)
            self.nextStep_Button.setEnabled(False)
            self.prevStep_Button.setEnabled(False)

        

    """
    Others
    """
    def get_data_folder_location(self):
        return self.vtk_3d_visualizer.data_container.get_data_folder_location()

    def save_screenshot(self, path):
        self.vtk_3d_visualizer.save_screenshot(path)

    def set_time_step(self, time_step, make_render = True):
        if time_step in self.time_steps:
            self.current_time_step = time_step
        else:
            closest_higher = self.time_steps[
                np.where(self.time_steps > time_step)[0][0]]
            closest_lower = self.time_steps[
                np.where(self.time_steps < time_step)[0][-1]]
            if abs(time_step-closest_higher) < abs(time_step-closest_lower):
                self.current_time_step = closest_higher
            else:
                self.current_time_step = closest_lower
        self.updating_ui = True
        for callback in self.time_step_change_observers:
            callback(self.current_time_step)
        self.updating_ui = False
        if make_render:
            self.make_render()

    def bind_time_step_to(self, callback):
        self.time_step_change_observers.append(callback)

    def unbind_time_step_to(self, callback):
        self.time_step_change_observers.remove(callback)