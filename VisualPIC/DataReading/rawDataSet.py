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

import sys
import h5py

from VisualPIC.DataReading.dataReaderSelectors import RawDataReaderSelector


class RawDataSet:
    
    def __init__(self, simulationCode, name, location, totalTimeSteps, speciesName, internalName):
        self.name = name
        self.location = location
        self.speciesName = speciesName
        self.totalTimeSteps = totalTimeSteps
        self.dataReader = RawDataReaderSelector.GetReader(simulationCode, location, speciesName, name, internalName)
 
    def GetNormalizedUnits(self):
        return self.dataUnits
        
    def GetRawData(self):
        return self.rawData
        
    def GetUnits(self):
        return self.dataUnits
        
    def GetPlotData(self, timeStep):
        self.LoadData(timeStep)
        return self.GetRawData(), self.GetUnits()
        
    def GetName(self):
        return self.name
        
    def GetTotalTimeSteps(self):
        return self.totalTimeSteps
        
    def GetSpeciesName(self):
        return self.speciesName
        