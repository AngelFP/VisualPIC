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


class RawDataReaderBase(DataReader):
    """Parent class for all rawDataReaders"""
    __metaclass__  = abc.ABCMeta
    def __init__(self, location, speciesName, dataName, internalName):
        DataReader.__init__(self, location, speciesName, dataName, internalName)
        self.internalName = dataName

    def GetData(self, timeStep):
        if timeStep != self.currentTimeStep:
            self.currentTimeStep = timeStep
            self.OpenFileAndReadData()
        return self.data

    def GetDataUnits(self):
        if self.dataUnits == "":
            self.OpenFileAndReadUnits()
        return self.dataUnits

    def GetTime(self, timeStep):
        if timeStep != self.currentTimeStep:
            self.currentTimeStep = timeStep
            self.OpenFileAndReadData()
        return self.currentTime

    def GetTimeUnits(self):
        if self.timeUnits == "":
            self.OpenFileAndReadUnits()
        return self.timeUnits

class OsirisRawDataReader(RawDataReaderBase):
    def __init__(self, location, speciesName, dataName, internalName):
        RawDataReaderBase.__init__(self, location, speciesName, dataName, internalName)

    def OpenFileAndReadData(self):
        file_content = self.OpenFile(self.currentTimeStep)
        if self.internalName == "tag":
            tags = np.array(file_content.get(self.internalName))
            self.data = (tags[:,0]-tags[:,1])*tags[:,0]
        else:
            self.data = np.array(file_content.get(self.internalName))
        self.currentTime = file_content.attrs["TIME"][0]
        file_content.close()

    def OpenFileAndReadUnits(self):
        file_content = self.OpenFile(0)
        if sys.version_info[0] < 3:
            self.dataUnits = str(list(file_content[self.internalName].attrs["UNITS"])[0])
            self.timeUnits = str(file_content.attrs["TIME UNITS"][0])
        else:
            self.dataUnits = str(list(file_content[self.internalName].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")
            self.timeUnits = str(file_content.attrs["TIME UNITS"][0])[2:-1].replace("\\\\","\\")
        file_content.close()

    def OpenFile(self, timeStep):
        fileName = "RAW-" + self.speciesName + "-" + str(timeStep).zfill(6)
        ending = ".h5"
        file_path = self.location + "/" + fileName + ending
        file_content = h5py.File(file_path, 'r')
        return file_content


class HiPACERawDataReader(RawDataReaderBase):
    def __init__(self, location, speciesName, dataName, internalName):
        RawDataReaderBase.__init__(self, location, speciesName, dataName, internalName)

    def OpenFileAndReadData(self):
        raise NotImplementedError

    def OpenFileAndReadUnits(self):
        raise NotImplementedError


class PIConGPURawDataReader(RawDataReaderBase):
    def __init__(self, location, speciesName, dataName, internalName):
        RawDataReaderBase.__init__(self, location, speciesName, dataName, internalName)

    def OpenFileAndReadData(self):
        raise NotImplementedError

    def OpenFileAndReadUnits(self):
        raise NotImplementedError