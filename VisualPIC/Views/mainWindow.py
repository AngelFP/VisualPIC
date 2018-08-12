# -*- coding: utf-8 -*-

#Copyright 2016-2018 Angel Ferran Pousa, DESY
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
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas)

from VisualPIC.Views.createAnimationWindow import CreateAnimationWindow
from VisualPIC.Views.simulationParametersWindow import SimulationParametersWindow
from VisualPIC.Views.aboutWindow import AboutWindow
from VisualPIC.Views.particleTrackerWindow import ParticleTrackerWindow
from VisualPIC.Views.visualizer3DvtkWindow import Visualizer3DvtkWindow
from VisualPIC.DataHandling.dataContainer import DataContainer
from VisualPIC.DataPlotting.fieldToPlot import FieldToPlot
from VisualPIC.DataPlotting.rawDataSetToPlot import RawDataSetToPlot
from VisualPIC.DataPlotting.subplot import *
from VisualPIC.DataPlotting.colorMapsCollection import ColorMapsCollection
from VisualPIC.DataPlotting.dataPlotter import DataPlotter
from VisualPIC.Controls.subplotItem import SubplotItem
from VisualPIC.Controls.customNavigationToolbar import (CustomNavigationToolbar
                                                        as NavigationToolbar)


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
        self.set_ui_icons()
        self.data_container = DataContainer()
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
        self.time_steps = np.zeros(1)

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
        
    def CreateCanvasAndFigure(self):
        self.figure = Figure()
        #self.figure.patch.set_facecolor("white")
        self.canvas = FigureCanvas(self.figure)
        self.plotWidget_layout.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, self.plot_Widget, coordinates=True)
        self.plotWidget_layout.addWidget(self.toolbar)
    
    def InitialUIValues(self):
        # due to 2D button toggled
        self.addLaser_checkBox.setVisible(False)
        self.freeRaw_widget.setVisible(True)
        self.premadeRaw_widget.setVisible(False)
        self.yRaw_comboBox.setEnabled(True)
    
    def RegisterUIEvents(self):
        self.browse_Button.clicked.connect(self.BrowseButton_Clicked)
        self.folderLocation_lineEdit.textChanged.connect(self.FolderLocationlineEdit_TextChanged)
        self.loadData_Button.clicked.connect(self.LoadDataButton_Cicked)
        self.addDomainField_Button.clicked.connect(self.add_domain_fieldButton_Clicked)
        self.addSpeciesField_Button.clicked.connect(self.add_speciesFieldButton_Clicked)
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
        self.actionSimulation_parameters.triggered.connect(self.ActionSimulationParameters_Toggled)
        self.actionAbout.triggered.connect(self.ActionAbout_Toggled)
        self.actionOpen_Folder.triggered.connect(self.BrowseButton_Clicked)
        self.action3D_Visualizer.triggered.connect(self.Action3D_Visualizer_Toggled)
        self.addRawField_Button.clicked.connect(self.AddRawFieldButton_Clicked)

    """
    UI event handlers
    """
    def BrowseButton_Clicked(self):
        self.OpenFolderDialog()
        
    def Av2DDomainFieldsComboBox_IndexChanged(self):
        self.set_selected_domain_field()

    def AvSpeciesFieldsComboBox_IndexChanged(self):
        self.set_selected_species_field()

    def TimeStepSlider_Released(self):
        if self.timeStep_Slider.value() in self.time_steps:
            self.MakePlots()
        else:
            val = self.timeStep_Slider.value()
            closestHigher = self.time_steps[np.where(self.time_steps > val)[0][0]]
            closestLower = self.time_steps[np.where(self.time_steps < val)[0][-1]]
            if abs(val-closestHigher) < abs(val-closestLower):
                self.timeStep_Slider.setValue(closestHigher)
            else:
                self.timeStep_Slider.setValue(closestLower)
            self.MakePlots()

    def RowsSpinBox_ValueChanged(self):
        self.SetListOfPlotPositions()

    def ColumnsSpinBox_ValueChanged(self):
        self.SetListOfPlotPositions()
    
    def LoadDataButton_Cicked(self):
        self.clear_data()
        self.data_container.clear_data()
        self.LoadFolderData()
        self.AdaptUIToSpecificSimulationCode()
        self.AdaptUIToSimulationParams()

    def AdaptUIToSpecificSimulationCode(self):
        simulationCode = self.data_container.get_simulation_code_name()
        codesWithNormalizedUnits = ["Osiris", "HiPACE"]
        if simulationCode not in codesWithNormalizedUnits:
            self.removedNormalizationTab = self.tabWidget_2.widget(2)
            self.tabWidget_2.removeTab(2)
        elif self.removedNormalizationTab != None:
            self.tabWidget_2.addTab(self.removedNormalizationTab, "Normalization")
            self.removedNormalizationTab = None

    def AdaptUIToSimulationParams(self):
        simulationParams = self.data_container.get_simulation_parameters()
        if 'isLaser' in simulationParams:
            isLaser = simulationParams["isLaser"]
            if ("Normalized Vector Potential" in self.data_container.get_available_domain_fields_names()) or ("a_mod" in self.data_container.get_available_domain_fields_names()):
                self.addLaser_checkBox.setVisible(isLaser)
        
    def FolderLocationlineEdit_TextChanged(self):
        folderPath = str(self.folderLocation_lineEdit.text())
        self.data_container.set_data_folder_location(folderPath)

    def ActionParticleTracker_Toggled(self):
        self.particleTracker = ParticleTrackerWindow(self.data_container, self.colorMapsCollection, self.dataPlotter)
        screenGeometry = QtWidgets.QApplication.desktop().screenGeometry()
        x = (screenGeometry.width()-self.particleTracker.width()) / 2;
        y = (screenGeometry.height()-self.particleTracker.height()) / 2 -20;
        self.particleTracker.move(x, y);
        self.particleTracker.show()

    def Action3D_Visualizer_Toggled(self):
        self.visualizer3D = Visualizer3DvtkWindow(self.data_container)
        screenGeometry = QtWidgets.QApplication.desktop().screenGeometry()
        x = (screenGeometry.width()-self.visualizer3D.width()) / 2;
        y = (screenGeometry.height()-self.visualizer3D.height()) / 2 -20;
        self.visualizer3D.move(x, y);
        self.visualizer3D.show()

    def ActionMakeVideo_Toggled(self):
        AnimationWindow = CreateAnimationWindow(self)
        AnimationWindow.exec_()

    def ActionSimulationParameters_Toggled(self):
        ParametersWindow = SimulationParametersWindow(self)
        ParametersWindow.exec_()

    def ActionAbout_Toggled(self):
        aboutWindow = AboutWindow(self)
        aboutWindow.exec_()
        
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
        currentIndex = np.where(self.time_steps == currentTimeStep)[0][0]
        if currentIndex < len(self.time_steps)-1:
            self.timeStep_Slider.setValue(self.time_steps[currentIndex + 1])
        self.MakePlots()
        
    def PrevButton_Clicked(self):
        currentTimeStep = self.timeStep_Slider.value()
        currentIndex = np.where(self.time_steps == currentTimeStep)[0][0]
        if currentIndex > 0:
            self.timeStep_Slider.setValue(self.time_steps[currentIndex - 1])
        self.MakePlots()
        
    def AddRawFieldButton_Clicked(self):
        species_name = self.rawFieldSpecies_comboBox.currentText()
        xDataSetName = self.xRaw_comboBox.currentText()
        yDataSetName = self.yRaw_comboBox.currentText()
        if self.rawPlotType_radioButton_2.isChecked():
            zDataSetName = self.zRaw_comboBox.currentText()
        dataSets = {}
        for species in self.data_container.get_available_species():
            if species.get_name() == species_name:
               xDataSet = species.get_raw_dataset(xDataSetName) 
               dataSets["x"] = RawDataSetToPlot(xDataSet)
               yDataSet = species.get_raw_dataset(yDataSetName) 
               dataSets["y"] = RawDataSetToPlot(yDataSet)
               pxDataSet = species.get_raw_dataset("Pz") 
               dataSets["Px"] = RawDataSetToPlot(pxDataSet)
               pyDataSet = species.get_raw_dataset("Py") 
               dataSets["Py"] = RawDataSetToPlot(pyDataSet)
               if self.rawPlotType_radioButton_2.isChecked():
                   zDataSet = species.get_raw_dataset(zDataSetName) 
                   dataSets["z"] = RawDataSetToPlot(zDataSet)
                   pzDataSet = species.get_raw_dataset("Pz") 
                   dataSets["Pz"] = RawDataSetToPlot(pzDataSet)
               weightingDataSet = species.get_raw_dataset("Charge")
               dataSets["weight"] = RawDataSetToPlot(weightingDataSet)
               self.AddRawDataSubplot(dataSets)

    def PlotButton_Clicked(self):
        self.MakePlots()
        
    def add_domain_fieldButton_Clicked(self):
        self.AddFieldsToPlot(self.data_container.get_selected_domain_field(), self.domainFieldPlotDimension)
        	
    def add_speciesFieldButton_Clicked(self):
        self.data_container.set_selected_species_fields()
        if self.addLaser_checkBox.isVisible() and self.addLaser_checkBox.checkState():
            fields = self.data_container.get_selected_species_fields()
            if "Normalized Vector Potential" in self.data_container.get_available_domain_fields_names():
                fields.append(self.data_container.get_domain_field("Normalized Vector Potential"))
            elif "a_mod" in self.data_container.get_available_domain_fields_names():
                fields.append(self.data_container.get_domain_field("a_mod"))
            self.AddFieldsToPlot(fields, self.speciesFieldPlotDimension)
        else:
            self.AddFieldsToPlot(self.data_container.get_selected_species_fields(), self.speciesFieldPlotDimension)


    """
    Called from UI event handlers
    """

    def OpenFolderDialog(self):
        folderPath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select MS Folder", self.data_container.get_folder_path()))
        if folderPath != "":
            self.SetFolderPath(folderPath)
        
    def SetFolderPath(self, folderPath):
        self.data_container.set_data_folder_location(folderPath)
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
        wid = SubplotItem(subplot, self.MakePlots, self)
        wid2 = QtWidgets.QListWidgetItem()
        wid2.setSizeHint(QtCore.QSize(100, 40))
        self.fieldsToPlot_listWidget.addItem(wid2)
        self.fieldsToPlot_listWidget.setItemWidget(wid2, wid)
        self.SetTimeSteps()
        
    def FillAvailableSpeciesList(self):
        model = QtGui.QStandardItemModel()
        avSpecies = list()
        avSpecies = self.data_container.get_available_species_names()
        for species in avSpecies:
            item = QtGui.QStandardItem(species)
            item.setCheckable(True)
            model.appendRow(item)
        model.itemChanged.connect(self.Item_Changed)
        self.selectedSpecies_listView.setModel(model)

    def Item_Changed(self,item):
        # If the item is checked, add the species to the list of selected species
        if item.checkState():
            self.data_container.add_selected_species(item.text())
        else:
            self.data_container.remove_selected_species(item.text())
        self.avSpeciesFields_comboBox.clear()
        self.avSpeciesFields_comboBox.addItems(self.data_container.get_commonly_available_fields())
    
    def clear_data(self):
        self.rows_spinBox.setValue(1)
        self.columns_spinBox.setValue(1)
        self.fieldsToPlot_listWidget.clear()
        self.currentAxesFieldsToPlot[:] = []
        self.subplotList[:] = []
        
    def LoadFolderData(self):
        ParametersWindow = SimulationParametersWindow(self)
        ParametersWindow.exec_()
        self.data_container.load_data()
        self.av2DDomainFields_comboBox.clear()
        self.av2DDomainFields_comboBox.addItems(self.data_container.get_available_domain_fields_names())
        self.FillAvailableSpeciesList()
        self.FillRawData()
        self.set_selected_domain_field()
        self.set_selected_species_field()
    
    def set_selected_domain_field(self):
        self.data_container.set_selected_domain_field(self.av2DDomainFields_comboBox.currentText())
        
    def set_selected_species_field(self):
        self.data_container.set_selected_species_field(self.avSpeciesFields_comboBox.currentText())

    def FillRawData(self):
        self.rawFieldSpecies_comboBox.clear()
        species_names = list()
        for species in self.data_container.get_species_with_raw_data():
            species_names.append(species.get_name())
        self.rawFieldSpecies_comboBox.addItems(species_names)
        self.FillSpeciesRawData(self.rawFieldSpecies_comboBox.currentText())
    
    def FillSpeciesRawData(self, species_name):
        self.xRaw_comboBox.clear()
        self.yRaw_comboBox.clear()
        self.zRaw_comboBox.clear()
        for species in self.data_container.get_species_with_raw_data():
            if species_name == species.get_name():
                self.xRaw_comboBox.addItems(species.get_raw_dataset_names_list())
                self.yRaw_comboBox.addItems(species.get_raw_dataset_names_list())
                self.zRaw_comboBox.addItems(species.get_raw_dataset_names_list())
        
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
        time_step = self.timeStep_Slider.value()
        self.dataPlotter.MakePlot(self.figure, self.subplotList, rows, columns, time_step)
        self.canvas.draw()
            
    def RemoveSubplot(self, item):
        index = self.subplotList.index(item.subplot)
        self.subplotList.remove(item.subplot)
        self.fieldsToPlot_listWidget.takeItem(index)
        for subplot in self.subplotList:
            if subplot.get_position() > index+1:
                subplot.set_position(subplot.get_position()-1)
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
                self.time_steps = subplot.get_time_steps()
            else :
                self.time_steps = np.intersect1d(self.time_steps, subplot.get_time_steps())
            i+=1
        minTime = min(self.time_steps)
        maxTime = max(self.time_steps)
        self.timeStep_Slider.setMinimum(minTime)
        self.timeStep_Slider.setMaximum(maxTime)
