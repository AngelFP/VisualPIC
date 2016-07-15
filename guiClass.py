
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
import copy

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from CreateAnimationWidget import CreateAnimationWidget
from availableDataClass import AvailableData
from dataPlotterClass import DataPlotter
from fieldToPlotClass import FieldToPlot
from colorMapsCollectionClass import ColorMapsCollection
from plotFieldWidgetClass import PlotFieldWidget
import unitConverters

#from navigationToolbar2Class import NavigationToolbar2QT as NavigationToolbar

if getattr(sys, 'frozen', False):
    # we are running in a bundle
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
guipath = os.path.join( bundle_dir, 'DataVisualizerGUI.ui' )

Ui_MainWindow, QMainWindow = loadUiType(guipath)

	
class GUI_MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(GUI_MainWindow, self).__init__()
        self.setupUi(self)
        self.unitConverter = unitConverters.OsirisUnitConverter()
        self.availableData = AvailableData()
        self.dataPlotter = DataPlotter()
        self.colorMapsCollection = ColorMapsCollection()
        self.InitialUIValues()
        self.RegisterUIEvents()
        self.fieldOnPlot = ""
        self.fieldsToPlot = list()
        self.currentAxesFieldsToPlot = list()
        self.SetListOfPlotPositions()
        self.CreateCanvasAndFigure()
        
     
    def StartProgressBar(self):
        self.loading_ProgressBar.setMaximum(0)
        
    def StopProgressBar(self):
        self.loading_ProgressBar.setMaximum(10)
        
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
        self.selectDomainField_Button.clicked.connect(self.SelectDomainFieldButton_Clicked)
        self.selectSpeciesField_Button.clicked.connect(self.SelectSpeciesFieldButton_Clicked)
        self.av2DDomainFields_comboBox.currentIndexChanged.connect(self.SetSelectedDomainField)
        self.avSpeciesFields_comboBox.currentIndexChanged.connect(self.SetSelectedSpeciesField)
        self.timeStep_Slider.sliderReleased.connect(self.PlotFields)
        self.timeStep_Slider.valueChanged.connect(self.TimeStepSlider_valueChanged)
        self.rows_spinBox.valueChanged.connect(self.SetListOfPlotPositions)
        self.columns_spinBox.valueChanged.connect(self.SetListOfPlotPositions)
        self.nextStep_Button.clicked.connect(self.NextButton_Clicked)
        self.prevStep_Button.clicked.connect(self.PrevButton_Clicked)
        self.availableSpeciesFields_radioButton.toggled.connect(self.SpeciesFieldsRadioButton_Toggled)
        self.customSpeciesFields_radioButton.toggled.connect(self.SpeciesFieldsRadioButton_Toggled)
        self.availableDomainFields_radioButton.toggled.connect(self.DomainFieldsRadioButton_Toggled)
        self.available1DDomainFields_radioButton.toggled.connect(self.DomainFieldsRadioButton_Toggled)
        self.customDomainFields_radioButton.toggled.connect(self.DomainFieldsRadioButton_Toggled)
        self.rawPlotType_radioButton_1.toggled.connect(self.rawFieldsRadioButton_Toggled)
        self.rawPlotType_radioButton_2.toggled.connect(self.rawFieldsRadioButton_Toggled)
        self.rawPlotType_radioButton_3.toggled.connect(self.rawFieldsRadioButton_Toggled)
        self.plot_pushButton.clicked.connect(self.PlotButton_Clicked)
        self.actionMake_video.triggered.connect(self.actionMakeVideo_toggled)
        self.normalizedUnits_checkBox.toggled.connect(self.normalizedUnitsCheckBox_StatusChanged)
        self.setNormalization_Button.clicked.connect(self.setNormalizationButton_Clicked)
    
    def rawFieldsRadioButton_Toggled(self):
        if self.rawPlotType_radioButton_1.isChecked():
            self.freeRaw_widget.setVisible(True)
            self.premadeRaw_widget.setVisible(False)
            self.yRaw_comboBox.setEnabled(False)
        elif self.rawPlotType_radioButton_2.isChecked():
            self.freeRaw_widget.setVisible(True)
            self.premadeRaw_widget.setVisible(False)
            self.yRaw_comboBox.setEnabled(True)
        elif self.rawPlotType_radioButton_3.isChecked():
            self.freeRaw_widget.setVisible(False)
            self.premadeRaw_widget.setVisible(True)
        
        
    def setNormalizationButton_Clicked(self):
        n_p = float(self.plasmaDensity_lineEdit.text())
        self.unitConverter.setPlasmaDensity(n_p)
        for widget in self.fieldsToPlot_listWidget.children()[0].children():
            widget.LoadUnitsOptions()
    
    
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
        CreateAnimationWindow = CreateAnimationWidget(self)
        CreateAnimationWindow.exec_()
        
    def SpeciesFieldsRadioButton_Toggled(self):
        if self.availableSpeciesFields_radioButton.isChecked():
            self.avSpeciesFields_comboBox.setEnabled(True)
            self.customSpeciesFields_comboBox.setEnabled(False)
        elif self.customSpeciesFields_radioButton.isChecked():
            self.avSpeciesFields_comboBox.setEnabled(False)
            self.customSpeciesFields_comboBox.setEnabled(True)      
            
    def DomainFieldsRadioButton_Toggled(self):
        if self.availableDomainFields_radioButton.isChecked():
            self.av2DDomainFields_comboBox.setEnabled(True)
            self.av1DDomainFields_comboBox.setEnabled(False)
            self.avCustomDomainFields_comboBox.setEnabled(False)
        elif self.available1DDomainFields_radioButton.isChecked():
            self.av2DDomainFields_comboBox.setEnabled(False)
            self.av1DDomainFields_comboBox.setEnabled(True)
            self.avCustomDomainFields_comboBox.setEnabled(False)  
        elif self.customDomainFields_radioButton.isChecked():
            self.av2DDomainFields_comboBox.setEnabled(False)
            self.av1DDomainFields_comboBox.setEnabled(False)
            self.avCustomDomainFields_comboBox.setEnabled(True)
            
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
        self.currentAxesFieldsToPlot.clear()
        self.fieldsToPlot.clear()
        
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
        for species in self.availableData.GetAvailableRawSpecies():
            speciesNames.append(species.GetName())
        self.rawFieldSpecies_comboBox.addItems(speciesNames)
        self.FillSpeciesRawData(self.rawFieldSpecies_comboBox.currentText())
        
    
    def FillSpeciesRawData(self, speciesName):
        for species in self.availableData.GetAvailableRawSpecies():
            if speciesName == species.GetName():
                self.xRaw_comboBox.addItems(species.GetAvailableFieldNamesList())
                self.yRaw_comboBox.addItems(species.GetAvailableFieldNamesList())
        
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
        
        plotPosition = int(self.plotPosition_comboBox.currentText())
        for fld in self.currentAxesFieldsToPlot:
            fld.SetPlotPosition(plotPosition)
            
        self.AddFieldToPlotOnPosition(plotPosition, copy.copy(self.currentAxesFieldsToPlot))
        self.RemoveExcessFields()
        self.PlotFields()
        
    def SelectDomainFieldButton_Clicked(self):
        self.SetCurrentAxesFieldsToPlot(self.availableData.GetSelectedDomainField())
	
    def SelectSpeciesFieldButton_Clicked(self):
        self.availableData.SetSelectedSpeciesFields()
        self.SetCurrentAxesFieldsToPlot(self.availableData.GetSelectedSpeciesFields())
        
    def SetCurrentAxesFieldsToPlot(self, field):
        self.fieldsToPlot_listWidget.clear()
        self.currentAxesFieldsToPlot.clear()
        if isinstance(field, list):
            fldList = list()
            i=0
            for fld in field:
                fieldToPlot = FieldToPlot(fld, self.unitConverter)
                fldList.append(fieldToPlot)
                
                wid = PlotFieldWidget(fieldToPlot, self.colorMapsCollection, len(field)>1)
                wid2 = QtGui.QListWidgetItem()
                wid2.setSizeHint(QtCore.QSize(100, 189))
                self.fieldsToPlot_listWidget.addItem(wid2)
                self.fieldsToPlot_listWidget.setItemWidget(wid2, wid)
            
                i+=1
            self.currentAxesFieldsToPlot = fldList    
        else:
            fieldToPlot = FieldToPlot(field, self.unitConverter)#, self.colorMapsCollection)
            
            wid = PlotFieldWidget(fieldToPlot, self.colorMapsCollection, False)
            wid2 = QtGui.QListWidgetItem()
            wid2.setSizeHint(QtCore.QSize(100, 189))
            self.fieldsToPlot_listWidget.addItem(wid2)
            self.fieldsToPlot_listWidget.setItemWidget(wid2, wid)
            self.currentAxesFieldsToPlot.append(fieldToPlot)
        
    def AddFieldToPlotOnPosition(self, fieldPosition, fieldToPlot):
        cnt = len(self.fieldsToPlot)
        if fieldPosition <= cnt:
            self.fieldsToPlot[fieldPosition-1] = fieldToPlot
        else:
            i = cnt
            while i < fieldPosition-1:
                self.fieldsToPlot.append(None)
                i+=1
            self.fieldsToPlot.append(fieldToPlot)
            
    def RemoveExcessFields(self):
        rows = self.rows_spinBox.value()
        columns = self.columns_spinBox.value()
        while len(self.fieldsToPlot) > rows*columns:
            self.fieldsToPlot.remove(self.fieldsToPlot[-1])
            
            
    def PlotFields(self):
        rows = self.rows_spinBox.value()
        columns = self.columns_spinBox.value()
        timeStep = self.timeStep_Slider.value()
        
        self.dataPlotter.MakePlot(self.figure, self.fieldsToPlot, rows, columns, timeStep)
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
#        
#        
#        