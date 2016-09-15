# -*- coding: utf-8 -*-

#Copyright 2016 ?ngel Ferran Pousa
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

from PyQt4.uic import loadUiType
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
import numpy as np
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)


from VisualPIC.DataHandling.dataContainer import DataContainer
from VisualPIC.DataHandling.rawDataSetToPlot import RawDataSetToPlot
from VisualPIC.DataHandling.subplot import *
from VisualPIC.DataPlotting.colorMapsCollection import ColorMapsCollection
from VisualPIC.DataPlotting.dataPlotter import DataPlotter
from VisualPIC.Controls.plotFieldItem import PlotFieldItem
from VisualPIC.Tools.particleTracking import ParticleTracker
import VisualPIC.DataHandling.unitConverters as unitConverters


if getattr(sys, 'frozen', False):
    # we are running in a bundle
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
guipath = os.path.join( bundle_dir, 'ParticleTracker.ui' )

Ui_ParticleTrackerWindow, QParticleTrackerWindow = loadUiType(guipath)

	
class ParticleTrackerWindow(QParticleTrackerWindow, Ui_ParticleTrackerWindow):
    def __init__(self, dataContainer, unitConverter, colormapsCollection, dataPlotter):
        super(ParticleTrackerWindow, self).__init__()
        self.setupUi(self)
        self.unitConverter = unitConverter
        self.particleTracker = ParticleTracker(dataContainer, unitConverter)
        self.colormapsCollection = colormapsCollection
        self.dataPlotter = dataPlotter
        self.selectorSubplot = None
        self.subplotList = list()
        self.subplotRows = 1
        self.subplotColumns = 1
        self.increaseRowsColumnsCounter = 0
        self.CreateCanvasAndFigures()
        self.FillInitialUI();
        self.RegisterUIEvents();

    def CreateCanvasAndFigures(self):
        self.mainFigure = Figure()
        self.mainFigure.patch.set_facecolor("white")
        self.mainCanvas = FigureCanvas(self.mainFigure)
        self.mainPlot_layout.addWidget(self.mainCanvas)
        self.mainCanvas.draw()
        self.toolbar = NavigationToolbar(self.mainCanvas, self.mainPlot_widget, coordinates=True)
        self.mainPlot_layout.addWidget(self.toolbar)
        self.selectorFigure = Figure()
        self.selectorFigure.patch.set_facecolor("white")
        self.selectorCanvas = FigureCanvas(self.selectorFigure)
        self.selectorPlot_layout.addWidget(self.selectorCanvas)
        self.selectorCanvas.draw()

    def CreateSelectorSubplotObject(self):
        if self.selectorSubplot == None or self.selectorSubplot.GetPlottedSpeciesName() != self.speciesSelector_comboBox.currentText():
            speciesName = str(self.speciesSelector_comboBox.currentText())
            dataSets = {}
            dataSets["x"] = RawDataSetToPlot(self.particleTracker.GetSpeciesDataSet(speciesName, "x1"), self.unitConverter)
            dataSets["y"] = RawDataSetToPlot(self.particleTracker.GetSpeciesDataSet(speciesName, "x2"), self.unitConverter)
            self.selectorSubplot = RawDataSubplot(1, self.colormapsCollection, dataSets)
            self.selectorSubplot.SetPlotType("Scatter")
            self.selectorSubplot.SetAxisProperty("x", "LabelFontSize", 10)
            self.selectorSubplot.SetAxisProperty("y", "LabelFontSize", 10)
            self.selectorSubplot.SetTitleProperty("FontSize", 0)

    def RegisterUIEvents(self):
        self.selectorTimeStep_Slider.valueChanged.connect(self.SelectorTimeStepSlider_ValueChanged)
        self.selectorTimeStep_Slider.sliderReleased.connect(self.SelectorTimeStepSlider_Released)
        self.speciesSelector_comboBox.currentIndexChanged.connect(self.SpeciesSelectorComboBox_IndexChanged)
        self.rectangleSelection_Button.clicked.connect(self.RectangleSelectionButton_Clicked)
        self.trackParticles_Button.clicked.connect(self.TrackParticlesButton_Clicked)
        self.plotType_radioButton_1.toggled.connect(self.PlotTypeRadioButton_Toggled)
        self.plotType_radioButton_2.toggled.connect(self.PlotTypeRadioButton_Toggled)
        self.addToPlot_Button.clicked.connect(self.AddToPlotButton_Clicked)
        self.plot_pushButton.clicked.connect(self.PlotPushButton_Clicked)
        self.selectAll_checkBox.toggled.connect(self.SelectAllCheckBox_StatusChanged)
        self.browseExportPath_pushButton.clicked.connect(self.BrowseExportPathButton_Clicked)
        self.selectAllExport_checkBox.toggled.connect(self.SelectAllExportCheckBox_StatusChanged)
        self.exportData_pushButton.clicked.connect(self.ExportDataButton_Clicked)

    def FillInitialUI(self):
        comboBoxItems = self.particleTracker.GetSpeciesNames()
        if len(comboBoxItems) > 0:
            comboBoxItems.insert(0, "Select Species")
        else:
            comboBoxItems.insert(0, "No species available")
        self.speciesSelector_comboBox.addItems(comboBoxItems)

    def FillPlotUI(self):
        self.x_comboBox.clear()
        self.y_comboBox.clear()
        self.z_comboBox.clear()
        self.x_comboBox.addItems(self.particleTracker.GetAvailableWholeSimulationQuantitiesInParticles())
        self.y_comboBox.addItems(self.particleTracker.GetAvailableWholeSimulationQuantitiesInParticles())
        self.z_comboBox.addItems(self.particleTracker.GetAvailableWholeSimulationQuantitiesInParticles())
        self.trackedParticles_Label.setText("Tracking " + str(self.particleTracker.GetTotalNumberOfTrackedParticles())+ " particle(s)")

    def FillExportDataUI(self):
        self.CreateTrackedParticlesTable()
        self.exportPath_lineEdit.setText(self.particleTracker.GetDataLocation())

    """
    UI Events
    """
    def SelectorTimeStepSlider_ValueChanged(self):
        self.selectorTimeStep_lineEdit.setText(str(self.selectorTimeStep_Slider.value()))

    def SelectorTimeStepSlider_Released(self):
        if self.selectorTimeStep_Slider.value() in self.timeSteps:
            self.MakeSelectorPlot()
        else:
            val = self.selectorTimeStep_Slider.value()
            closestHigher = self.timeSteps[np.where(self.timeSteps > val)[0][0]]
            closestLower = self.timeSteps[np.where(self.timeSteps < val)[0][-1]]
            if abs(val-closestHigher) < abs(val-closestLower):
                self.selectorTimeStep_Slider.setValue(closestHigher)
            else:
                self.selectorTimeStep_Slider.setValue(closestLower)
        self.MakeSelectorPlot()

    def SpeciesSelectorComboBox_IndexChanged(self):
        self.MakeSelectorPlot()

    def RectangleSelectionButton_Clicked(self):
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
        ax.callbacks.connect('key_press_event', self.toggle_selector_event)

    def TrackParticlesButton_Clicked(self):
        self.particleTracker.SetParticlesToTrack(self.GetSelectedParticles())
        self.particleTracker.FillEvolutionOfAllDataSetsInParticles()
        self.FillPlotUI()
        self.FillExportDataUI()

    def PlotTypeRadioButton_Toggled(self):
        self.z_comboBox.setEnabled(self.plotType_radioButton_2.isChecked())

    def AddToPlotButton_Clicked(self):
        xDataSetName = str(self.x_comboBox.currentText())
        yDataSetName = str(self.y_comboBox.currentText())
        zDataSetName = None
        if self.plotType_radioButton_2.isChecked():
            zDataSetName = str(self.z_comboBox.currentText())
        plotPosition = len(self.subplotList)+1
        subplot = RawDataEvolutionSubplot(plotPosition, self.colormapsCollection, self.particleTracker.GetTrackedParticlesDataToPlot(xDataSetName, yDataSetName, zDataSetName), self.particleTracker.GetTrackedSpeciesName())
        self.subplotList.append(subplot)
        self.SetAutoColumnsAndRows()
        wid = PlotFieldItem(subplot, self)
        wid2 = QtGui.QListWidgetItem()
        wid2.setSizeHint(QtCore.QSize(100, 40))
        self.subplots_listWidget.addItem(wid2)
        self.subplots_listWidget.setItemWidget(wid2, wid)

    def PlotPushButton_Clicked(self):
        self.MakePlots()

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
        filter["x1"] = (min(x1,x2), max(x1,x2))
        filter["x2"] = (min(y1,y2), max(y1,y2))
        self.FindParticles(self.selectorTimeStep_Slider.value(),str(self.speciesSelector_comboBox.currentText()),filter)

    def toggle_selector_event(self, event):
        print(' Key pressed.')
        if event.key in ['Q', 'q'] and self.toggle_selector.active:
            print(' RectangleSelector deactivated.')
            self.toggle_selector.set_active(False)
        if event.key in ['A', 'a'] and not self.toggle_selector.active:
            print(' RectangleSelector activated.')
            self.toggle_selector.set_active(True)

    """
    Other functions
    """

    def OpenFolderDialog(self):
        folderPath = str(QtGui.QFileDialog.getExistingDirectory(self, "Export data to:", str(self.exportPath_lineEdit.text())))
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
            newItem = QTableWidgetItem()
            newItem.setCheckState(QtCore.Qt.Unchecked)
            self.particleList_tableWidget.setItem(i, 0, newItem)
        for n, key in enumerate(tableHeaders[1:]):
            for m, item in enumerate(tableData[key]):
                newItem = QTableWidgetItem(str(item))
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
            newItem = QTableWidgetItem()
            newItem.setCheckState(QtCore.Qt.Unchecked)
            self.trackedParticlesList_tableWidget.setItem(i, 0, newItem)
        for n, key in enumerate(tableHeaders[1:]):
            for m, item in enumerate(tableData[key]):
                newItem = QTableWidgetItem(str(item))
                self.trackedParticlesList_tableWidget.setItem(m, n+1, newItem)
        self.trackedParticlesList_tableWidget.resizeColumnsToContents()
        self.trackedParticlesList_tableWidget.setHorizontalHeaderLabels(tableHeaders)

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
            self.selectorFigure.tight_layout()
            self.selectorCanvas.draw()
            self.SetTimeSteps()

    def SetTimeSteps(self):
        self.timeSteps = self.selectorSubplot.GetTimeSteps()
        minTime = min(self.timeSteps)
        maxTime = max(self.timeSteps)
        self.selectorTimeStep_Slider.setMinimum(minTime)
        self.selectorTimeStep_Slider.setMaximum(maxTime)

    def SetAutoColumnsAndRows(self):
        if self.subplotRows*self.subplotColumns < len(self.subplotList):
            if self.increaseRowsColumnsCounter % 2 == 0:
                self.subplotRows += 1
            else:
                self.subplotColumns += 1
            self.increaseRowsColumnsCounter += 1

    def RemoveSubplot(self, item):
        index = self.subplotList.index(item.subplot)
        self.subplotList.remove(item.subplot)
        self.subplots_listWidget.takeItem(index)
        for subplot in self.subplotList:
            if subplot.GetPosition() > index+1:
                subplot.SetPosition(subplot.GetPosition()-1)
        if len(self.subplotList) > 0:
            if self.increaseRowsColumnsCounter % 2 == 0:
                if len(self.subplotList) <= self.subplotRows*(self.subplotColumns-1):
                    self.subplotColumns -= 1
                    self.increaseRowsColumnsCounter -= 1
            else:
                if len(self.subplotList) <= (self.subplotRows-1)*self.subplotColumns:
                    self.subplotRows -= 1
                    self.increaseRowsColumnsCounter -= 1

    def MakePlots(self):
        self.dataPlotter.MakePlot(self.mainFigure, self.subplotList, self.subplotRows, self.subplotColumns)
        self.mainCanvas.draw()
        
