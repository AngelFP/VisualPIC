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


class RawDataReader(DataReader):
    """Parent class for all rawDataReaders"""
    __metaclass__  = abc.ABCMeta
    def __init__(self, location, speciesName, dataName):
        DataReader.__init__(self, location, speciesName, dataName)


class OsirisRawDataReader(RawDataReader):
    def __init__(self, location, speciesName, dataName):
        RawDataReader.__init__(self, location, speciesName, dataName)

    def OpenFileAndReadData(self):
        fileName = "RAW-" + self.__speciesName + "-" + str(self.__currentTimeStep).zfill(6)
        ending = ".h5"
        file_path = self.__location + "/" + fileName + ending
        file_content = h5py.File(file_path, 'r')
        self.ReadRawData(file_content)
        file_content.close()

    def OpenFileAndReadUnits(self):
        fileName = "RAW-" + self.__speciesName + "-" + str(0).zfill(6)
        ending = ".h5"
        file_path = self.__location + "/" + fileName + ending
        file_content = h5py.File(file_path, 'r')
        self.ReadUnits(file_content)
        file_content.close()
        
    def ReadData(self,file_content):
        self.__data = file_content[self.internalName][()] #the [()] ending means we get all the data as an array, otherwise we only get some chunks (more efficient, but its not an array, and thus we cant transpose it) 

    def ReadUnits(self, file_content):
        if sys.version_info[0] < 3:
            self.__dataUnits = str(list(file_content[self.internalName].attrs["UNITS"])[0])
        else:
            self.__dataUnits = str(list(file_content[self.internalName].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")


class HiPACERawDataReader(RawDataReader):
    def __init__(self, location, speciesName, dataName):
        RawDataReader.__init__(self, location, speciesName, dataName)

    def OpenFileAndReadData(self):
        raise NotImplementedError

    def OpenFileAndReadUnits(self):
        raise NotImplementedError
        
    def ReadData(self,file_content):
        raise NotImplementedError

    def ReadUnits(self, file_content):
        raise NotImplementedError