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

from PyQt4.uic import loadUiType
from PyQt4 import QtCore, QtGui
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from VisualPIC.Views.createAnimationWindow import CreateAnimationWindow
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
guipath = os.path.join( bundle_dir, 'ParticleTracker.ui' )

Ui_ParticleTracker, QParticleTracker = loadUiType(guipath)

	
class ParticleTracker(QParticleTracker, Ui_ParticleTracker):
    def __init__(self, dataContainer):
        super(ParticleTracker, self).__init__()
        self.setupUi(self)
        self.dataContainer = dataContainer