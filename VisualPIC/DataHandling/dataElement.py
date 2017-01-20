# -*- coding: utf-8 -*-

#Copyright 2016-2017 Ángel Ferran Pousa
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

class DataElement(object):
    """Base class for all data elements (fields and rawDataSets)"""
    def __init__(self, unitConverter, standardName, timeSteps, speciesName = "", hasNonISUnits = True):
        self._unitConverter = unitConverter
        self.dataStandardName = standardName
        self.speciesName = speciesName
        self.timeSteps = timeSteps # array of integers
        self.hasNonISUnits = hasNonISUnits
        
    def GetName(self):
        return self.dataStandardName

    def GetSpeciesName(self):
        return self.speciesName

    def GetTimeSteps(self):
        return self.timeSteps

    def GetPossibleDataUnits(self):
        return self._unitConverter.GetPossibleDataUnits(self)

    def GetDataISUnits(self):
        return self._unitConverter.GetDataISUnits(self)

    def GetDataInISUnits(self, timeStep):
        return self._unitConverter.GetDataInISUnits(self, timeStep)

    def GetDataInUnits(self, units, timeStep):
        return self._unitConverter.GetDataInUnits(self, units, timeStep)

    def GetAxisInUnits(self, axis, units, timeStep):
        return self._unitConverter.GetAxisInUnits(axis, self, units, timeStep)

    def GetAxisInISUnits(self, axis, timeStep):
        return self._unitConverter.GetAxisInISUnits(axis, self, timeStep)

    def GetData(self, timeStep):
        raise NotImplementedError
        
    def GetDataUnits(self):
        raise NotImplementedError

    def GetTimeInUnits(self, units, timeStep):
        return self._unitConverter.GetTimeInUnits(self, units, timeStep)

    def GetTime(self, timeStep):
        raise NotImplementedError
    
    def GetPossibleTimeUnits(self):
        return self._unitConverter.GetPossibleTimeUnits(self)

    def GetTimeUnits(self):
        raise NotImplementedError

