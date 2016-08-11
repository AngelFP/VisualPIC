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


import abc
import sys
import h5py

from VisualPIC.DataReading.dataReader import DataReader


class FieldReaderBase(DataReader):
    """Parent class for all FieldReaders"""
    __metaclass__  = abc.ABCMeta
    def __init__(self, location, speciesName, dataName):
        DataReader.__init__(self, location, speciesName, dataName)
        self.__fieldDimension = ""
        self.__axisUnits = {}
        self.__ReadBasicData()
    
    def GetAxisUnits(self):
        if self.__axisUnits == {}:
            self.__OpenFileAndReadUnits()
        return self.__axisUnits

    @abc.abstractmethod
    def __ReadBasicData(self):
        raise NotImplementedError

    @abc.abstractmethod
    def __ReadInternalName(self):
        raise NotImplementedError

    @abc.abstractmethod
    def __DetermineFieldDimension(self, file_content):
        raise NotImplementedError


class OsirisFieldReader(FieldReaderBase):
    def __init__(self, location, speciesName, dataName):
        FieldReaderBase.__init__(self, location, speciesName, dataName)

    def __ReadBasicData(self):
        fileName = self.__dataName + "-"
        if self.__speciesName != "":
            fileName += self.__speciesName + "-"
        fileName += str(0).zfill(6)
        ending = ".h5"
        file_path = self.__location + "/" + fileName + ending
        file_content = h5py.File(file_path, 'r')
        self.__ReadInternalName(file_content)
        self.__DetermineFieldDimension(file_content)
        file_content.close()
        
    def __ReadInternalName(self, file_content):
        self.__internalName = "/" + list(file_content.keys())[1]

    def __DetermineFieldDimension(self, file_content):
        if '/AXIS/AXIS3' in file_content:
            self.__fieldDimension = "3D"
        else:
            self.__fieldDimension = "2D"

    def __OpenFileAndReadData(self):
        fileName = self.name + "-"
        if self.speciesName != "":
            fileName += self.speciesName + "-"
        fileName += str(timeStep).zfill(6)
        ending = ".h5"
        file_path = self.location + "/" + fileName + ending
        file_content = h5py.File(file_path, 'r')
        self.__data = file_content[self.internalName][()]
        file_content.close()

    def __OpenFileAndReadUnits(self):
        fileName = self.name + "-"
        if self.speciesName != "":
            fileName += self.speciesName + "-"
        fileName += str(timeStep).zfill(6)
        ending = ".h5"
        file_path = self.location + "/" + fileName + ending
        file_content = h5py.File(file_path, 'r')
        if sys.version_info[0] < 3:
            self.__axisUnits["z"] = str(list(file_content['/AXIS/AXIS1'].attrs["UNITS"])[0])
            self.__axisUnits["y"] = str(list(file_content['/AXIS/AXIS2'].attrs["UNITS"])[0])
            self.__dataUnits = str(list(file_content[self.internalName].attrs["UNITS"])[0])
        else:
            self.__axisUnits["z"] = str(list(file_content['/AXIS/AXIS1'].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")
            self.__axisUnits["y"] = str(list(file_content['/AXIS/AXIS2'].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")
            self.__dataUnits = str(list(file_content[self.internalName].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")
        file_content.close()


class HiPACEFieldReader(FieldDataReader):
    def __init__(self, location, speciesName, dataName):
        FieldReaderBase.__init__(self, location, speciesName, dataName)

    def __ReadBasicData(self):
        raise NotImplementedError
        
    def __ReadInternalName(self, file_content):
        raise NotImplementedError

    def __DetermineFieldDimension(self, file_content):
        raise NotImplementedError

    def __OpenFileAndReadData(self):
        raise NotImplementedError

    def __OpenFileAndReadUnits(self):
        raise NotImplementedError