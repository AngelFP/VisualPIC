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

import gc
import os
import sys

from PyQt5.uic import loadUiType
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import *
import numpy as np
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)


from VisualPIC.DataHandling.dataContainer import DataContainer
from VisualPIC.DataHandling.rawDataSetToPlot import RawDataSetToPlot
from VisualPIC.DataHandling.subplot import *
from VisualPIC.DataPlotting.colorMapsCollection import ColorMapsCollection
from VisualPIC.DataPlotting.dataPlotter import DataPlotter
from VisualPIC.Controls.plotFieldItem import PlotFieldItem
from VisualPIC.Tools.particleTracking import ParticleTracker


if getattr(sys, 'frozen', False):
    # we are running in a bundle
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
guipath = os.path.join( bundle_dir, 'ParticleTracker.ui' )

Ui_ParticleTrackerWindow, QParticleTrackerWindow = loadUiType(guipath)

	
class ParticleTrackerWindow(QParticleTrackerWindow, Ui_ParticleTrackerWindow):
    def __init__(self, dataContainer, colormapsCollection, dataPlotter):
        super(ParticleTrackerWindow, self).__init__()
        self.setupUi(self)
        self.particleTracker = ParticleTracker(dataContainer)
        self.colormapsCollection = colormapsCollection
        self.dataPlotter = dataPlotter
        self.selectorSubplot = None
        self.evolSubplotList = list()
        self.instantSubplotList = list()
        self.evolSubplotRows = 1
        self.evolSubplotColumns = 1
        self.instantSubplotRows = 1
        self.instantSubplotColumns = 1
        self.increaseEvolRowsColumnsCounter = 0
        self.increaseInstantRowsColumnsCounter = 0
        self.instantTimeSteps = np.zeros(1)
        self.CreateCanvasAndFigures()
        self.FillInitialUI();
        self.RegisterUIEvents();

    def CreateCanvasAndFigures(self):
        # Graphic selector
        self.selectorFigure = Figure()
        self.selectorFigure.patch.set_facecolor("white")
        self.selectorCanvas = FigureCanvas(self.selectorFigure)
        self.selectorPlot_layout.addWidget(self.selectorCanvas)
        self.selectorCanvas.draw()
        # Evolution plots
        self.mainFigure = Figure()
        self.mainFigure.patch.set_facecolor("white")
        self.mainCanvas = FigureCanvas(self.mainFigure)
        self.mainPlot_layout.addWidget(self.mainCanvas)
        self.mainCanvas.draw()
        self.toolbar = NavigationToolbar(self.mainCanvas, self.mainPlot_widget, coordinates=True)
        self.mainPlot_layout.addWidget(self.toolbar)
        # Instant plots
        self.instantPlotsFigure = Figure()
        self.instantPlotsFigure.patch.set_facecolor("white")
        self.instantPlotsCanvas = FigureCanvas(self.instantPlotsFigure)
        self.instantPlots_layout.addWidget(self.instantPlotsCanvas)
        self.instantPlotsCanvas.draw()
        self.instantPlotsToolbar = NavigationToolbar(self.instantPlotsCanvas, self.instantPlots_widget, coordinates=True)
        self.instantPlots_layout.addWidget(self.instantPlotsToolbar)

    def CreateSelectorSubplotObject(self):
        #if self.selectorSubplot == None or self.selectorSubplot.GetPlottedSpeciesName() != self.speciesSelector_comboBox.currentText():
        speciesName = str(self.speciesSelector_comboBox.currentText())
        dataSets = {}
        xAxis = str(self.xAxis_comboBox.currentText())
        yAxis = str(self.yAxis_comboBox.currentText())
        dataSets["x"] = RawDataSetToPlot(self.particleTracker.GetSpeciesDataSet(speciesName, xAxis))
        dataSets["y"] = RawDataSetToPlot(self.particleTracker.GetSpeciesDataSet(speciesName, yAxis))
        dataSets["weight"] = RawDataSetToPlot(self.particleTracker.GetSpeciesDataSet(speciesName, "Charge"))
        self.selectorSubplot = RawDataSubplot(1, self.colormapsCollection, dataSets)
        self.selectorSubplot.SetPlotType("Scatter")
        self.selectorSubplot.SetPlotProperty("General", "DisplayColorbar", False)
        self.selectorSubplot.SetAxisProperty("x", "LabelFontSize", 10)
        self.selectorSubplot.SetAxisProperty("y", "LabelFontSize", 10)
        self.selectorSubplot.SetTitleProperty("FontSize", 0)

    def RegisterUIEvents(self):
        self.selectorTimeStep_Slider.valueChanged.connect(self.SelectorTimeStepSlider_ValueChanged)
        self.selectorTimeStep_Slider.sliderReleased.connect(self.SelectorTimeStepSlider_Released)
        self.instantTimeStep_Slider.valueChanged.connect(self.InstantTimeStepSlider_ValueChanged)
        self.instantTimeStep_Slider.sliderReleased.connect(self.InstantTimeStepSlider_Released)
        self.speciesSelector_comboBox.currentIndexChanged.connect(self.SpeciesSelectorComboBox_IndexChanged)
        self.xAxis_comboBox.currentIndexChanged.connect(self.AxisComboBox_IndexChanged)
        self.yAxis_comboBox.currentIndexChanged.connect(self.AxisComboBox_IndexChanged)
        self.rectangleSelection_Button.clicked.connect(self.RectangleSelectionButton_Clicked)
        self.findParticles_button.clicked.connect(self.FindParticlesButton_Clicked)
        self.trackParticles_Button.clicked.connect(self.TrackParticlesButton_Clicked)
        self.plotType_radioButton_1.toggled.connect(self.PlotTypeRadioButton_Toggled)
        self.plotType_radioButton_2.toggled.connect(self.PlotTypeRadioButton_Toggled)
        self.instPlotType_radioButton.toggled.connect(self.InstantPlotTypeRadioButton_Toggled)
        self.instPlotType_radioButton_2.toggled.connect(self.InstantPlotTypeRadioButton_Toggled)
        self.addToPlot_Button.clicked.connect(self.AddToPlotButton_Clicked)
        self.addToInstantPlot_Button.clicked.connect(self.AddToInstantPlotButton_Clicked)
        self.plot_pushButton.clicked.connect(self.PlotPushButton_Clicked)
        self.plotInstant_pushButton.clicked.connect(self.PlotInstantPushButton_Clicked)
        self.selectAll_checkBox.toggled.connect(self.SelectAllCheckBox_StatusChanged)
        self.browseExportPath_pushButton.clicked.connect(self.BrowseExportPathButton_Clicked)
        self.selectAllExport_checkBox.toggled.connect(self.SelectAllExportCheckBox_StatusChanged)
        self.exportData_pushButton.clicked.connect(self.ExportDataButton_Clicked)
        self.nextStep_Button.clicked.connect(self.NextButton_Clicked)
        self.prevStep_Button.clicked.connect(self.PrevButton_Clicked)

    def FillInitialUI(self):
        comboBoxItems = self.particleTracker.GetSpeciesNames()
        if len(comboBoxItems) > 0:
            comboBoxItems.insert(0, "Select Species")
        else:
            comboBoxItems.insert(0, "No species available")
        self.speciesSelector_comboBox.addItems(comboBoxItems)

    def FillEvolutionPlotsUI(self):
        self.x_comboBox.clear()
        self.y_comboBox.clear()
        self.z_comboBox.clear()
        self.x_comboBox.addItems(self.particleTracker.GetAvailableWholeSimulationQuantitiesInParticles())
        self.y_comboBox.addItems(self.particleTracker.GetAvailableWholeSimulationQuantitiesInParticles())
        self.z_comboBox.addItems(self.particleTracker.GetAvailableWholeSimulationQuantitiesInParticles())
        self.trackedParticles_Label.setText("Tracking " + str(self.particleTracker.GetTotalNumberOfTrackedParticles())+ " particle(s)")

    def FillInstantPlotsUI(self):
        self.instX_comboBox.clear()
        self.instY_comboBox.clear()
        self.instZ_comboBox.clear()
        self.instX_comboBox.addItems(self.particleTracker.GetNamesOfInstantRawDataSets())
        self.instY_comboBox.addItems(self.particleTracker.GetNamesOfInstantRawDataSets())
        self.instZ_comboBox.addItems(self.particleTracker.GetNamesOfInstantRawDataSets())
        self.trackedParticles_Label_3.setText("Tracking " + str(self.particleTracker.GetTotalNumberOfTrackedParticles())+ " particle(s)")

    def FillExportDataUI(self):
        self.CreateTrackedParticlesTable()
        self.exportPath_lineEdit.setText(self.particleTracker.GetDataLocation())

    """
    UI Events
    """
    def SelectorTimeStepSlider_ValueChanged(self):
        self.selectorTimeStep_lineEdit.setText(str(self.selectorTimeStep_Slider.value()))

    def SelectorTimeStepSlider_Released(self):
        if self.selectorTimeStep_Slider.value() not in self.timeSteps:
            val = self.selectorTimeStep_Slider.value()
            closestHigher = self.timeSteps[np.where(self.timeSteps > val)[0][0]]
            closestLower = self.timeSteps[np.where(self.timeSteps < val)[0][-1]]
            if abs(val-closestHigher) < abs(val-closestLower):
                self.selectorTimeStep_Slider.setValue(closestHigher)
            else:
                self.selectorTimeStep_Slider.setValue(closestLower)
        self.MakeSelectorPlot()
        self._CreateFineSelectionTable()

    def InstantTimeStepSlider_ValueChanged(self):
        self.instantTimeStep_lineEdit.setText(str(self.instantTimeStep_Slider.value()))

    def InstantTimeStepSlider_Released(self):
        if self.instantTimeStep_Slider.value() not in self.instantTimeSteps:
            val = self.instantTimeStep_Slider.value()
            closestHigher = self.timeSteps[np.where(self.instantTimeSteps > val)[0][0]]
            closestLower = self.timeSteps[np.where(self.instantTimeSteps < val)[0][-1]]
            if abs(val-closestHigher) < abs(val-closestLower):
                self.instantTimeStep_Slider.setValue(closestHigher)
            else:
                self.instantTimeStep_Slider.setValue(closestLower)
        self.MakeInstantPlots()

    def NextButton_Clicked(self):
        currentTimeStep = self.instantTimeStep_Slider.value()
        currentIndex = np.where(self.instantTimeSteps == currentTimeStep)[0][0]
        if currentIndex < len(self.instantTimeSteps)-1:
            self.instantTimeStep_Slider.setValue(self.instantTimeSteps[currentIndex + 1])
        self.MakeInstantPlots()
        
    def PrevButton_Clicked(self):
        currentTimeStep = self.instantTimeStep_Slider.value()
        currentIndex = np.where(self.instantTimeSteps == currentTimeStep)[0][0]
        if currentIndex > 0:
            self.instantTimeStep_Slider.setValue(self.instantTimeSteps[currentIndex - 1])
        self.MakeInstantPlots()

    def SpeciesSelectorComboBox_IndexChanged(self):
        self._SetGraphicSelectorComboBoxes()
        self.MakeSelectorPlot()
        self._CreateFineSelectionTable()

    def _SetGraphicSelectorComboBoxes(self):
        self._updatingUI = True
        speciesName = str(self.speciesSelector_comboBox.currentText())
        axisList = self.particleTracker.GetSpeciesRawDataSetNames(speciesName)
        self.xAxis_comboBox.clear()
        self.yAxis_comboBox.clear()
        self.xAxis_comboBox.addItems(axisList)
        self.yAxis_comboBox.addItems(axisList)
        if "z" in axisList:
            self.xAxis_comboBox.setCurrentIndex(axisList.index("z"))
        if "y" in axisList:
            self.yAxis_comboBox.setCurrentIndex(axisList.index("y"))
        self._updatingUI = False

    def AxisComboBox_IndexChanged(self):
        if not self._updatingUI:
            self.MakeSelectorPlot()

    def RectangleSelectionButton_Clicked(self):
        self.toggle_selector.set_active(True)

    def FindParticlesButton_Clicked(self):
        speciesName = str(self.speciesSelector_comboBox.currentText())
        timeStep = self.selectorTimeStep_Slider.value()
        filters = self.GetSelectedFilters()
        self.FindParticles(timeStep, speciesName, filters)

    def TrackParticlesButton_Clicked(self):
        self.particleTracker.SetParticlesToTrack(self.GetSelectedParticles())
        self.particleTracker.FillEvolutionOfAllDataSetsInParticles()
        self.particleTracker.MakeInstantaneousRawDataSets()
        self.FillEvolutionPlotsUI()
        self.FillInstantPlotsUI()
        self.FillExportDataUI()

    def PlotTypeRadioButton_Toggled(self):
        self.z_comboBox.setEnabled(self.plotType_radioButton_2.isChecked())

    def InstantPlotTypeRadioButton_Toggled(self):
        self.instZ_comboBox.setEnabled(self.instPlotType_radioButton_2.isChecked())

    def AddToPlotButton_Clicked(self):
        xDataSetName = str(self.x_comboBox.currentText())
        yDataSetName = str(self.y_comboBox.currentText())
        zDataSetName = None
        if self.plotType_radioButton_2.isChecked():
            zDataSetName = str(self.z_comboBox.currentText())
        plotPosition = len(self.evolSubplotList)+1
        subplot = RawDataEvolutionSubplot(plotPosition, self.colormapsCollection, self.particleTracker.GetTrackedParticlesDataToPlot(xDataSetName, yDataSetName, zDataSetName), self.particleTracker.GetTrackedSpeciesName())
        self.evolSubplotList.append(subplot)
        self.SetAutoEvolColumnsAndRows()
        wid = PlotFieldItem(subplot, self)
        wid2 = QtWidgets.QListWidgetItem()
        wid2.setSizeHint(QtCore.QSize(100, 40))
        self.subplots_listWidget.addItem(wid2)
        self.subplots_listWidget.setItemWidget(wid2, wid)

    def AddToInstantPlotButton_Clicked(self):
        xDataSetName = str(self.instX_comboBox.currentText())
        yDataSetName = str(self.instY_comboBox.currentText())
        if self.instPlotType_radioButton_2.isChecked():
            zDataSetName = str(self.instZ_comboBox.currentText())
        plotPosition = len(self.instantSubplotList)+1
        dataSets = {}
        xDataSet = self.particleTracker.GetInstantRawDataSet(xDataSetName)
        dataSets["x"] = RawDataSetToPlot(xDataSet)
        yDataSet = self.particleTracker.GetInstantRawDataSet(yDataSetName)
        dataSets["y"] = RawDataSetToPlot(yDataSet)
        pxDataSet = self.particleTracker.GetInstantRawDataSet("Px")
        dataSets["Px"] = RawDataSetToPlot(pxDataSet)
        pyDataSet = self.particleTracker.GetInstantRawDataSet("Py")
        dataSets["Py"] = RawDataSetToPlot(pyDataSet)
        if self.instPlotType_radioButton_2.isChecked():
            zDataSet = self.particleTracker.GetInstantRawDataSet(zDataSetName)
            dataSets["z"] = RawDataSetToPlot(zDataSet)
            pzDataSet = self.particleTracker.GetInstantRawDataSet("Pz")
            dataSets["Pz"] = RawDataSetToPlot(pzDataSet)
        weightDataSet = self.particleTracker.GetInstantRawDataSet("Charge")
        dataSets["weight"] = RawDataSetToPlot(weightDataSet)
        subplot = RawDataSubplot(plotPosition, self.colormapsCollection, dataSets)
        self.instantSubplotList.append(subplot)
        self.SetAutoInstantColumnsAndRows()
        wid = PlotFieldItem(subplot, self)
        wid2 = QtWidgets.QListWidgetItem()
        wid2.setSizeHint(QtCore.QSize(100, 40))
        self.instantSubplots_listWidget.addItem(wid2)
        self.instantSubplots_listWidget.setItemWidget(wid2, wid)
        self.SetInstantTimeSteps()

    def PlotPushButton_Clicked(self):
        self.MakeEvolPlots()

    def PlotInstantPushButton_Clicked(self):
        self.MakeInstantPlots()

    def SelectAllCheckBox_StatusChanged(self):
        if self.selectAll_checkBox.checkState():
            for row in np.arange(0, self.particleList_tableWidget.rowCount()):
                item = self.particleList_tableWidget.item(row, 0)
                item.setCheckState(QtCore.Qt.Checked)
        else:
            for row in np.arange(0, self.particleList_tableWidget.rowCount()):
                item = self.particleList_tableWidget.item(row, 0)
                item.setCheckState(QtCore.Qt.Unchecked)

    def SelectAllExportCheckBox_StatusChanged(self):
        if self.selectAllExport_checkBox.checkState():
            for row in np.arange(0, self.trackedParticlesList_tableWidget.rowCount()):
                item = self.trackedParticlesList_tableWidget.item(row, 0)
                item.setCheckState(QtCore.Qt.Checked)
        else:
            for row in np.arange(0, self.trackedParticlesList_tableWidget.rowCount()):
                item = self.trackedParticlesList_tableWidget.item(row, 0)
                item.setCheckState(QtCore.Qt.Unchecked)

    def BrowseExportPathButton_Clicked(self):
        self.OpenFolderDialog()

    def ExportDataButton_Clicked(self):
        particleIndices = self.GetIndicesOfParticlesToExport()
        self.particleTracker.ExportParticleData(particleIndices, str(self.exportPath_lineEdit.text()))

    """
    Rectangle Selector
    """
    def line_select_callback(self, eclick, erelease):
        'eclick and erelease are the press and release events'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        filter = {}
        xAxisVariable = str(self.xAxis_comboBox.currentText())
        yAxisVariable = str(self.yAxis_comboBox.currentText())
        filter[xAxisVariable] = (min(x1,x2), max(x1,x2))
        filter[yAxisVariable] = (min(y1,y2), max(y1,y2))
        self.FindParticles(self.selectorTimeStep_Slider.value(),str(self.speciesSelector_comboBox.currentText()),filter)

    """
    Other functions
    """
    def OpenFolderDialog(self):
        folderPath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Export data to:", str(self.exportPath_lineEdit.text())))
        if folderPath != "":
            self.exportPath_lineEdit.setText(folderPath)

    def FindParticles(self, timeStep, speciesName, filter):
        self.particleList = self.particleTracker.FindParticles(timeStep, speciesName, filter)
        self.CreateParticleTable()

    def CreateParticleTable(self):
        n = len(self.particleList)
        variableNames = self.particleList[0].GetNamesOfTimeStepQuantities()
        allParticlesData = list()
        tableData = {}
        for particle in self.particleList:
            allParticlesData.append(particle.GetCurrentTimeStepQuantities())
        for variableName in variableNames:
            varValues = np.zeros(n)
            for i in np.arange(0,n):
                varValues[i] = allParticlesData[i][variableName]
            tableData[variableName] = varValues
        self.particleList_tableWidget.setColumnCount(len(variableNames)+1)
        self.particleList_tableWidget.setRowCount(n)
        tableHeaders = variableNames
        tableHeaders.insert(0," ")
        for i in np.arange(0,n):
            newItem = QtWidgets.QTableWidgetItem()
            newItem.setCheckState(QtCore.Qt.Unchecked)
            self.particleList_tableWidget.setItem(i, 0, newItem)
        for n, key in enumerate(tableHeaders[1:]):
            for m, item in enumerate(tableData[key]):
                newItem = QtWidgets.QTableWidgetItem(str(item))
                self.particleList_tableWidget.setItem(m, n+1, newItem)
        self.particleList_tableWidget.resizeColumnsToContents()
        self.particleList_tableWidget.setHorizontalHeaderLabels(tableHeaders)

    def GetSelectedParticles(self):
        selectedParticles = list()
        for row in np.arange(0, self.particleList_tableWidget.rowCount()):
            item = self.particleList_tableWidget.item(row, 0)
            if item.checkState():
                selectedParticles.append(self.particleList[row])
        return selectedParticles

    def GetSelectedFilters(self):
        filters = {}
        for row in np.arange(0, self.advancedSelector_tableWidget.rowCount()):
            item = self.advancedSelector_tableWidget.item(row, 0)
            if item.checkState():
                name = self.advancedSelector_tableWidget.item(row, 1).text()
                minVal = float(self.advancedSelector_tableWidget.item(row, 2).text())
                maxVal = float(self.advancedSelector_tableWidget.item(row, 3).text())
                filters[name] = (minVal, maxVal)
        return filters

    def CreateTrackedParticlesTable(self):
        trackedParticles = self.particleTracker.GetTrackedParticles()
        n = len(trackedParticles)
        variableNames = trackedParticles[0].GetNamesOfTimeStepQuantities()
        allParticlesData = list()
        tableData = {}
        for particle in trackedParticles:
            allParticlesData.append(particle.GetCurrentTimeStepQuantities())
        for variableName in variableNames:
            varValues = np.zeros(n)
            for i in np.arange(0,n):
                varValues[i] = allParticlesData[i][variableName]
            tableData[variableName] = varValues
        self.trackedParticlesList_tableWidget.setColumnCount(len(variableNames)+1)
        self.trackedParticlesList_tableWidget.setRowCount(n)
        tableHeaders = variableNames
        tableHeaders.insert(0," ")
        for i in np.arange(0,n):
            newItem = QtWidgets.QTableWidgetItem()
            newItem.setCheckState(QtCore.Qt.Unchecked)
            self.trackedParticlesList_tableWidget.setItem(i, 0, newItem)
        for n, key in enumerate(tableHeaders[1:]):
            for m, item in enumerate(tableData[key]):
                newItem = QtWidgets.QTableWidgetItem(str(item))
                self.trackedParticlesList_tableWidget.setItem(m, n+1, newItem)
        self.trackedParticlesList_tableWidget.setHorizontalHeaderLabels(tableHeaders)
        self.trackedParticlesList_tableWidget.resizeColumnsToContents()

    def _CreateFineSelectionTable(self):
        tableData = self._GetMaximumsAndMinimumsOfQuantities()
        tableHeaders = ["Use", "Quantity", "Minimum", "Maximum"]
        n = len(tableData)
        m = len(tableHeaders)
        self.advancedSelector_tableWidget.setRowCount(n)
        self.advancedSelector_tableWidget.setColumnCount(m)
        for i in np.arange(0,n):
            newItem = QtWidgets.QTableWidgetItem()
            newItem.setCheckState(QtCore.Qt.Unchecked)
            self.advancedSelector_tableWidget.setItem(i, 0, newItem)
        for i in np.arange(n):
            for j in np.arange(m-1):
                newItem = QtWidgets.QTableWidgetItem(str(tableData[i][j]))
                self.advancedSelector_tableWidget.setItem(i, j+1, newItem)
        self.advancedSelector_tableWidget.setHorizontalHeaderLabels(tableHeaders)
        self.advancedSelector_tableWidget.resizeColumnsToContents()

    def _GetMaximumsAndMinimumsOfQuantities(self):
        speciesName = str(self.speciesSelector_comboBox.currentText())
        timeStep = self.selectorTimeStep_Slider.value()
        quantityNamesList = self.particleTracker.GetSpeciesRawDataSetNames(speciesName)
        maxMinList = []
        for quantity in quantityNamesList:
            dataSet = self.particleTracker.GetSpeciesDataSet(speciesName, quantity)
            data = dataSet.GetDataInOriginalUnits(timeStep)
            dataMin = min(data)
            dataMax = max(data)
            maxMinList.append([quantity, dataMin, dataMax])
        return maxMinList
            

    def GetIndicesOfParticlesToExport(self):
        selectedParticlesIndices = list()
        for row in np.arange(0, self.trackedParticlesList_tableWidget.rowCount()):
            item = self.trackedParticlesList_tableWidget.item(row, 0)
            if item.checkState():
                selectedParticlesIndices.append(row)
        return selectedParticlesIndices

    def MakeSelectorPlot(self):
        if self.speciesSelector_comboBox.currentText() not in ["Select Species", "No species available"]:
            self.CreateSelectorSubplotObject()
            sbpList = list()
            sbpList.append(self.selectorSubplot) # we need to create a list of only one subplot because the DataPlotter only accepts lists.
            self.dataPlotter.MakePlot(self.selectorFigure, sbpList, 1, 1, self.selectorTimeStep_Slider.value())
            ax = self.selectorFigure.axes[0]
            if sys.version_info[0] < 3:
                self.toggle_selector = RectangleSelector(ax, self.line_select_callback,
                                               drawtype='box', useblit=True,
                                               button=[1, 3],  # don't use middle button
                                               minspanx=5, minspany=5,
                                               spancoords='pixels')
            else:
                self.toggle_selector = RectangleSelector(ax, self.line_select_callback,
                                               drawtype='box', useblit=True,
                                               button=[1, 3],  # don't use middle button
                                               minspanx=5, minspany=5,
                                               spancoords='pixels',
                                               interactive = True)
            self.toggle_selector.set_active(False)
            self.selectorFigure.tight_layout()
            self.selectorCanvas.draw()
            self.SetTimeSteps()

    def SetTimeSteps(self):
        self.timeSteps = self.selectorSubplot.GetTimeSteps()
        minTime = min(self.timeSteps)
        maxTime = max(self.timeSteps)
        self.selectorTimeStep_Slider.setMinimum(minTime)
        self.selectorTimeStep_Slider.setMaximum(maxTime)

    def SetAutoEvolColumnsAndRows(self):
        if self.evolSubplotRows*self.evolSubplotColumns < len(self.evolSubplotList):
            if self.increaseEvolRowsColumnsCounter % 2 == 0:
                self.evolSubplotRows += 1
            else:
                self.evolSubplotColumns += 1
            self.increaseEvolRowsColumnsCounter += 1

    def SetAutoInstantColumnsAndRows(self):
        if self.instantSubplotRows*self.instantSubplotColumns < len(self.instantSubplotList):
            if self.increaseInstantRowsColumnsCounter % 2 == 0:
                self.instantSubplotRows += 1
            else:
                self.instantSubplotColumns += 1
            self.increaseInstantRowsColumnsCounter += 1

    def RemoveSubplot(self, item):
        index = self.evolSubplotList.index(item.subplot)
        self.evolSubplotList.remove(item.subplot)
        self.subplots_listWidget.takeItem(index)
        for subplot in self.evolSubplotList:
            if subplot.GetPosition() > index+1:
                subplot.SetPosition(subplot.GetPosition()-1)
        if len(self.evolSubplotList) > 0:
            if self.increaseEvolRowsColumnsCounter % 2 == 0:
                if len(self.evolSubplotList) <= self.evolSubplotRows*(self.evolSubplotColumns-1):
                    self.evolSubplotColumns -= 1
                    self.increaseEvolRowsColumnsCounter -= 1
            else:
                if len(self.evolSubplotList) <= (self.evolSubplotRows-1)*self.evolSubplotColumns:
                    self.evolSubplotRows -= 1
                    self.increaseEvolRowsColumnsCounter -= 1

    def MakeEvolPlots(self):
        self.dataPlotter.MakePlot(self.mainFigure, self.evolSubplotList, self.evolSubplotRows, self.evolSubplotColumns)
        self.mainCanvas.draw()

    def MakeInstantPlots(self):
        timeStep = self.instantTimeStep_Slider.value()
        self.dataPlotter.MakePlot(self.instantPlotsFigure, self.instantSubplotList, self.instantSubplotRows, self.instantSubplotColumns, timeStep)
        self.instantPlotsCanvas.draw()

    def SetInstantTimeSteps(self):
        i = 0
        for subplot in self.instantSubplotList:
            if i == 0:
                self.instantTimeSteps = subplot.GetTimeSteps()
            else :
                self.instantTimeSteps = np.intersect1d(self.instantTimeSteps, subplot.GetTimeSteps())
            i+=1
        minTime = min(self.instantTimeSteps)
        maxTime = max(self.instantTimeSteps)
        self.instantTimeStep_Slider.setMinimum(minTime)
        self.instantTimeStep_Slider.setMaximum(maxTime)
        
