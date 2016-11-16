# -*- coding: utf-8 -*-

#Copyright 2016 Angel Ferran Pousa
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

import numpy as np

from VisualPIC.DataHandling.dataElement import DataElement


class SelfContainedDataElement(DataElement):
    def __init__(self, standardName, dataValues, dataUnits, timeValues, timeUnits, timeSteps, speciesName = ''):
        """Constructor.

        Keyword arguments:
        dataValues -- a matrix containing all the data, where the columns are the particles and the rows are time steps.
        dataUnits  -- string containing the data units.
        timeValues -- a 1D array containing the time values on each time step. Same number of elements as rows in dataValues.
        timeUnits  -- string containing the time units.
        timeSteps  -- a 1D array containing the number of each time step saved to disk during the simulation.
        """
        SelfContainedDataElement.__init__(self, standardName, timeSteps, speciesName)
        self.dataValues = dataValues
        self.dataUnits = dataUnits
        self.timeValues = timeValues
        self.timeUnits = timeUnits

    def GetData(self, timeStep):
        index = np.where(self.timeSteps == timeStep)[0][0]
        return self.dataValues[index]
        
    def GetDataUnits(self):
        return self.dataUnits

    def GetTime(self, timeStep):
        index = np.where(self.timeSteps == timeStep)[0][0]
        return self.timeValues[index]
        
    def GetTimeUnits(self):
        return self.timeUnits


class SelfContainedRawDataSet(SelfContainedDataElement):
    def __init__(self, standardName, dataValues, dataUnits, timeValues, timeUnits, timeSteps, speciesName = ''):
        SelfContainedRawDataSet.__init__(self, standardName, dataValues, dataUnits, timeValues, timeUnits, timeSteps, speciesName)