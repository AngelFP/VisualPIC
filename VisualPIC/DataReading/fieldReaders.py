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


import abc
import sys
import h5py
import numpy as np

from VisualPIC.DataReading.dataReader import DataReader


class FieldReaderBase(DataReader):
    """Parent class for all FieldReaders"""
    __metaclass__  = abc.ABCMeta
    def __init__(self, location, speciesName, dataName):
        DataReader.__init__(self, location, speciesName, dataName)
        self.internalName = ""
        self.fieldDimension = ""
        self.axisUnits = {}
        self.axisExtent = ()
        self.ReadBasicData()
    
    def GetData(self, timeStep):
        if timeStep != self.currentTimeStep:
            self.currentTimeStep = timeStep
            self.OpenFileAndReadData()
        return self.data, self.axisExtent

    def GetDataUnits(self):
        if self.dataUnits == "":
            self.OpenFileAndReadUnits()
        return self.dataUnits, self.axisUnits

    @abc.abstractmethod
    def ReadBasicData(self):
        raise NotImplementedError

    @abc.abstractmethod
    def ReadInternalName(self):
        raise NotImplementedError

    @abc.abstractmethod
    def DetermineFieldDimension(self, file_content):
        raise NotImplementedError


class OsirisFieldReader(FieldReaderBase):
    def __init__(self, location, speciesName, dataName):
        FieldReaderBase.__init__(self, location, speciesName, dataName)

    def ReadBasicData(self):
        file_content = self.OpenFile(0)
        self.ReadInternalName(file_content)
        self.DetermineFieldDimension(file_content)
        file_content.close()
        
    def ReadInternalName(self, file_content):
        self.internalName = "/" + list(file_content.keys())[1]

    def DetermineFieldDimension(self, file_content):
        if '/AXIS/AXIS3' in file_content:
            self.fieldDimension = "3D"
        else:
            self.fieldDimension = "2D"

    def OpenFileAndReadData(self):
        file_content = self.OpenFile(self.currentTimeStep)
        self.data = np.array(file_content.get(self.internalName))
        self.axisExtent = file_content.attrs['XMIN'][0], file_content.attrs['XMAX'][0], file_content.attrs['XMIN'][1], file_content.attrs['XMAX'][1]
        file_content.close()

    def OpenFileAndReadUnits(self):
        file_content = self.OpenFile(0)
        if sys.version_info[0] < 3:
            self.axisUnits["x"] = str(list(file_content['/AXIS/AXIS1'].attrs["UNITS"])[0])
            self.axisUnits["y"] = str(list(file_content['/AXIS/AXIS2'].attrs["UNITS"])[0])
            self.dataUnits = str(list(file_content[self.internalName].attrs["UNITS"])[0])
        else:
            self.axisUnits["x"] = str(list(file_content['/AXIS/AXIS1'].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")
            self.axisUnits["y"] = str(list(file_content['/AXIS/AXIS2'].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")
            self.dataUnits = str(list(file_content[self.internalName].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")
        file_content.close()

    def OpenFile(self, timeStep):
        fileName = self.dataName + "-"
        if self.speciesName != "":
            fileName += self.speciesName + "-"
        fileName += str(timeStep).zfill(6)
        ending = ".h5"
        file_path = self.location + "/" + fileName + ending
        file_content = h5py.File(file_path, 'r')
        return file_content


class HiPACEFieldReader(FieldReaderBase):
    def __init__(self, location, speciesName, dataName):
        FieldReaderBase.__init__(self, location, speciesName, dataName)

    def ReadBasicData(self):
        raise NotImplementedError
        
    def ReadInternalName(self, file_content):
        raise NotImplementedError

    def DetermineFieldDimension(self, file_content):
        raise NotImplementedError

    def OpenFileAndReadData(self):
        raise NotImplementedError

    def OpenFileAndReadUnits(self):
        raise NotImplementedError