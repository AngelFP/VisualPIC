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
from scipy import interpolate as ip


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
    def Get1DSliceInOriginalUnits(self, timeStep, slicePositionX, slicePositionY = None):
        return self.dataReader.Get1DSlice(timeStep, slicePositionX, slicePositionY)

    def Get2DSliceInOriginalUnits(self, sliceAxis, slicePosition, timeStep):
        return self.dataReader.Get2DSlice(sliceAxis, slicePosition, timeStep)

    def GetAllFieldDataInOriginalUnits(self, timeStep):
        return  self.dataReader.GetAllFieldData(timeStep)

    def Get3DFieldFrom2DSliceInOriginalUnits(self, timeStep, transvEl, longEl, fraction):
        """
            fraction: used to define the range of data we want to visualize in the transverse direction.
                - fraction = 1 -> get all the data
                - fraction = 0.5 -> get only from x=0 to x=x_max/2
        """
        field2D = self.GetAllFieldDataInOriginalUnits(timeStep)
        nx = field2D.shape[0]
        field2D = field2D[int(nx/2):int(nx/2+nx/2*fraction)] # we get only half
        cilShape = field2D.shape
        Rin,Zin = np.mgrid[0:cilShape[0], 0:cilShape[1]] # cyl. coordinates of original data
        Zin = np.reshape(Zin, Zin.shape[0]*Zin.shape[1])
        Rin = np.reshape(Rin, Rin.shape[0]*Rin.shape[1])
        field2D = np.reshape(field2D, field2D.shape[0]*field2D.shape[1])
        transvSpacing = cilShape[0]*2/transvEl
        lonSpacing = cilShape[1]/longEl
        field3D = np.zeros((transvEl, transvEl, longEl))
        X, Y, Z = np.mgrid[0:cilShape[0]:transvSpacing,0:cilShape[0]:transvSpacing,0:cilShape[1]:lonSpacing] # cart. coordinates of 3D field
        Rout = np.sqrt(X**2 + Y**2)
        # Fill the field sector by sector (only the first has to be calculated. The rest are simlpy mirrored)
        field3D[int(transvEl/2):transvEl+1,int(transvEl/2):transvEl+1] = ip.griddata(np.column_stack((Rin,Zin)), field2D, (Rout, Z), method='nearest', fill_value = 0) # top right section when looking back from z to the x-y plane.
        field3D[0:int(transvEl/2),int(transvEl/2):transvEl+1] = np.flip(field3D[int(transvEl/2):transvEl+1,int(transvEl/2):transvEl+1], 0)
        field3D[0:int(transvEl/2),0:int(transvEl/2)] = np.flip(field3D[0:int(transvEl/2),int(transvEl/2):transvEl+1], 1)
        field3D[int(transvEl/2):transvEl+1,0:int(transvEl/2)] = np.flip(field3D[int(transvEl/2):transvEl+1,int(transvEl/2):transvEl+1], 1)
        return field3D
    
    """
    Get data in any units
    """
    def Get1DSlice(self, timeStep, units, slicePositionX, slicePositionY = None):
        sliceData = self.dataReader.Get1DSlice(timeStep, slicePositionX, slicePositionY)
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
    def Get1DSliceISUnits(self, timeStep, slicePositionX, slicePositionY = None):
        sliceData = self.dataReader.Get1DSlice(timeStep, slicePositionX, slicePositionY)
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