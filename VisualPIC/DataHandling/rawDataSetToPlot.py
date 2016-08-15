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
        self.__dataSet = dataSet
        self.__unitConverter = unitConverter
        self.__dataProperties = {
            "name":dataSet.GetName(), 
            "speciesName":dataSet.GetSpeciesName(), 
            "dataSetUnits":dataSet.GetDataUnits(), 
            "possibleDataSetUnits":self.__GetPossibleDataSetUnits()
        }
            
    def __GetPossibleDataSetUnits(self):
        return self.__unitConverter.GetRawDataSetUnitsOptions(self.__dataSet)
        
    def GetDataSetPlotData(self, timeStep):
        return self.__unitConverter.GetRawDataInUnits(timeStep, self.__dataSet, __dataProperties["dataSetUnits"])
    
    def GetProperty(self, propertyName):
        return self.__dataProperties[propertyName]

    def GetDataProperties(self):
        return self.__dataProperties
        
    def SetDataProperties(self, props):
        self.__dataProperties = props