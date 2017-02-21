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
from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, SceneEditor

from VisualPIC.Views.particleTrackerWindow import ParticleTrackerWindow
from VisualPIC.DataHandling.dataContainer import DataContainer
from VisualPIC.DataPlotting.fieldToPlot import FieldToPlot


if getattr(sys, 'frozen', False):
    # we are running in a bundle
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
guipath = os.path.join( bundle_dir, 'Visualizer3Dmayavi.ui' )

Ui_Visualizer3Dmayavi, QVisualizer3Dmayavi = loadUiType(guipath)

	
class Visualizer3Dmayavi(QVisualizer3Dmayavi, Ui_Visualizer3Dmayavi):
    def __init__(self, dataContainer):
        super(Visualizer3Dmayavi, self).__init__()
        self.setupUi(self)
        self.dataContainer = dataContainer
        self.RegisterUIEvents()
        self.CreateMayaviRenderer()
        self.timeSteps = np.zeros(1)
        self.FillUIWithData()
        
    def CreateMayaviRenderer(self):
        pass

    def RegisterUIEvents(self):
        self.addDomainField_Button.clicked.connect(self.AddDomainFieldButton_Clicked)
        self.addSpeciesField_Button.clicked.connect(self.AddSpeciesFieldButton_Clicked)
        self.av2DDomainFields_comboBox.currentIndexChanged.connect(self.Av2DDomainFieldsComboBox_IndexChanged)
        self.avSpeciesFields_comboBox.currentIndexChanged.connect(self.AvSpeciesFieldsComboBox_IndexChanged)
        self.timeStep_Slider.sliderReleased.connect(self.TimeStepSlider_Released)
        self.timeStep_Slider.valueChanged.connect(self.TimeStepSlider_ValueChanged)
        self.nextStep_Button.clicked.connect(self.NextButton_Clicked)
        self.prevStep_Button.clicked.connect(self.PrevButton_Clicked)
        self.plot_pushButton.clicked.connect(self.PlotButton_Clicked)

    def FillUIWithData(self):
        self.av2DDomainFields_comboBox.clear()
        self.av2DDomainFields_comboBox.addItems(self.dataContainer.GetAvailableDomainFieldsNames())
        self.FillAvailableSpeciesList()
        self.SetSelectedDomainField()
        self.SetSelectedSpeciesField()

    def FillAvailableSpeciesList(self):
        model = QtGui.QStandardItemModel()
        avSpecies = list()
        avSpecies = self.dataContainer.GetAvailableSpeciesNames()
        for species in avSpecies:
            item = QtGui.QStandardItem(species)
            item.setCheckable(True)
            model.appendRow(item)
        model.itemChanged.connect(self.Item_Changed)
        self.selectedSpecies_listView.setModel(model)

    """
    UI event handlers
    """
    def Av2DDomainFieldsComboBox_IndexChanged(self):
        self.SetSelectedDomainField()

    def AvSpeciesFieldsComboBox_IndexChanged(self):
        self.SetSelectedSpeciesField()

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

    def PlotButton_Clicked(self):
        self.MakePlots()
        
    def AddDomainFieldButton_Clicked(self):
        self.AddFieldsToPlot(self.dataContainer.GetSelectedDomainField(), self.domainFieldPlotDimension)
        	
    def AddSpeciesFieldButton_Clicked(self):
        self.dataContainer.SetSelectedSpeciesFields()
        self.AddFieldsToPlot(self.dataContainer.GetSelectedSpeciesFields(), self.speciesFieldPlotDimension)

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
        self.fieldsToPlot_listWidget.clear()
        self.currentAxesFieldsToPlot[:] = []
        self.subplotList[:] = []
    
    def SetSelectedDomainField(self):
        self.dataContainer.SetSelectedDomainField(self.av2DDomainFields_comboBox.currentText())
        
    def SetSelectedSpeciesField(self):
        self.dataContainer.SetSelectedSpeciesField(self.avSpeciesFields_comboBox.currentText())
        
    def AddFieldsToPlot(self, fields, fieldPlotDimension):
        fldList = list()
        for fld in fields:
            fieldToPlot = FieldToPlot(fld, fieldPlotDimension, self.colorMapsCollection, isPartOfMultiplot = len(fields)>1)
            fldList.append(fieldToPlot)
        plotPosition = len(self.subplotList)+1
        subplot = FieldSubplot(plotPosition, self.colorMapsCollection, fldList)
        self.subplotList.append(subplot)
        self.SetAutoColumnsAndRows()
        wid = SubplotItem(subplot, self.MakePlots, self)
        wid2 = QtWidgets.QListWidgetItem()
        wid2.setSizeHint(QtCore.QSize(100, 40))
        self.fieldsToPlot_listWidget.addItem(wid2)
        self.fieldsToPlot_listWidget.setItemWidget(wid2, wid)
        self.SetTimeSteps()
        
    def MakePlots(self):
        #Create source
        source = vtk.vtkSphereSource()
        source.SetCenter(0, 0, 0)
        source.SetRadius(5.0)
 
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())
 
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
 
        self.renderer.AddActor(actor)
 
        self.renderer.ResetCamera()

        self.show()
        self.interactor.Initialize()

    def RemoveSubplot(self, item):
        index = self.subplotList.index(item.subplot)
        self.subplotList.remove(item.subplot)
        self.fieldsToPlot_listWidget.takeItem(index)
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