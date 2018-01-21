# -*- coding: utf-8 -*-

#Copyright 2016-2017 Angel Ferran Pousa, DESY
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


import abc
from h5py import File as H5File
import numpy as np

from VisualPIC.DataReading.dataReader import DataReader


class FieldReaderBase(DataReader):
    """Parent class for all FieldReaders"""
    __metaclass__  = abc.ABCMeta
    def __init__(self, location, speciesName, dataName, firstTimeStep):
        DataReader.__init__(self, location, speciesName, dataName)
        self.internalName = ""
        self.fieldDimension = ""
        self.firstTimeStep = firstTimeStep
        self.matrixShape = []
        self.axisUnits = {}
        self.axisData = {}
        self.currentTimeStep = {"Slice-1D":-1, "Slice-2D":-1, "AllData":-1}
        self.data = {"Slice-1D":[], "Slice-2D":[], "AllData":[]}
        self.currentSliceAxis = {"Slice-1D":-1, "Slice-2D":-1}
        self.currentSlicePosition = {"Slice-1D":-1, "Slice-2D":-1}
        self._ReadBasicData()

    def Get1DSlice(self, timeStep, slicePositionX, slicePositionY = None):
        if (timeStep != self.currentTimeStep["Slice-1D"]) or ((slicePositionX, slicePositionY) != self.currentSlicePosition["Slice-1D"]):
            self.currentTimeStep["Slice-1D"] = timeStep
            self.currentSlicePosition["Slice-1D"] = (slicePositionX, slicePositionY)
            self.data["Slice-1D"] = self._Read1DSlice(timeStep, slicePositionX, slicePositionY)
        return self.data["Slice-1D"]

    def Get2DSlice(self, sliceAxis, slicePosition, timeStep):
        if (timeStep != self.currentTimeStep["Slice-2D"]) or (slicePosition != self.currentSlicePosition["Slice-2D"]) or (sliceAxis != self.currentSliceAxis["Slice-2D"]):
            self.currentTimeStep["Slice-2D"] = timeStep
            self.currentSlicePosition["Slice-2D"] = slicePosition
            self.currentSliceAxis["Slice-2D"] = sliceAxis
            self.data["Slice-2D"] = self._Read2DSlice(sliceAxis, slicePosition, timeStep)
        return self.data["Slice-2D"]

    def GetAllFieldData(self, timeStep):
        if timeStep != self.currentTimeStep["AllData"]:
            self.currentTimeStep["AllData"] = timeStep
            self.data["AllData"] = self._ReadAllFieldData(timeStep)
        return self.data["AllData"]

    def GetTime(self, timeStep):
        self._ReadTime(timeStep)
        return self.currentTime

    def GetTimeUnits(self):
        if self.timeUnits == "":
            self._ReadUnits()
        return self.timeUnits

    def GetDataUnits(self):
        if self.dataUnits == "":
            self._ReadUnits()
        return self.dataUnits

    def GetAxisData(self, timeStep):
        self.axisData = self._ReadAxisData(timeStep)
        return self.axisData

    def GetAxisUnits(self):
        if self.dataUnits == "":
            self._ReadUnits()
        return self.axisUnits

    @abc.abstractmethod
    def _ReadBasicData(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _GetMatrixShape(self, file_content):
        raise NotImplementedError

    @abc.abstractmethod
    def _ReadInternalName(self, file_content):
        raise NotImplementedError

    @abc.abstractmethod
    def _DetermineFieldDimension(self, file_content):
        raise NotImplementedError

    @abc.abstractmethod
    def _Read1DSlice(self, timeStep, slicePositionX, slicePositionY = None):
        raise NotImplementedError

    @abc.abstractmethod
    def _Read2DSlice(self, sliceAxis, slicePosition, timeStep):
        raise NotImplementedError

    @abc.abstractmethod
    def _ReadAllFieldData(self, timeStep):
        raise NotImplementedError

    @abc.abstractmethod
    def _ReadAxisData(self, timeStep):
        raise NotImplementedError

    @abc.abstractmethod
    def _ReadTime(self, timeStep):
        raise NotImplementedError


class OsirisFieldReader(FieldReaderBase):
    def __init__(self, location, speciesName, dataName, firstTimeStep):
        FieldReaderBase.__init__(self, location, speciesName, dataName, firstTimeStep)

    def _ReadBasicData(self):
        file_content = self._OpenFile(self.firstTimeStep)
        self._ReadInternalName(file_content)
        self._DetermineFieldDimension(file_content)
        self._GetMatrixShape(file_content)
        self._ReadSimulationProperties(file_content)
        file_content.close()

    def _GetMatrixShape(self, file_content):
        self.matrixShape = file_content.get(self.internalName).shape
        
    def _ReadInternalName(self, file_content):
        self.internalName = list(file_content.keys())[1]

    def _DetermineFieldDimension(self, file_content):
        if '/AXIS/AXIS3' in file_content:
            self.fieldDimension = "3D"
        else:
            self.fieldDimension = "2D"

    def _Read1DSlice(self, timeStep, slicePositionX, slicePositionY = None):
        # TODO: add support for 3D fields
        file_content = self._OpenFile(timeStep)
        fieldData = file_content[self.internalName]
        if self.fieldDimension == '2D':
            elementsX = self.matrixShape[-2]
            selectedRow = round(elementsX*(float(slicePositionX)/100))
            sliceData = np.array(fieldData[selectedRow])
        elif self.fieldDimension == '3D':
            elementsX = self.matrixShape[-3]
            elementsY = self.matrixShape[-2]
            selectedX = round(elementsX*(float(slicePositionX)/100))
            selectedY = round(elementsY*(float(slicePositionY)/100))
            sliceData = np.array(fieldData[selectedX, selectedY])
        file_content.close()
        return sliceData

    def _Read2DSlice(self, sliceAxis, slicePosition, timeStep):
        file_content = self._OpenFile(timeStep)
        fieldData = file_content[self.internalName]
        elementsX3 = self.matrixShape[-3] # number of elements in the transverse direction
        selectedRow = round(elementsX3*(float(slicePosition)/100))
        sliceData = np.array(fieldData[selectedRow])
        file_content.close()
        return sliceData

    def _ReadAllFieldData(self, timeStep):
        file_content = self._OpenFile(timeStep)
        fieldData = np.array(file_content[self.internalName])
        file_content.close()
        return fieldData

    def _ReadAxisData(self, timeStep):
        file_content = self._OpenFile(timeStep)
        elementsX = self.matrixShape[-1] # number of elements in the longitudinal z direction
        elementsY = self.matrixShape[-2] # number of elements in the transverse y direction
        axisData = {}
        axisData["x"] = np.linspace(file_content.attrs['XMIN'][0], file_content.attrs['XMAX'][0], elementsX)
        axisData["y"] = np.linspace(file_content.attrs['XMIN'][1], file_content.attrs['XMAX'][1], elementsY)
        if self.fieldDimension == "3D":
            elementsZ = self.matrixShape[-3] # number of elements in the transverse x direction
            axisData["z"] = np.linspace(file_content.attrs['XMIN'][2], file_content.attrs['XMAX'][2], elementsZ)
        file_content.close()
        return axisData

    def _ReadTime(self, timeStep):
        file_content = self._OpenFile(timeStep)
        self.currentTime = file_content.attrs["TIME"][0]
        file_content.close()

    def _ReadUnits(self):
        file_content = self._OpenFile(self.firstTimeStep)
        self.axisUnits["x"] = str(list(file_content['/AXIS/AXIS1'].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")
        self.axisUnits["y"] = str(list(file_content['/AXIS/AXIS2'].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")
        self.dataUnits = str(list(file_content[self.internalName].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")
        self.timeUnits = str(file_content.attrs["TIME UNITS"][0])[2:-1].replace("\\\\","\\")
        file_content.close()

    def _ReadSimulationProperties(self, file_content):
        self.grid_resolution = np.array(file_content.attrs['NX'])
        self.grid_size = np.array(file_content.attrs['XMAX']) - np.array(file_content.attrs['XMIN'])
        self.grid_units = str(list(file_content['/AXIS/AXIS1'].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")

    def _OpenFile(self, timeStep):
        fileName = self.dataName + "-"
        if self.speciesName != "":
            fileName += self.speciesName + "-"
        fileName += str(timeStep).zfill(6)
        ending = ".h5"
        file_path = self.location + "/" + fileName + ending
        file_content = H5File(file_path, 'r')
        return file_content


class HiPACEFieldReader(FieldReaderBase):
    def __init__(self, location, speciesName, dataName, firstTimeStep):
        FieldReaderBase.__init__(self, location, speciesName, dataName, firstTimeStep)

    def _ReadBasicData(self):
        file_content = self._OpenFile(self.firstTimeStep)
        self._ReadInternalName(file_content)
        self._DetermineFieldDimension(file_content)
        self._GetMatrixShape(file_content)
        self._ReadSimulationProperties(file_content)
        file_content.close()

    def _GetMatrixShape(self, file_content):
        self.matrixShape = file_content.get(self.internalName).shape
        
    def _ReadInternalName(self, file_content):
        self.internalName = list(file_content.keys())[0]

    def _DetermineFieldDimension(self, file_content):
        self.fieldDimension = "3D"

    def _Read1DSlice(self, timeStep, slicePositionX, slicePositionY = None):
        # TODO: add support for 3D fields
        file_content = self._OpenFile(timeStep)
        fieldData = file_content[self.internalName]
        if self.fieldDimension == '2D':
            elementsX = self.matrixShape[-2]
            selectedRow = round(elementsX*(float(slicePositionX)/100))
            sliceData = np.array(fieldData[selectedRow])
        elif self.fieldDimension == '3D':
            elementsX = self.matrixShape[-3]
            elementsY = self.matrixShape[-2]
            selectedX = round(elementsX*(float(slicePositionX)/100))
            selectedY = round(elementsY*(float(slicePositionY)/100))
            sliceData = np.array(fieldData[selectedX, selectedY])
        file_content.close()
        return sliceData

    def _Read2DSlice(self, sliceAxis, slicePosition, timeStep):
        file_content = self._OpenFile(timeStep)
        fieldData = file_content[self.internalName]
        elementsX3 = self.matrixShape[2] # number of elements in the transverse direction
        selectedRow = round(elementsX3*(float(slicePosition)/100))
        sliceData = np.array(fieldData[:,:,selectedRow]).T
        file_content.close()
        return sliceData

    def _ReadAllFieldData(self, timeStep):
        file_content = self._OpenFile(timeStep)
        fieldData = np.array(file_content[self.internalName])
        file_content.close()
        return fieldData

    def _ReadAxisData(self, timeStep):
        file_content = self._OpenFile(timeStep)
        elementsX = self.matrixShape[-1] # number of elements in the longitudinal z direction
        elementsY = self.matrixShape[-2] # number of elements in the transverse y direction
        axisData = {}
        axisData["x"] = np.linspace(file_content.attrs['XMIN'][0], file_content.attrs['XMAX'][0], elementsX)
        axisData["y"] = np.linspace(file_content.attrs['XMIN'][1], file_content.attrs['XMAX'][1], elementsY)
        if self.fieldDimension == "3D":
            elementsZ = self.matrixShape[-3] # number of elements in the transverse x direction
            axisData["z"] = np.linspace(file_content.attrs['XMIN'][2], file_content.attrs['XMAX'][2], elementsZ)
        file_content.close()
        return axisData

    def _ReadTime(self, timeStep):
        file_content = self._OpenFile(timeStep)
        self.currentTime = file_content.attrs["TIME"][0]
        file_content.close()

    def _ReadUnits(self):
        # No units information is currently stored by HiPACE
        if self.speciesName != "":
            self.dataUnits = 'e \omega_p^3/ c^3'
        elif self.dataName == 'Ez':
            self.dataUnits = 'm_e c \omega_p e^{-1}'
        else:
            self.dataUnits = 'unknown'
        self.timeUnits = '1/ \omega_p'
        self.axisUnits["x"] = 'c/ \omega_p'
        self.axisUnits["y"] = 'c/ \omega_p'
        self.axisUnits["z"] = 'c/ \omega_p'

    def _ReadSimulationProperties(self, file_content):
        self.grid_resolution = np.array(file_content.attrs['NX'])
        self.grid_size = np.array(file_content.attrs['XMAX']) - np.array(file_content.attrs['XMIN'])
        self.grid_units = str(list(file_content['/AXIS/AXIS1'].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")

    def _OpenFile(self, timeStep):
        if self.speciesName != "":
            fileName = 'density_' + self.speciesName + '_' + self.dataName
        else:
            fileName = 'field_' + self.dataName
            
        fileName += '_' + str(timeStep).zfill(6)
        ending = ".h5"
        file_path = self.location + "/" + fileName + ending
        file_content = H5File(file_path, 'r')
        return file_content