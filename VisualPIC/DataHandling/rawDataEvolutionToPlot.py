# -*- coding: utf-8 -*-

#Copyright 2016-2017 Angel Ferran Pousa
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

class RawDataEvolutionToPlot:
    # todo: implement unitConverter
    def __init__(self, dataSetName, particle): #, unitConverter):
        self._dataSet = particle.GetWholeSimulationQuantity(dataSetName)
        #self._unitConverter = unitConverter
        self._dataProperties = {
            "name":dataSetName,
            "dataSetUnits":self._dataSet["units"], 
            "possibleDataSetUnits":self._GetPossibleDataSetUnits()
        }
            
    def _GetPossibleDataSetUnits(self):
        return self._dataSet["units"]
        
    def GetDataSetPlotData(self):
        return self._dataSet["values"]
    
    def GetProperty(self, propertyName):
        return self._dataProperties[propertyName]

    def GetDataProperties(self):
        return self._dataProperties
        
    def SetDataProperties(self, props):
        self._dataProperties = props