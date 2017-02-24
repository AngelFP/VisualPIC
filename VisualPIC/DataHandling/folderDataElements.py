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


from VisualPIC.DataHandling.dataElement import DataElement
from VisualPIC.DataReading.dataReaderSelectors import *


class FolderDataElement(DataElement):
    """Base class for all data elements (fields and rawDataSets)"""
    def __init__(self, simulationCode, nameInCode, standardName, location, timeSteps, speciesName = "", internalName = "", hasNonISUnits = True):
        DataElement.__init__(self, standardName, timeSteps, speciesName, hasNonISUnits)
        self.dataNameInCode = nameInCode # name of the variable in the simulation code (e.g. "e1-savg" for the averaged longitudinal E field in Osiris)
        self.dataLocation = location
        self.dataReader = None # Each subclass will load its own

    def GetNameInCode(self):
        return self.dataNameInCode
        
    def GetDataOriginalUnits(self):
        return self.dataReader.GetDataUnits()

    def GetTimeInOriginalUnits(self, timeStep):
        return self.dataReader.GetTime(timeStep)
        
    def GetTimeOriginalUnits(self):
        return self.dataReader.GetTimeUnits()


class FolderField(FolderDataElement):
    def __init__(self, simulationCode, nameInCode, standardName, location, timeSteps, speciesName="", hasNonISUnits = True):
        FolderDataElement.__init__(self, simulationCode, nameInCode, standardName, location, timeSteps, speciesName, hasNonISUnits = hasNonISUnits)
        self.dataReader = FieldReaderSelector.GetReader(simulationCode, location, speciesName, nameInCode, timeSteps[0])
          
    def GetFieldDimension(self):
        return self.dataReader.fieldDimension

    def GetPossibleAxisUnits(self):
        return self._unitConverter.GetPossibleAxisUnits(self)

    def GetAxisDataInOriginalUnits(self, axis, timeStep):
        return self.dataReader.GetAxisData(timeStep)[axis] #dictionary
        
    def GetAxisOriginalUnits(self):
        return self.dataReader.GetAxisUnits()

    """
    Get data in original units
    """
    def Get1DSliceInOriginalUnits(self, slicePosition, timeStep):
        return self.dataReader.Get1DSlice(slicePosition, timeStep)

    def Get2DSliceInOriginalUnits(self, sliceAxis, slicePosition, timeStep):
        return self.dataReader.Get2DSlice(sliceAxis, slicePosition, timeStep)

    def GetAllFieldDataInOriginalUnits(self, timeStep):
        return  self.dataReader.GetAllFieldData(timeStep)
    
    """
    Get data in any units
    """
    def Get1DSlice(self, slicePosition, timeStep, units):
        sliceData = self.dataReader.Get1DSlice(slicePosition, timeStep)
        originalDataUnits = self.dataReader.GetDataUnits()
        return self._unitConverter.GetDataInUnits(self, units, sliceData)

    def Get2DSlice(self, sliceAxis, slicePosition, timeStep, units):
        sliceData = self.dataReader.Get2DSlice(sliceAxis, slicePosition, timeStep)
        originalDataUnits = self.dataReader.GetDataUnits()
        return self._unitConverter.GetDataInUnits(self, units, sliceData)

    def GetAllFieldData(self, timeStep, units):
        fieldData = self.dataReader.GetAllFieldData(timeStep)
        originalDataUnits = self.dataReader.GetDataUnits()
        return self._unitConverter.GetDataInUnits(self, units, fieldData)

    """
    Get data in IS units
    """
    def Get1DSliceISUnits(self, slicePosition, timeStep):
        sliceData = self.dataReader.Get1DSlice(slicePosition, timeStep)
        originalDataUnits = self.dataReader.GetDataUnits()
        return self._unitConverter.GetDataInISUnits(self, sliceData)

    def Get2DSliceISUnits(self, sliceAxis, slicePosition, timeStep):
        sliceData = self.dataReader.Get2DSlice(sliceAxis, slicePosition, timeStep)
        originalDataUnits = self.dataReader.GetDataUnits()
        return self._unitConverter.GetDataInISUnits(self, sliceData)

    def GetAllFieldDataISUnits(self, timeStep):
        fieldData = self.dataReader.GetAllFieldData(timeStep)
        originalDataUnits = self.dataReader.GetDataUnits()
        return self._unitConverter.GetDataInISUnits(self, fieldData)


class FolderRawDataSet(FolderDataElement):
    def __init__(self, simulationCode, nameInCode, standardName, location, timeSteps, speciesName, internalName, hasNonISUnits = True):
        FolderDataElement.__init__(self, simulationCode, nameInCode, standardName, location, timeSteps, speciesName, internalName, hasNonISUnits)
        self.dataReader = RawDataReaderSelector.GetReader(simulationCode, location, speciesName, nameInCode, internalName, timeSteps[0])

    """
    Get data in original units
    """
    def GetDataInOriginalUnits(self, timeStep):
        return self.dataReader.GetData(timeStep)

    """
    Get data in any units
    """
    def GetDataInUnits(self, units, timeStep):
        return self._unitConverter.GetDataInUnits(self, units, self.dataReader.GetData(timeStep))

    """
    Get data in IS units
    """
    def GetDataInISUnits(self, timeStep):
        return self._unitConverter.GetDataInISUnits(self, self.dataReader.GetData(timeStep))