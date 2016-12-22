# -*- coding: utf-8 -*-

#Copyright 2016 Ángel Ferran Pousa
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

import gc
import os
import sys

from PyQt5.uic import loadUiType
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from VisualPIC.Views.createAnimationWindow import CreateAnimationWindow
from VisualPIC.Views.particleTrackerWindow import ParticleTrackerWindow
from VisualPIC.DataHandling.dataContainer import DataContainer
from VisualPIC.DataHandling.fieldToPlot import FieldToPlot
from VisualPIC.DataHandling.rawDataSetToPlot import RawDataSetToPlot
from VisualPIC.DataHandling.subplot import *
from VisualPIC.DataPlotting.colorMapsCollection import ColorMapsCollection
from VisualPIC.DataPlotting.dataPlotter import DataPlotter
from VisualPIC.Controls.plotFieldItem import PlotFieldItem
import VisualPIC.DataHandling.unitConverters as unitConverters


if getattr(sys, 'frozen', False):
    # we are running in a bundle
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
guipath = os.path.join( bundle_dir, 'DataVisualizerGUI.ui' )

Ui_MainWindow, QMainWindow = loadUiType(guipath)

	
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.dataContainer = DataContainer()
        self.colorMapsCollection = ColorMapsCollection()
        self.dataPlotter = DataPlotter(self.colorMapsCollection)
        self.InitialUIValues()
        self.RegisterUIEvents()
        self.subplotList = list()
        self.currentAxesFieldsToPlot = list()
        self.SetListOfPlotPositions()
        self.CreateCanvasAndFigure()
        self.increaseRowsColumnsCounter = 0
        self.speciesFieldPlotDimension = "2D"
        self.domainFieldPlotDimension = "2D"
        """ Backups for removed UI items for each simulation code """
        self.removedNormalizationTab = None
        self.timeSteps = np.zeros(1)
        
    def CreateCanvasAndFigure(self):
        self.figure = Figure()
        self.figure.patch.set_facecolor("white")
        self.canvas = FigureCanvas(self.figure)
        self.plotWidget_layout.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, self.plot_Widget, coordinates=True)
        self.plotWidget_layout.addWidget(self.toolbar)
    
    def InitialUIValues(self):
        # due to 2D button toggled
        self.freeRaw_widget.setVisible(True)
        self.premadeRaw_widget.setVisible(False)
        self.yRaw_comboBox.setEnabled(True)
    
    def RegisterUIEvents(self):
        self.browse_Button.clicked.connect(self.BrowseButton_Clicked)
        self.folderLocation_lineEdit.textChanged.connect(self.FolderLocationlineEdit_TextChanged)
        self.loadData_Button.clicked.connect(self.LoadDataButton_Cicked)
        self.addDomainField_Button.clicked.connect(self.AddDomainFieldButton_Clicked)
        self.addSpeciesField_Button.clicked.connect(self.AddSpeciesFieldButton_Clicked)
        self.av2DDomainFields_comboBox.currentIndexChanged.connect(self.Av2DDomainFieldsComboBox_IndexChanged)
        self.avSpeciesFields_comboBox.currentIndexChanged.connect(self.AvSpeciesFieldsComboBox_IndexChanged)
        self.timeStep_Slider.sliderReleased.connect(self.TimeStepSlider_Released)
        self.timeStep_Slider.valueChanged.connect(self.TimeStepSlider_ValueChanged)
        self.rows_spinBox.valueChanged.connect(self.RowsSpinBox_ValueChanged)
        self.columns_spinBox.valueChanged.connect(self.ColumnsSpinBox_ValueChanged)
        self.nextStep_Button.clicked.connect(self.NextButton_Clicked)
        self.prevStep_Button.clicked.connect(self.PrevButton_Clicked)
        self.oneDimSpeciesField_radioButton.toggled.connect(self.SpeciesFieldsRadioButton_Toggled)
        self.twoDimSpeciesField_radioButton.toggled.connect(self.SpeciesFieldsRadioButton_Toggled)
        self.oneDimDomainField_radioButton.toggled.connect(self.DomainFieldsRadioButton_Toggled)
        self.twoDimDomainField_radioButton.toggled.connect(self.DomainFieldsRadioButton_Toggled)
        self.rawPlotType_radioButton_1.toggled.connect(self.RawFieldsRadioButton_Toggled)
        self.rawPlotType_radioButton_2.toggled.connect(self.RawFieldsRadioButton_Toggled)
        self.rawPlotType_radioButton_3.toggled.connect(self.RawFieldsRadioButton_Toggled)
        self.plot_pushButton.clicked.connect(self.PlotButton_Clicked)
        self.actionParticle_Tracker.triggered.connect(self.ActionParticleTracker_Toggled)
        self.actionMake_video.triggered.connect(self.ActionMakeVideo_Toggled)
        self.setNormalization_Button.clicked.connect(self.SetNormalizationButton_Clicked)
        self.addRawField_Button.clicked.connect(self.AddRawFieldButton_Clicked)

    """
    UI event handlers
    """
    def BrowseButton_Clicked(self):
        self.OpenFolderDialog()
        
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

    def RowsSpinBox_ValueChanged(self):
        self.SetListOfPlotPositions()

    def ColumnsSpinBox_ValueChanged(self):
        self.SetListOfPlotPositions()

    def SetNormalizationButton_Clicked(self):
        n_p = float(self.plasmaDensity_lineEdit.text())
        self.unitConverter.SetNormalizationFactor(n_p)
    
    def LoadDataButton_Cicked(self):
        self.ClearData()
        self.dataContainer.ClearData()
        self.LoadFolderData()
        self.unitConverter = unitConverters.UnitConverterSelector.GetUnitConverter(self.dataContainer.GetSimulationCodeName())
        self.AdaptUIToSpecificSimulationCode()

    def AdaptUIToSpecificSimulationCode(self):
        simulationCode = self.dataContainer.GetSimulationCodeName()
        codesWithNormalizedUnits = ["Osiris", "HiPACE"]
        if simulationCode not in codesWithNormalizedUnits:
            self.removedNormalizationTab = self.tabWidget_2.widget(2)
            self.tabWidget_2.removeTab(2)
        elif self.removedNormalizationTab != None:
            self.tabWidget_2.addTab(self.removedNormalizationTab, "Normalization")
            self.removedNormalizationTab = None
        
    def FolderLocationlineEdit_TextChanged(self):
        folderPath = str(self.folderLocation_lineEdit.text())
        self.dataContainer.SetDataFolderLocation(folderPath)
    
    def ActionParticleTracker_Toggled(self):
        self.particleTracker = ParticleTrackerWindow(self.dataContainer, self.unitConverter, self.colorMapsCollection, self.dataPlotter)
        self.particleTracker.show()

    def ActionMakeVideo_Toggled(self):
        AnimationWindow = CreateAnimationWindow(self)
        AnimationWindow.exec_()
        
    def SpeciesFieldsRadioButton_Toggled(self):
        if self.oneDimSpeciesField_radioButton.isChecked():
            self.speciesFieldPlotDimension = "1D"
        elif self.twoDimSpeciesField_radioButton.isChecked(): 
            self.speciesFieldPlotDimension = "2D"
            
    def DomainFieldsRadioButton_Toggled(self):
        if self.oneDimDomainField_radioButton.isChecked():
            self.domainFieldPlotDimension = "1D"
        elif self.twoDimDomainField_radioButton.isChecked():
            self.domainFieldPlotDimension = "2D"
            
    def RawFieldsRadioButton_Toggled(self):
        if self.rawPlotType_radioButton_1.isChecked():
            self.freeRaw_widget.setVisible(True)
            self.premadeRaw_widget.setVisible(False)
            self.zRaw_comboBox.setEnabled(False)
        elif self.rawPlotType_radioButton_2.isChecked():
            self.freeRaw_widget.setVisible(True)
            self.premadeRaw_widget.setVisible(False)
            self.zRaw_comboBox.setEnabled(True)
        elif self.rawPlotType_radioButton_3.isChecked():
            self.freeRaw_widget.setVisible(False)
            self.premadeRaw_widget.setVisible(True)
            
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
        
    def AddRawFieldButton_Clicked(self):
        speciesName = self.rawFieldSpecies_comboBox.currentText()
        xDataSetName = self.xRaw_comboBox.currentText()
        yDataSetName = self.yRaw_comboBox.currentText()
        if self.rawPlotType_radioButton_2.isChecked():
            zDataSetName = self.zRaw_comboBox.currentText()
        dataSets = {}
        for species in self.dataContainer.GetAvailableSpecies():
            if species.GetName() == speciesName:
               xDataSet = species.GetRawDataSet(xDataSetName) 
               dataSets["x"] = RawDataSetToPlot(xDataSet, self.unitConverter)
               yDataSet = species.GetRawDataSet(yDataSetName) 
               dataSets["y"] = RawDataSetToPlot(yDataSet, self.unitConverter)
               pxDataSet = species.GetRawDataSet("Pz") 
               dataSets["Px"] = RawDataSetToPlot(pxDataSet, self.unitConverter)
               pyDataSet = species.GetRawDataSet("Py") 
               dataSets["Py"] = RawDataSetToPlot(pyDataSet, self.unitConverter)
               if self.rawPlotType_radioButton_2.isChecked():
                   zDataSet = species.GetRawDataSet(zDataSetName) 
                   dataSets["z"] = RawDataSetToPlot(zDataSet, self.unitConverter)
                   pzDataSet = species.GetRawDataSet("Pz") 
                   dataSets["Pz"] = RawDataSetToPlot(pzDataSet, self.unitConverter)
               weightingDataSet = species.GetRawDataSet("Charge")
               dataSets["weight"] = RawDataSetToPlot(weightingDataSet, self.unitConverter)
               self.AddRawDataSubplot(dataSets)

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

    def OpenFolderDialog(self):
        folderPath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select MS Folder", self.dataContainer.GetFolderPath()))
        if folderPath != "":
            self.SetFolderPath(folderPath)
        
    def SetFolderPath(self, folderPath):
        self.dataContainer.SetDataFolderLocation(folderPath)
        self.folderLocation_lineEdit.setText(folderPath)

    def SetListOfPlotPositions(self):
        self.plotPosition_comboBox.clear()
        rows = self.rows_spinBox.value()
        columns = self.columns_spinBox.value()
        total = rows*columns
        positionsArray = np.linspace(1,total,total)
        positionsList = list()
        for item in positionsArray:
            positionsList.append(str(int(item)))
        self.plotPosition_comboBox.addItems(positionsList)

    def AddRawDataSubplot(self, dataSets):
        plotPosition = len(self.subplotList)+1
        subplot = RawDataSubplot(plotPosition, self.colorMapsCollection, dataSets)
        self.subplotList.append(subplot)
        self.SetAutoColumnsAndRows()
        wid = PlotFieldItem(subplot, self)
        wid2 = QtWidgets.QListWidgetItem()
        wid2.setSizeHint(QtCore.QSize(100, 40))
        self.fieldsToPlot_listWidget.addItem(wid2)
        self.fieldsToPlot_listWidget.setItemWidget(wid2, wid)
        self.SetTimeSteps()
        
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
        
    def LoadFolderData(self):
        self.dataContainer.LoadData()
        self.av2DDomainFields_comboBox.clear()
        self.av2DDomainFields_comboBox.addItems(self.dataContainer.GetAvailableDomainFieldsNames())
        self.FillAvailableSpeciesList()
        self.FillRawData()
        self.SetSelectedDomainField()
        self.SetSelectedSpeciesField()
    
    def SetSelectedDomainField(self):
        self.dataContainer.SetSelectedDomainField(self.av2DDomainFields_comboBox.currentText())
        
    def SetSelectedSpeciesField(self):
        self.dataContainer.SetSelectedSpeciesField(self.avSpeciesFields_comboBox.currentText())

    def FillRawData(self):
        self.rawFieldSpecies_comboBox.clear()
        speciesNames = list()
        for species in self.dataContainer.GetSpeciesWithRawData():
            speciesNames.append(species.GetName())
        self.rawFieldSpecies_comboBox.addItems(speciesNames)
        self.FillSpeciesRawData(self.rawFieldSpecies_comboBox.currentText())
    
    def FillSpeciesRawData(self, speciesName):
        for species in self.dataContainer.GetSpeciesWithRawData():
            if speciesName == species.GetName():
                self.xRaw_comboBox.addItems(species.GetRawDataSetsNamesList())
                self.yRaw_comboBox.addItems(species.GetRawDataSetsNamesList())
                self.zRaw_comboBox.addItems(species.GetRawDataSetsNamesList())
        
    def AddFieldsToPlot(self, fields, fieldPlotDimension):
        fldList = list()
        for fld in fields:
            fieldToPlot = FieldToPlot(fld, fieldPlotDimension, self.unitConverter, self.colorMapsCollection, isPartOfMultiplot = len(fields)>1)
            fldList.append(fieldToPlot)
        plotPosition = len(self.subplotList)+1
        subplot = FieldSubplot(plotPosition, self.colorMapsCollection, fldList)
        self.subplotList.append(subplot)
        self.SetAutoColumnsAndRows()
        wid = PlotFieldItem(subplot, self)
        wid2 = QtWidgets.QListWidgetItem()
        wid2.setSizeHint(QtCore.QSize(100, 40))
        self.fieldsToPlot_listWidget.addItem(wid2)
        self.fieldsToPlot_listWidget.setItemWidget(wid2, wid)
        self.SetTimeSteps()
            
    def SetAutoColumnsAndRows(self):
        rows = self.rows_spinBox.value()
        columns = self.columns_spinBox.value()
        if rows*columns < len(self.subplotList):
            if self.increaseRowsColumnsCounter % 2 == 0:
                self.IncreaseRows()
            else:
                self.IncreaseColumns()
            self.increaseRowsColumnsCounter += 1
                
    def IncreaseColumns(self):
        self.columns_spinBox.stepUp()
        
    def IncreaseRows(self):
        self.rows_spinBox.stepUp()
        
    def DecreaseColumns(self):
        self.columns_spinBox.stepDown()
        
    def DecreaseRows(self):
        self.rows_spinBox.stepDown()
        
    def MakePlots(self):
        rows = self.rows_spinBox.value()
        columns = self.columns_spinBox.value()
        timeStep = self.timeStep_Slider.value()
        self.dataPlotter.MakePlot(self.figure, self.subplotList, rows, columns, timeStep)
        self.canvas.draw()
        
    #def PlotDomainField(self):#, fieldName, timeStep):
    #    fieldName = self.dataContainer.GetSelectedDomainFieldName();
    #    timeStep = self.timeStep_Slider.value()
    #    for field in self.dataContainer.GetAvailableDomainFields():
    #        if field.GetName() == fieldName:
    #            plotData = field.GetPlotData(timeStep)
    #            self.AddPlot(self.dataPlotter.GetSimplePlot(plotData))
            
    #def AddPlot(self, figure):
    #    if self.plotWidget_layout.count() == 0:
    #        self.figure = figure
    #        self.canvas = FigureCanvas(self.figure)
    #        self.plotWidget_layout.addWidget(self.canvas)
    #        self.canvas.draw()
    #    else:
    #        self.dataPlotter.UpdateFigure(self.figure)
    #        self.canvas.draw()
    #        gc.collect()
            
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