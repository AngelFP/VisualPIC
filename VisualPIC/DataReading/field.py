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

class Field:
    
    def __init__(self, simulationCode, name, location, totalTimeSteps, speciesName=""):
        self.name = name
        self.location = location
        self.speciesName = speciesName
        self.totalTimeSteps = totalTimeSteps
        self.simulationCode = simulationCode
        self.dataReader = RawDataReaderSelector.GetReader(simulationCode, location, speciesName, name)
          
    def GetFieldDimension(self):
        return self.fieldDimension
        
    def GetExtent(self):
        axisExtent = [self.xMin[0],self.xMax[0], self.xMin[1],self.xMax[1]]
        return axisExtent
        
    def GetFieldValues(self):
        return self.fieldData
        
    def GetUnits(self):
        return self.x1Units, self.x2Units, self.fieldUnits
        
    def GetPlotData(self, timeStep):
        self.LoadData(timeStep)
        return self.GetFieldValues(), self.GetExtent(), self.GetUnits()
        
    def GetName(self):
        return self.name
        
    def GetTotalTimeSteps(self):
        return self.totalTimeSteps
        
    def GetSpeciesName(self):
        return self.speciesName
        
    def GetNormalizedUnits(self, ofWhat):
        if ofWhat == "x":
            return self.x1Units
        if ofWhat == "y":
            return self.x2Units
        if ofWhat == "Field":
            return self.fieldUnits
        
        