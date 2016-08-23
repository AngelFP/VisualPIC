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
import numpy as np
from matplotlib.figure import Figure
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
        self.particleTracker = ParticleTracker(dataContainer)
        self.colormapsCollection = colormapsCollection
        self.dataPlotter = dataPlotter
        self.selectorSubplot = None
        self.CreateCanvasAndFigures()
        self.FillInitialUI();
        #self.CreateSelectorSubplotObject()
        self.RegisterUIEvents();
        #self.MakeSelectorPlot()

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
            speciesName = self.speciesSelector_comboBox.currentText()
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

    def FillInitialUI(self):
        comboBoxItems = self.particleTracker.GetSpeciesNames()
        comboBoxItems.insert(0, "Select Species")
        self.speciesSelector_comboBox.addItems(comboBoxItems)
        self.selectorTimeStep_Slider.setMaximum(self.particleTracker.GetTotalTimeSteps()-1)

    """
    UI Events
    """

    def SelectorTimeStepSlider_ValueChanged(self):
        self.selectorTimeStep_lineEdit.setText(str(self.selectorTimeStep_Slider.value()))

    def SelectorTimeStepSlider_Released(self):
        self.MakeSelectorPlot()

    def SpeciesSelectorComboBox_IndexChanged(self):
        self.MakeSelectorPlot()

    """
    Other functions
    """

    def MakeSelectorPlot(self):
        if self.speciesSelector_comboBox.currentText() != "Select Species":
            self.CreateSelectorSubplotObject()
            sbpList = list()
            sbpList.append(self.selectorSubplot) # we need to create a list of only one subplot because the DataPlotter only accepts lists.
            self.dataPlotter.MakePlot(self.selectorFigure, sbpList, 1, 1, self.selectorTimeStep_Slider.value())
            self.selectorFigure.tight_layout()
            self.selectorCanvas.draw()
        
