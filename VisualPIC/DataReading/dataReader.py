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


class DataReader(object):
    """Parent class for all data readers (fieldReaders and rawDataReaders)"""
    __metaclass__  = abc.ABCMeta
    def __init__(self, location, speciesName, dataName):
        self.__location = location
        self.__speciesName = speciesName
        self.__dataName = dataName
        self.__currentTimeStep = 0
        self.__dataUnits = ""
        self.__data = None

    def GetData(self, timeStep):
        if timeStep != self.__currenTimeStep:
            self.__currentTimeStep = timeStep
            self.OpenFileAndReadData()
        return self.__data

    def GetUnits(self):
        if self.__dataUnits != "":
            self.OpenFileAndReadUnits()
        return self.__dataUnits

    @abc.abstractmethod
    def OpenFileAndReadData(self):
        raise NotImplementedError

    @abc.abstractmethod
    def OpenFileAndReadUnits(self):
        raise NotImplementedError

    @abc.abstractmethod
    def ReadData(self, file_content):
        raise NotImplementedError
    
    @abc.abstractmethod
    def ReadUnits(self, file_content):
        raise NotImplementedError


