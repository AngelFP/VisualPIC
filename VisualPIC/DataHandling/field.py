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

import sys

from VisualPIC.DataHandling.dataElement import DataElement
from VisualPIC.DataReading.dataReaderSelectors import FieldReaderSelector


class Field(DataElement):
    def __init__(self, simulationCode, name, location, timeSteps, speciesName=""):
        DataElement.__init__(self, simulationCode, name, location, timeSteps, speciesName)
        self.dataReader = FieldReaderSelector.GetReader(simulationCode, location, speciesName, name)
          
    def GetFieldDimension(self):
        return self.dataReader.fieldDimension

    def GetAxisData(self, timeStep):
        return self.dataReader.GetAxisData(timeStep) #dictionary
        
    def GetAxisUnits(self):
        return self.dataReader.GetAxisUnits()
        
        