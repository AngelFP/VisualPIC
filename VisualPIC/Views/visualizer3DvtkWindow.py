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

import h5py
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
        self.timeSteps = np.zeros(1)
        self.FillUIWithData()
        
    def CreateVTKWidget(self):
        self.vtkwidget = self.visualizer3Dvtk.GetVTKWidget(self.plot_Widget)
        self.plotWidget_layout.addWidget(self.vtkwidget)
    
    def RegisterUIEvents(self):
        self.addToRender_Button.clicked.connect(self.AddToRenderButton_Clicked)
        self.timeStep_Slider.sliderReleased.connect(self.TimeStepSlider_Released)
        self.timeStep_Slider.valueChanged.connect(self.TimeStepSlider_ValueChanged)
        self.nextStep_Button.clicked.connect(self.NextButton_Clicked)
        self.prevStep_Button.clicked.connect(self.PrevButton_Clicked)
        self.render_pushButton.clicked.connect(self.RenderButton_Clicked)

    def FillUIWithData(self):
        self.FillAvailable3DFieldsList()

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

    """
    UI event handlers
    """
    def TimeStepSlider_Released(self):
        if self.timeStep_Slider.value() in self.timeSteps:
            self.MakeRender()
        else:
            val = self.timeStep_Slider.value()
            closestHigher = self.timeSteps[np.where(self.timeSteps > val)[0][0]]
            closestLower = self.timeSteps[np.where(self.timeSteps < val)[0][-1]]
            if abs(val-closestHigher) < abs(val-closestLower):
                self.timeStep_Slider.setValue(closestHigher)
            else:
                self.timeStep_Slider.setValue(closestLower)
            self.MakeRender()
            
    def TimeStepSlider_ValueChanged(self):
        self.timeStep_LineEdit.setText(str(self.timeStep_Slider.value()))
        
    def NextButton_Clicked(self):
        currentTimeStep = self.timeStep_Slider.value()
        currentIndex = np.where(self.timeSteps == currentTimeStep)[0][0]
        if currentIndex < len(self.timeSteps)-1:
            self.timeStep_Slider.setValue(self.timeSteps[currentIndex + 1])
        self.MakeRender()
        
    def PrevButton_Clicked(self):
        currentTimeStep = self.timeStep_Slider.value()
        currentIndex = np.where(self.timeSteps == currentTimeStep)[0][0]
        if currentIndex > 0:
            self.timeStep_Slider.setValue(self.timeSteps[currentIndex - 1])
        self.MakeRender()

    def RenderButton_Clicked(self):
        self.MakeRender()
        	
    def AddToRenderButton_Clicked(self):
        model = self.availableFields_listView.model()
        for index in range(model.rowCount()):
            item = model.item(index)
            if item.checkState() == QtCore.Qt.Checked:
                text = item.text()
                fieldName = text.split(" [")[0]
                speciesName = text.split(" [")[1][:-1]
                if self.visualizer3Dvtk.AddVolumeField(fieldName, speciesName):
                    wid = VolumeVTKItem(self.visualizer3Dvtk.GetVolumeField(fieldName, speciesName), self)
                    wid2 = QtWidgets.QListWidgetItem()
                    wid2.setSizeHint(QtCore.QSize(100, 40))
                    self.fieldsToRender_listWidget.addItem(wid2)
                    self.fieldsToRender_listWidget.setItemWidget(wid2, wid)
        self.SetTimeSteps()

    """
    Called from UI event handlers
    """
    def ClearData(self):
        self.fieldsToRender_listWidget.clear()
        self.volumeList[:] = []
        
    def MakeRender(self):
        timeStep = self.timeStep_Slider.value()
        self.visualizer3Dvtk.MakeRender(timeStep)

    def RemoveField(self, item):
        self.visualizer3Dvtk.RemoveVolume(item.volume)
        for i in np.arange(0, self.fieldsToRender_listWidget.count()):
            if item == self.fieldsToRender_listWidget.itemWidget(self.fieldsToRender_listWidget.item(i)):
                self.fieldsToRender_listWidget.takeItem(i)
        self.SetTimeSteps()

    def SetTimeSteps(self):
        self.timeSteps = self.visualizer3Dvtk.GetTimeSteps()
        minTime = min(self.timeSteps)
        maxTime = max(self.timeSteps)
        self.timeStep_Slider.setMinimum(minTime)
        self.timeStep_Slider.setMaximum(maxTime)