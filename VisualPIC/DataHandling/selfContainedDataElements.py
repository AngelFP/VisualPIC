# -*- coding: utf-8 -*-

#Copyright 2016-2018 Angel Ferran Pousa, DESY
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
    def __init__(self, standardName, dataValues, dataUnits, hasNonIsUnits, timeValues, timeUnits, timeSteps, speciesName = ''):
        """Constructor.

        Keyword arguments:
        standardName -- standard VisualPIC name of the data.
        dataValues -- a matrix containing all the data, where the columns are the particles and the rows are time steps. Data should be in the original units from the data file.
        dataUnits  -- string containing the data units.
        timeValues -- a 1D array containing the time values on each time step. Same number of elements as rows in dataValues. Data should be in the original units from the data file.
        timeUnits  -- string containing the time units.
        timeSteps  -- a 1D array containing the number of each time step saved to disk during the simulation.
        """
        DataElement.__init__(self, standardName, timeSteps, speciesName, hasNonIsUnits)
        self.dataValues = dataValues
        self.dataUnits = dataUnits
        self.timeValues = timeValues
        self.timeUnits = timeUnits

    def GetDataOriginalUnits(self):
        return self.dataUnits

    def GetTimeInOriginalUnits(self, timeStep):
        index = np.where(self.timeSteps == timeStep)[0][0]
        return self.timeValues[index]
        
    def GetTimeOriginalUnits(self):
        return self.timeUnits


class SelfContainedRawDataSet(SelfContainedDataElement):
    def __init__(self, standardName, dataValues, dataUnits, hasNonIsUnits, timeValues, timeUnits, timeSteps, speciesName = ''):
        return super().__init__(standardName, dataValues, dataUnits, hasNonIsUnits, timeValues, timeUnits, timeSteps, speciesName)
    
    """
    Get data in original units
    """
    def GetDataInOriginalUnits(self, timeStep):
        index = np.where(self.timeSteps == timeStep)[0][0]
        rawValues = self.dataValues[index] # migth contain NaN values
        dataMask = np.isfinite(rawValues)
        return rawValues[dataMask] # return the data without the NaN values
    
    """
    Get data in any units
    """
    def GetDataInUnits(self, units, timeStep):
        return self._unitConverter.GetDataInUnits(self, units, self.GetDataInOriginalUnits(timeStep))

    """
    Get data in IS units
    """
    def GetDataInISUnits(self, timeStep):
        return self._unitConverter.GetDataInISUnits(self, self.GetDataInOriginalUnits(timeStep))


class EvolutionData(SelfContainedDataElement):
    def __init__(self, standardName, dataValues, dataUnits, hasNonIsUnits, timeValues, timeUnits, timeSteps, speciesName = ''):
        return super().__init__(standardName, dataValues, dataUnits, hasNonIsUnits, timeValues, timeUnits, timeSteps, speciesName)

    def GetAllDataInOriginalUnits(self):
        return self.dataValues

    def GetAllDataInUnits(self, units):
        return self._unitConverter.GetDataInUnits(self, units, self.dataValues)

    def GetAllTimeInOriginalUnits(self):
        return self.timeValues

    def GetAllDataInISUnits(self):
        return self._unitConverter.GetDataInISUnits(self, self.GetAllDataInOriginalUnits())