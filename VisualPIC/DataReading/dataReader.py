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
    def __init__(self, location, speciesName, dataName, internalName = ""):
        self.location = location
        self.speciesName = speciesName
        self.dataName = dataName
        self.internalName = internalName
        self.currentTimeStep = None # time step number
        self.currentTime = None # simulation time in the current time step
        self.timeUnits = ""
        self.dataUnits = ""
        self.data = None

    @abc.abstractmethod
    def OpenFileAndReadData(self):
        raise NotImplementedError

    @abc.abstractmethod
    def OpenFileAndReadUnits(self):
        raise NotImplementedError


