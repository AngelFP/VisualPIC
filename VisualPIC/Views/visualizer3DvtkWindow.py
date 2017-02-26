# -*- coding: utf-8 -*-

#Copyright 2016-2017 ?ngel Ferran Pousa
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

from VisualPIC.Views.particleTrackerWindow import ParticleTrackerWindow
from VisualPIC.DataHandling.dataContainer import DataContainer
from VisualPIC.DataPlotting.fieldToPlot import FieldToPlot
from VisualPIC.Tools.visualizer3Dvtk import Visualizer3Dvtk


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
        self.plotWidget_layout.addWidget(self.visualizer3Dvtk.GetVTKWidget(self.plot_Widget))
    
    def RegisterUIEvents(self):
        self.addToRender_Button.clicked.connect(self.AddToRenderButton_Clicked)
        self.timeStep_Slider.sliderReleased.connect(self.TimeStepSlider_Released)
        self.timeStep_Slider.valueChanged.connect(self.TimeStepSlider_ValueChanged)
        self.nextStep_Button.clicked.connect(self.NextButton_Clicked)
        self.prevStep_Button.clicked.connect(self.PrevButton_Clicked)
        self.render_pushButton.clicked.connect(self.RenderButton_Clicked)

    def FillUIWithData(self):
        #self.av2DDomainFields_comboBox.addItems(self.dataContainer.GetAvailableDomainFieldsNames())
        self.FillAvailable3DFieldsList()
        #self.SetSelectedDomainField()
        #self.SetSelectedSpeciesField()

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
        model.itemChanged.connect(self.Item_Changed)
        self.availableFields_listView.setModel(model)

    """
    UI event handlers
    """
    def TimeStepSlider_Released(self):
        if self.timeStep_Slider.value() in self.timeSteps:
            self.MakePlots()
        else:
            val = self.timeStep_Slider.value()
            closestHigher = self.timeSteps[np.where(self.timeSteps > val)[0][0]]
            closestLower = self.timeSteps[np.where(self.timeSteps < val)[0][-1]]
            if abs(val-closestHigher) < abs(val-closestLower):
                self.timeStep_Slider.setValue(closestHigher)
            else:
                self.timeStep_Slider.setValue(closestLower)
            self.MakePlots()
            
    def TimeStepSlider_ValueChanged(self):
        self.timeStep_LineEdit.setText(str(self.timeStep_Slider.value()))
        
    def NextButton_Clicked(self):
        currentTimeStep = self.timeStep_Slider.value()
        currentIndex = np.where(self.timeSteps == currentTimeStep)[0][0]
        if currentIndex < len(self.timeSteps)-1:
            self.timeStep_Slider.setValue(self.timeSteps[currentIndex + 1])
        self.MakePlots()
        
    def PrevButton_Clicked(self):
        currentTimeStep = self.timeStep_Slider.value()
        currentIndex = np.where(self.timeSteps == currentTimeStep)[0][0]
        if currentIndex > 0:
            self.timeStep_Slider.setValue(self.timeSteps[currentIndex - 1])
        self.MakePlots()

    def RenderButton_Clicked(self):
        self.MakePlots()
        	
    def AddToRenderButton_Clicked(self):
        #self.dataContainer.SetSelectedSpeciesFields()
        #self.AddFieldsToPlot(self.dataContainer.GetSelectedSpeciesFields(), self.speciesFieldPlotDimension)
        field = self.visualizer3Dvtk.GetVolumeField("Charge density", "plasma")
        field.SetColorPoints([0, 1, 0, 0, 100, 1, 0, 0, 255, 1, 0, 0])
        field.SetOpacityPoints([0, 1, 255, 1])
        self.visualizer3Dvtk.UpdateRender()

    """
    Called from UI event handlers
    """
    def Item_Changed(self,item):
        # If the item is checked, add the species to the list of selected species
        if item.checkState():
            self.dataContainer.AddSelectedSpecies(item.text())
        else:
            self.dataContainer.RemoveSelectedSpecies(item.text())
        self.avSpeciesFields_comboBox.clear()
        self.avSpeciesFields_comboBox.addItems(self.dataContainer.GetCommonlyAvailableFields())
    
    def ClearData(self):
        self.rows_spinBox.setValue(1)
        self.columns_spinBox.setValue(1)
        self.fieldsToRender_listWidget.clear()
        self.currentAxesFieldsToPlot[:] = []
        self.subplotList[:] = []
        
    def MakePlots(self):
        self.visualizer3Dvtk.AddVolumeField("Charge density", "plasma")
        self.visualizer3Dvtk.MakeRender(26)

    def RemoveSubplot(self, item):
        index = self.subplotList.index(item.subplot)
        self.subplotList.remove(item.subplot)
        self.fieldsToRender_listWidget.takeItem(index)
        for subplot in self.subplotList:
            if subplot.GetPosition() > index+1:
                subplot.SetPosition(subplot.GetPosition()-1)
        rows = self.rows_spinBox.value()
        columns = self.columns_spinBox.value()
        if len(self.subplotList) > 0:
            if self.increaseRowsColumnsCounter % 2 == 0:
                if len(self.subplotList) <= rows*(columns-1):
                    self.DecreaseColumns()
                    self.increaseRowsColumnsCounter -= 1
            else:
                if len(self.subplotList) <= (rows-1)*columns:
                    self.DecreaseRows()
                    self.increaseRowsColumnsCounter -= 1
        self.SetTimeSteps()

    def SetTimeSteps(self):
        i = 0
        for subplot in self.subplotList:
            if i == 0:
                self.timeSteps = subplot.GetTimeSteps()
            else :
                self.timeSteps = np.intersect1d(self.timeSteps, subplot.GetTimeSteps())
            i+=1
        minTime = min(self.timeSteps)
        maxTime = max(self.timeSteps)
        self.timeStep_Slider.setMinimum(minTime)
        self.timeStep_Slider.setMaximum(maxTime)