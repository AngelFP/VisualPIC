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

from VisualPIC.DataReading.dataReader import DataReader
from VisualPIC.DataHandling.dataElement import DataElement
from VisualPIC.DataReading.dataReaderSelectors import *

class FolderDataElement(DataElement):
    """Base class for all data elements (fields and rawDataSets)"""
    def __init__(self, simulationCode, nameInCode, standardName, location, timeSteps, speciesName = "", internalName = ""):
        DataElement.__init__(self, standardName, timeSteps, speciesName)
        self.dataNameInCode = nameInCode # name of the variable in the simulation code (e.g. "e1-savg" for the averaged longitudinal E field in Osiris)
        self.dataLocation = location
        self.dataReader = None # Each subclass will load its own

    def GetNameInCode(self):
        return self.dataNameInCode

    def GetData(self, timeStep):
        return self.dataReader.GetData(timeStep)
        
    def GetDataUnits(self):
        return self.dataReader.GetDataUnits()

    def GetTime(self, timeStep):
        return self.dataReader.GetTime(timeStep)
        
    def GetTimeUnits(self):
        return self.dataReader.GetTimeUnits()

class FolderField(FolderDataElement):
    def __init__(self, simulationCode, nameInCode, standardName, location, timeSteps, speciesName=""):
        FolderDataElement.__init__(self, simulationCode, nameInCode, standardName, location, timeSteps, speciesName)
        self.dataReader = FieldReaderSelector.GetReader(simulationCode, location, speciesName, nameInCode, timeSteps[0])
          
    def GetFieldDimension(self):
        return self.dataReader.fieldDimension

    def GetAxisData(self, timeStep):
        return self.dataReader.GetAxisData(timeStep) #dictionary
        
    def GetAxisUnits(self):
        return self.dataReader.GetAxisUnits()

class FolderRawDataSet(FolderDataElement):
    def __init__(self, simulationCode, nameInCode, standardName, location, timeSteps, speciesName, internalName):
        FolderDataElement.__init__(self, simulationCode, nameInCode, standardName, location, timeSteps, speciesName, internalName)
        self.dataReader = RawDataReaderSelector.GetReader(simulationCode, location, speciesName, nameInCode, internalName)