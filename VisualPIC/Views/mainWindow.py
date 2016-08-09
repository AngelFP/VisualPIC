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


from PyQt4.uic import loadUiType
from PyQt4 import QtCore, QtGui
import numpy as np
import gc
import os
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from VisualPIC.Views.createAnimationWindow import CreateAnimationWindow
from VisualPIC.DataReading.availableData import AvailableData 
from VisualPIC.DataPlotting.colorMapsCollection import ColorMapsCollection
from VisualPIC.DataPlotting.dataPlotter import DataPlotter
from VisualPIC.DataHandling.fieldToPlot import FieldToPlot
from VisualPIC.DataHandling.rawDataSetToPlot import RawDataSetToPlot
from VisualPIC.DataHandling.subplot import Subplot
from VisualPIC.Controls.plotFieldItem import PlotFieldItem
import VisualPIC.DataHandling.unitConverters as unitConverters

#from navigationToolbar2Class import NavigationToolbar2QT as NavigationToolbar

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
        self.unitConverter = unitConverters.OsirisUnitConverter()
        self.availableData = AvailableData()
        self.colorMapsCollection = ColorMapsCollection()
        self.dataPlotter = DataPlotter(self.colorMapsCollection)
        self.InitialUIValues()
        self.RegisterUIEvents()
#        self.fieldsToPlot = list()
        self.subplotList = list()
        self.currentAxesFieldsToPlot = list()
        self.SetListOfPlotPositions()
        self.CreateCanvasAndFigure()
        self.increaseRowsColumnsCounter = 0
        
        self.speciesFieldPlotDimension = "2D"
        self.domainFieldPlotDimension = "2D"

        
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
        
        self.browse_Button.clicked.connect(self.OpenFolderDialog)
        self.folderLocation_lineEdit.textChanged.connect(self.folderLocationlineEdit_TextChanged)
        self.loadData_Button.clicked.connect(self.loadDataButton_clicked)
        self.addDomainField_Button.clicked.connect(self.addDomainFieldButton_Clicked)
        self.addSpeciesField_Button.clicked.connect(self.addSpeciesFieldButton_Clicked)
        self.av2DDomainFields_comboBox.currentIndexChanged.connect(self.SetSelectedDomainField)
        self.avSpeciesFields_comboBox.currentIndexChanged.connect(self.SetSelectedSpeciesField)
        self.timeStep_Slider.sliderReleased.connect(self.PlotFields)
        self.timeStep_Slider.valueChanged.connect(self.TimeStepSlider_valueChanged)
        self.rows_spinBox.valueChanged.connect(self.SetListOfPlotPositions)
        self.columns_spinBox.valueChanged.connect(self.SetListOfPlotPositions)
        self.nextStep_Button.clicked.connect(self.NextButton_Clicked)
        self.prevStep_Button.clicked.connect(self.PrevButton_Clicked)
        self.oneDimSpeciesField_radioButton.toggled.connect(self.SpeciesFieldsRadioButton_Toggled)
        self.twoDimSpeciesField_radioButton.toggled.connect(self.SpeciesFieldsRadioButton_Toggled)
        self.oneDimDomainField_radioButton.toggled.connect(self.DomainFieldsRadioButton_Toggled)
        self.twoDimDomainField_radioButton.toggled.connect(self.DomainFieldsRadioButton_Toggled)
        self.rawPlotType_radioButton_1.toggled.connect(self.rawFieldsRadioButton_Toggled)
        self.rawPlotType_radioButton_2.toggled.connect(self.rawFieldsRadioButton_Toggled)
        self.rawPlotType_radioButton_3.toggled.connect(self.rawFieldsRadioButton_Toggled)
        self.plot_pushButton.clicked.connect(self.PlotButton_Clicked)
        self.actionMake_video.triggered.connect(self.actionMakeVideo_toggled)
        self.normalizedUnits_checkBox.toggled.connect(self.normalizedUnitsCheckBox_StatusChanged)
        self.setNormalization_Button.clicked.connect(self.setNormalizationButton_Clicked)
        self.addRawField_Button.clicked.connect(self.addRawFieldButton_Clicked)
    
    
        
        
    def setNormalizationButton_Clicked(self):
        n_p = float(self.plasmaDensity_lineEdit.text())
        self.unitConverter.setPlasmaDensity(n_p)
#        for widget in self.fieldsToPlot_listWidget.children()[0].children():
#            widget.LoadUnitsOptions()
    
    
    def normalizedUnitsCheckBox_StatusChanged(self):
        if self.normalizedUnits_checkBox.checkState():
            self.plasmaDensity_lineEdit.setEnabled(True)
            self.setNormalization_Button.setEnabled(True)
            self.unitConverter.allowNormUnits(True)
        else:
            self.plasmaDensity_lineEdit.setEnabled(False)
            self.setNormalization_Button.setEnabled(False)
            self.unitConverter.allowNormUnits(False)
    
    def loadDataButton_clicked(self):
        self.ClearData()
        self.LoadFolderData()
        
        
    def folderLocationlineEdit_TextChanged(self):
        folderPath = self.folderLocation_lineEdit.text()
        self.availableData.SetDataFolderLocation(folderPath)
    
    def actionMakeVideo_toggled(self):
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
            
    def rawFieldsRadioButton_Toggled(self):
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
            
    def TimeStepSlider_valueChanged(self):
        self.timeStep_LineEdit.setText(str(self.timeStep_Slider.value()))
        
    def NextButton_Clicked(self):
        ts = self.timeStep_Slider.value()
        self.timeStep_Slider.setValue(ts + 1)
        self.PlotFields()
        
    def PrevButton_Clicked(self):
        ts = self.timeStep_Slider.value()
        self.timeStep_Slider.setValue(ts - 1)
        self.PlotFields()
        
    def OpenFolderDialog(self):
        folderPath = QtGui.QFileDialog.getExistingDirectory(self, "Select MS Folder", self.availableData.GetFolderPath())
        if folderPath != "":
            self.SetFolderPath(folderPath)
        
    def SetFolderPath(self, folderPath):
        
        self.availableData.SetDataFolderLocation(folderPath)
        self.folderLocation_lineEdit.setText(folderPath)
    
    def ClearData(self):
        self.rows_spinBox.setValue(1)
        self.columns_spinBox.setValue(1)
        self.fieldsToPlot_listWidget.clear()
        self.currentAxesFieldsToPlot[:] = []
        #self.fieldsToPlot.clear()
        self.subplotList[:] = []
        
    def LoadFolderData(self):
        
        self.availableData.LoadFolderData()
        self.av2DDomainFields_comboBox.clear()
        self.av2DDomainFields_comboBox.addItems(self.availableData.GetAvailableDomainFieldsNames())
        self.FillAvailableSpeciesList()
        self.FillRawData()
        
        self.SetSelectedDomainField()
        self.SetSelectedSpeciesField()
        
    
    def SetSelectedDomainField(self):
        self.availableData.SetSelectedDomainField(self.av2DDomainFields_comboBox.currentText())
        
    def SetSelectedSpeciesField(self):
        self.availableData.SetSelectedSpeciesField(self.avSpeciesFields_comboBox.currentText())
    

    def FillRawData(self):
        self.rawFieldSpecies_comboBox.clear()
        speciesNames = list()
        for species in self.availableData.GetSpeciesWithRawData():
            speciesNames.append(species.GetName())
        self.rawFieldSpecies_comboBox.addItems(speciesNames)
        self.FillSpeciesRawData(self.rawFieldSpecies_comboBox.currentText())
        
    
    def FillSpeciesRawData(self, speciesName):
        for species in self.availableData.GetSpeciesWithRawData():
            if speciesName == species.GetName():
                self.xRaw_comboBox.addItems(species.GetRawDataSetsNamesList())
                self.yRaw_comboBox.addItems(species.GetRawDataSetsNamesList())
                self.zRaw_comboBox.addItems(species.GetRawDataSetsNamesList())
                
    def addRawFieldButton_Clicked(self):
        speciesName = self.rawFieldSpecies_comboBox.currentText()
        xDataSetName = self.xRaw_comboBox.currentText()
        yDataSetName = self.yRaw_comboBox.currentText()
        if self.rawPlotType_radioButton_2.isChecked():
            zDataSetName = self.zRaw_comboBox.currentText()
        dataSets = {}
        for species in self.availableData.GetAvailableSpecies():
            if species.GetName() == speciesName:
               xDataSet = species.GetRawDataSet(xDataSetName) 
               dataSets["x"] = RawDataSetToPlot(xDataSet, self.unitConverter)
               yDataSet = species.GetRawDataSet(yDataSetName) 
               dataSets["y"] = RawDataSetToPlot(yDataSet, self.unitConverter)
               if self.rawPlotType_radioButton_2.isChecked():
                   zDataSet = species.GetRawDataSet(zDataSetName) 
                   dataSets["z"] = RawDataSetToPlot(zDataSet, self.unitConverter)
               weightingDataSet = species.GetRawDataSet("q")
               dataSets["weight"] = RawDataSetToPlot(weightingDataSet, self.unitConverter)
               self.addRawDataSubplot(dataSets)
        
    def addRawDataSubplot(self, dataSets):
        plotPosition = len(self.subplotList)+1
        subplot = Subplot(plotPosition, self.colorMapsCollection, axisData = dataSets)
        self.subplotList.append(subplot)
        self.setAutoColumnsAndRows()
            
        wid = PlotFieldItem(subplot, self)
        wid2 = QtGui.QListWidgetItem()
        wid2.setSizeHint(QtCore.QSize(100, 40))
        self.fieldsToPlot_listWidget.addItem(wid2)
        self.fieldsToPlot_listWidget.setItemWidget(wid2, wid) 
        
    def FillAvailableSpeciesList(self):
        
        
        model = QtGui.QStandardItemModel()
        
        avSpecies = list()
        avSpecies = self.availableData.GetAvailableSpeciesNames()
        
        for species in avSpecies:
            item = QtGui.QStandardItem(species)
            item.setCheckable(True)
            model.appendRow(item)
        
        model.itemChanged.connect(self.on_item_changed)
        
        self.selectedSpecies_listView.setModel(model)
        
    def on_item_changed(self,item):
    # If the item is checked, add the species to the list of selected species
        if item.checkState():
            self.availableData.AddSelectedSpecies(item.text())
        else:
            self.availableData.RemoveSelectedSpecies(item.text())
            
        self.avSpeciesFields_comboBox.clear()
        self.avSpeciesFields_comboBox.addItems(self.availableData.GetCommonlyAvailableFields())
    
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
        
    # PLOTTING
    
    def PlotButton_Clicked(self):
        self.timeStep_Slider.setMaximum(self.availableData.GetNumberOfTimeSteps()-1)
        
        self.PlotFields()
        
    def addDomainFieldButton_Clicked(self):
        self.addFieldsToPlot(self.availableData.GetSelectedDomainField(), self.domainFieldPlotDimension)
        	
    def addSpeciesFieldButton_Clicked(self):
        self.availableData.SetSelectedSpeciesFields()
        self.addFieldsToPlot(self.availableData.GetSelectedSpeciesFields(), self.speciesFieldPlotDimension)
        
    def addFieldsToPlot(self, fields, fieldPlotDimension):
        fldList = list()
        for fld in fields:
            fieldToPlot = FieldToPlot(fld, fieldPlotDimension, self.unitConverter, self.colorMapsCollection, isPartOfMultiplot = len(fields)>1)
            fldList.append(fieldToPlot)
            
        plotPosition = len(self.subplotList)+1
        subplot = Subplot(plotPosition, self.colorMapsCollection, fieldsToPlotList = fldList)
        self.subplotList.append(subplot)
        self.setAutoColumnsAndRows()
            
        wid = PlotFieldItem(subplot, self)
        wid2 = QtGui.QListWidgetItem()
        wid2.setSizeHint(QtCore.QSize(100, 40))
        self.fieldsToPlot_listWidget.addItem(wid2)
        self.fieldsToPlot_listWidget.setItemWidget(wid2, wid)
        
        
#    def AddFieldToPlotOnPosition(self, fieldPosition, fieldToPlot):
#        cnt = len(self.fieldsToPlot)
#        if fieldPosition <= cnt:
#            self.fieldsToPlot[fieldPosition-1] = fieldToPlot
#        else:
#            i = cnt
#            while i < fieldPosition-1:
#                self.fieldsToPlot.append(None)
#                i+=1
#            self.fieldsToPlot.append(fieldToPlot)
#            
#    def RemoveExcessFields(self):
#        rows = self.rows_spinBox.value()
#        columns = self.columns_spinBox.value()
#        while len(self.fieldsToPlot) > rows*columns:
#            self.fieldsToPlot.remove(self.fieldsToPlot[-1])
            
    def setAutoColumnsAndRows(self):
        rows = self.rows_spinBox.value()
        columns = self.columns_spinBox.value()
        if rows*columns < len(self.subplotList):
            if self.increaseRowsColumnsCounter % 2 == 0:
                self.increaseRows()
            else:
                self.increaseColumns()
            self.increaseRowsColumnsCounter += 1
                
    def increaseColumns(self):
        self.columns_spinBox.stepUp()
        
    def increaseRows(self):
        self.rows_spinBox.stepUp()
        
    def decreaseColumns(self):
        self.columns_spinBox.stepDown()
        
    def decreaseRows(self):
        self.rows_spinBox.stepDown()
        
    def PlotFields(self):
        rows = self.rows_spinBox.value()
        columns = self.columns_spinBox.value()
        timeStep = self.timeStep_Slider.value()
        
        self.dataPlotter.MakePlot(self.figure, self.subplotList, rows, columns, timeStep)
        self.canvas.draw()
        
    def PlotDomainField(self):#, fieldName, timeStep):
        fieldName = self.availableData.GetSelectedDomainFieldName();
        timeStep = self.timeStep_Slider.value()
        for field in self.availableData.GetAvailableDomainFields():
            if field.GetName() == fieldName:
                plotData = field.GetPlotData(timeStep)
                self.AddPlot(self.dataPlotter.GetSimplePlot(plotData))
        
            
    def AddPlot(self, figure):
        
        if self.plotWidget_layout.count() == 0:
            self.figure = figure
            self.canvas = FigureCanvas(self.figure)
            
            self.plotWidget_layout.addWidget(self.canvas)
            self.canvas.draw()
        else:
            self.dataPlotter.UpdateFigure(self.figure)
            self.canvas.draw()
            gc.collect()
            
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
                    self.decreaseColumns()
                    self.increaseRowsColumnsCounter -= 1
            else:
                if len(self.subplotList) <= (rows-1)*columns:
                    self.decreaseRows()
                    self.increaseRowsColumnsCounter -= 1
#        
#        