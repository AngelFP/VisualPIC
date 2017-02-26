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
        #self.av2DDomainFields_comboBox.addItems(self.dataContainer.GetAvailableDomainFieldsNames())
        #self.FillAvailableSpeciesList()
        #self.SetSelectedDomainField()
        #self.SetSelectedSpeciesField()

    def FillAvailableSpeciesList(self):
        model = QtGui.QStandardItemModel()
        avSpecies = list()
        #avSpecies = self.dataContainer.GetAvailableSpeciesNames()
        #for species in avSpecies:
        #    item = QtGui.QStandardItem(species)
        #    item.setCheckable(True)
        #    model.appendRow(item)
        #model.itemChanged.connect(self.Item_Changed)
        #self.selectedSpecies_listView.setModel(model)

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
        #self.dataContainer.SetSelectedSpeciesFields()
        #self.AddFieldsToPlot(self.dataContainer.GetSelectedSpeciesFields(), self.speciesFieldPlotDimension)
        self.opacity.RemoveAllPoints()
        self.color.RemoveAllPoints()
        self.opacity.AddPoint(0, 0.0)
        self.opacity.AddPoint(self.maxvalue, 1.0)

        self.color.AddRGBPoint(0.0, 0, 0, 1)
        self.color.AddRGBPoint(0.2*self.maxvalue, 0, 0, 1)
        self.color.AddRGBPoint(0.4*self.maxvalue, 0, 0, 1)
        self.color.AddRGBPoint(1.0*self.maxvalue, 0, 0, 1)

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
        

        volumeprop = vtk.vtkVolumeProperty()

        #volumeprop.SetIndependentComponents(ncomp)
        volumeprop.IndependentComponentsOn()
        volumeprop.SetInterpolationTypeToLinear()

        charge = self.dataContainer.GetSpeciesField("plasma", "Charge density")
        axisz = charge.GetAxisDataInOriginalUnits("x", 20)
        axisy = charge.GetAxisDataInOriginalUnits("y", 20)
        axisx = charge.GetAxisDataInOriginalUnits("z", 20)
        
        dz = (axisz[1]-axisz[0])
        dy = (axisy[1]-axisy[0])
        dx = (axisx[1]-axisx[0])

        chargeData = np.absolute(charge.GetAllFieldDataInOriginalUnits(20))
        minvalue = np.amin(chargeData)
        maxvalue = np.amax(chargeData)

        den1 = 255.0/maxvalue
        chargeData = np.round(den1 * chargeData)

        # Change data from float to unsigned char
        npdatauchar = np.array(chargeData, dtype=np.uint8)
        minvalue = np.amin(npdatauchar)
        self.maxvalue = np.amax(npdatauchar)

        self.opacity = vtk.vtkPiecewiseFunction()
        self.color = vtk.vtkColorTransferFunction()

        self.opacity.AddPoint(0, 0.1)
        self.opacity.AddPoint(0.5*self.maxvalue, 0.1)
        self.opacity.AddPoint(self.maxvalue, 0.1)
        
        self.color.AddRGBPoint(0.0,0, 0, 1)
        self.color.AddRGBPoint(100, 1.000,0, 0)
        self.color.AddRGBPoint(self.maxvalue, 0, 1.0, 0)

        volumeprop.SetColor(0,self.color)
        volumeprop.SetScalarOpacity(0,self.opacity)
        volumeprop.ShadeOff(0)

        dataImport = vtk.vtkImageImport()
        dataImport.SetImportVoidPointer(npdatauchar)

        dataImport.SetDataScalarTypeToUnsignedChar()

        # Number of scalar components
        dataImport.SetNumberOfScalarComponents(1)
        # The following two functions describe how the data is stored
        # and the dimensions of the array it is stored in.
        dataImport.SetDataExtent(0, npdatauchar.shape[0]-1, 0, npdatauchar.shape[1]-1, 0, npdatauchar.shape[2]-1)
        dataImport.SetWholeExtent(0, npdatauchar.shape[0]-1, 0, npdatauchar.shape[1]-1, 0, npdatauchar.shape[2]-1)
        dataImport.SetDataSpacing(dx,dy,dz)
        dataImport.SetDataOrigin(axisx[0],axisy[0],axisz[0])

        dataImport.Update()

        # Set the mapper
        mapper = vtk.vtkGPUVolumeRayCastMapper()

        # Add data to the mapper
        mapper.SetInputConnection(dataImport.GetOutputPort())

        # The class vtkVolume is used to pair the previously declared volume
        # as well as the properties to be used when rendering that volume.
        volume = vtk.vtkVolume()
        volume.SetMapper(mapper)
        volume.SetProperty(volumeprop)
        volume.GetProperty()

        planeClip = vtk.vtkPlane()
        planeClip.SetOrigin((axisz[0]+axisz[1])/2.0-axisz[0],0.0,0.0)
        planeClip.SetNormal(0.0, 0.0, -1.0)

        light = vtk.vtkLight()
        light.SetColor(1.0, 0.0, 0.0)
        light.SwitchOn()
        light.SetIntensity(1)
        #renderer.AddLight(light)

        # Add the volume to the renderer ...
        self.renderer.AddVolume(volume)
        self.renderer.ResetCamera()

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