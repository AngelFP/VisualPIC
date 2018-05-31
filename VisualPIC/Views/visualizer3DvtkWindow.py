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
from PyQt5.uic import loadUiType
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

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
guipath = os.path.join( bundle_dir, 'Visualizer3Dvtk.ui' )

Ui_Visualizer3DvtkWindow, QVisualizer3DvtkWindow = loadUiType(guipath)

	
class Visualizer3DvtkWindow(QVisualizer3DvtkWindow, Ui_Visualizer3DvtkWindow):
    def __init__(self, dataContainer):
        super(Visualizer3DvtkWindow, self).__init__()
        self.setupUi(self)
        self.visualizer3Dvtk = Visualizer3Dvtk(dataContainer)
        self.RegisterUIEvents()
        self.CreateVTKWidget()
        self.current_time_step = -1
        self.time_steps = np.zeros(1)
        self.time_step_change_observers = list()
        self.updating_ui = False
        self.FillUIWithData()
        self.create_time_step_callbacks()
        
    def CreateVTKWidget(self):
        self.vtkWidget = self.visualizer3Dvtk.GetVTKWidget(self.plot_Widget)
        self.plotWidget_layout.addWidget(self.vtkWidget)
    
    def RegisterUIEvents(self):
        self.addToRender_Button.clicked.connect(self.AddToRenderButton_Clicked)
        self.timeStep_Slider.sliderReleased.connect(self.TimeStepSlider_Released)
        self.timeStep_Slider.valueChanged.connect(self.TimeStepSlider_ValueChanged)
        self.nextStep_Button.clicked.connect(self.NextButton_Clicked)
        self.prevStep_Button.clicked.connect(self.PrevButton_Clicked)
        self.render_pushButton.clicked.connect(self.RenderButton_Clicked)
        self.brightness_horizontalSlider.sliderReleased.connect(self.set_volume_brightness)
        self.contrast_horizontalSlider.sliderReleased.connect(self.set_volume_contrast)
        self.screenshotButton.clicked.connect(self.ScreenshotButton_Clicked)
        self.black_bg_radioButton.toggled.connect(self.change_background)
        self.white_bg_radioButton.toggled.connect(self.change_background)
        self.logo_checkBox.toggled.connect(self.visualizer3Dvtk.set_logo_widget_visibility)
        self.axes_checkBox.toggled.connect(self.visualizer3Dvtk.set_axes_widget_visibility)

    def set_volume_brightness(self):
        slider_value = self.brightness_horizontalSlider.value()
        slider_max = self.brightness_horizontalSlider.maximum()
        slider_min = self.brightness_horizontalSlider.minimum()
        # rescale value to a range between 0 and 1
        brightness = (slider_value-slider_min)/(slider_max-slider_min)
        color_level = (1-brightness)
        self.visualizer3Dvtk.set_color_level(color_level)
        self.UpdateRender()

    def set_volume_contrast(self):
        slider_value = self.contrast_horizontalSlider.value()
        slider_max = self.contrast_horizontalSlider.maximum()
        slider_min = self.contrast_horizontalSlider.minimum()
        # rescale value to a range between 0 and 1
        contrast = (slider_value-slider_min)/(slider_max-slider_min)
        if contrast == 1:
            contrast -= 1e-3
        color_window = -np.log(contrast)
        self.visualizer3Dvtk.set_color_window(color_window)
        self.UpdateRender()

    def change_background(self):
        if self.black_bg_radioButton.isChecked():
            self.visualizer3Dvtk.set_renderer_background(0, 0, 0)
        elif self.white_bg_radioButton.isChecked():
            self.visualizer3Dvtk.set_renderer_background(1, 1, 1)
        self.UpdateRender()

    def create_time_step_callbacks(self):
        self.bind_time_step_to(self.timeStep_Slider.setValue)

    def ScreenshotButton_Clicked(self):
        AnimationWindow = CreateVTKAnimationWindow(self)
        AnimationWindow.exec_()

    def FillUIWithData(self):
        self.FillAvailable3DFieldsList()
        self.set_brightness_slider_value()
        self.set_contrast_slider_value()

    def set_brightness_slider_value(self):
        slider_max = self.brightness_horizontalSlider.maximum()
        slider_min = self.brightness_horizontalSlider.minimum()
        color_level = self.visualizer3Dvtk.get_color_level()
        brightness = 1-color_level
        slider_value = slider_min + brightness*(slider_max-slider_min)
        self.brightness_horizontalSlider.setValue(slider_value)

    def set_contrast_slider_value(self):
        slider_max = self.contrast_horizontalSlider.maximum()
        slider_min = self.contrast_horizontalSlider.minimum()
        color_window = self.visualizer3Dvtk.get_color_window()
        contrast = np.exp(-color_window)
        slider_value = slider_min + contrast*(slider_max-slider_min)
        self.contrast_horizontalSlider.setValue(slider_value)

    def FillAvailable3DFieldsList(self):
        model = QtGui.QStandardItemModel()
        avFields = self.visualizer3Dvtk.GetListOfAvailable3DFields()
        for field in avFields:
            text = field["fieldName"]
            if field["speciesName"] != "":
                text += " [" + field["speciesName"] + "]"
            item = QtGui.QStandardItem(text)
            item.setCheckable(True)
            model.appendRow(item)
        self.availableFields_listView.setModel(model)

    def UpdateRender(self):
        self.visualizer3Dvtk.UpdateRender()

    def get_current_time_step(self):
        return self.current_time_step

    """
    UI event handlers
    """
    def TimeStepSlider_Released(self):
        self.set_time_step(self.timeStep_Slider.value())
            
    def TimeStepSlider_ValueChanged(self):
        self.timeStep_LineEdit.setText(str(self.timeStep_Slider.value()))
        
    def NextButton_Clicked(self):
        current_index = np.where(self.time_steps == self.current_time_step)[0][0]
        if current_index < len(self.time_steps)-1:
            self.set_time_step(self.time_steps[current_index + 1])
        
    def PrevButton_Clicked(self):
        current_index = np.where(self.time_steps == self.current_time_step)[0][0]
        if current_index > 0:
            self.set_time_step(self.time_steps[current_index - 1])

    def RenderButton_Clicked(self):
        self.make_render()
        	
    def AddToRenderButton_Clicked(self):
        model = self.availableFields_listView.model()
        for index in range(model.rowCount()):
            item = model.item(index)
            if item.checkState() == QtCore.Qt.Checked:
                text = item.text()
                if "[" in text:
                    fieldName = text.split(" [")[0]
                    speciesName = text.split(" [")[1][:-1]
                else:
                    fieldName = text
                    speciesName = ""
                if self.visualizer3Dvtk.AddVolumeField(fieldName, speciesName):
                    wid = VolumeVTKItem(self.visualizer3Dvtk.GetVolumeField(fieldName, speciesName), self)
                    wid2 = QtWidgets.QListWidgetItem()
                    wid2.setSizeHint(QtCore.QSize(100, 40))
                    self.fieldsToRender_listWidget.addItem(wid2)
                    self.fieldsToRender_listWidget.setItemWidget(wid2, wid)
        self.SetTimeSteps()
        if self.current_time_step == -1:
            self.set_time_step(self.time_steps[0], False)

    """
    Called from UI event handlers
    """
    def ClearData(self):
        self.fieldsToRender_listWidget.clear()
        self.volumeList[:] = []
        
    def make_render(self):
        self.visualizer3Dvtk.MakeRender(self.current_time_step)

    def RemoveField(self, item):
        self.visualizer3Dvtk.RemoveVolume(item.volume)
        for i in np.arange(0, self.fieldsToRender_listWidget.count()):
            if item == self.fieldsToRender_listWidget.itemWidget(self.fieldsToRender_listWidget.item(i)):
                self.fieldsToRender_listWidget.takeItem(i)
        self.SetTimeSteps()

    def SetTimeSteps(self):
        self.time_steps = self.visualizer3Dvtk.GetTimeSteps()
        minTime = min(self.time_steps)
        maxTime = max(self.time_steps)
        self.timeStep_Slider.setMinimum(minTime)
        self.timeStep_Slider.setMaximum(maxTime)

    """
    Others
    """
    def GetDataFolderLocation(self):
        return self.visualizer3Dvtk.dataContainer.GetDataFolderLocation()

    def SaveScreenshot(self, path):
        self.visualizer3Dvtk.SaveScreenshot(path)

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