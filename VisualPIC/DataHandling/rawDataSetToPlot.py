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

class RawDataSetToPlot:
    def __init__(self, dataSet, unitConverter):
        self._dataSet = dataSet
        self._unitConverter = unitConverter
        self._dataProperties = {
            "name":dataSet.GetName(), 
            "speciesName":dataSet.GetSpeciesName(), 
            "timeSteps":dataSet.GetTimeSteps(),
            "dataSetUnits":dataSet.GetDataUnits(), 
            "timeUnits":dataSet.GetTimeUnits(),
            "possibleDataSetUnits":self._GetPossibleDataSetUnits(),
            "possibleTimeUnits":self._GetPossibleTimeUnits()
        }
            
    def _GetPossibleDataSetUnits(self):
        return self._unitConverter.GetPossibleDataUnits(self._dataSet)

    def _GetPossibleTimeUnits(self):
        return self._unitConverter.GetPossibleTimeUnits(self._dataSet)

    def GetTime(self, timeStep):
        return self._unitConverter.GetTimeInUnits(self._dataSet, self._dataProperties["timeUnits"], timeStep)
        
    def GetDataSetPlotData(self, timeStep):
        return self._unitConverter.GetDataInUnits(self._dataSet, self._dataProperties["dataSetUnits"], timeStep)
    
    def GetProperty(self, propertyName):
        return self._dataProperties[propertyName]

    def SetProperty(self, propertyName, value):
        self._dataProperties[propertyName] = value

    def GetDataProperties(self):
        return self._dataProperties
        
    def SetDataProperties(self, props):
        self._dataProperties = props