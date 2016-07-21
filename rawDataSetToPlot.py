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
    def __init__(self, dataSet, unitConverter, dataSetUnits = "Norm", plotType = None, position = 1):
        
        self.dataSet = dataSet
        self.unitConverter = unitConverter
        self.dataSetUnits = dataSetUnits
        self.plotType = plotType
        self.position = position
        self.dataType = "Raw"
    
    def GetPosition(self):
        return self.position
        
    def GetDataSetPlotData(self, timeStep):
        
        return self.unitConverter.GetRawDataInUnits(timeStep, self.dataSet, self.dataSetUnits)
        
    def GetName(self):
        return self.dataSet.GetName()
        
    def SetPlotPosition(self, position):
        self.position = position;
        
    def GetSpeciesName(self):
        return self.dataSet.GetSpeciesName()
        
    def SetPlotType(self, plotType):
        self.plotType = plotType
        
    def GetPlotType(self, plotType):
        return self.plotType
        
    def GetPossibleDataSetUnits(self):
        self.dataSetUnitsOptions = self.unitConverter.getRawDataSetUnitsOptions(self.dataSet)
        return self.dataSetUnitsOptions
        
    def SetDataSetUnits(self, units):
        self.dataSetUnits = units
        
    def GetDataType(self):
        return self.dataType    
        
    def GetDataSetInfo(self):
        
        info = {
            "name":self.GetName(), 
            "speciesName":self.GetSpeciesName(), 
            "dataSetUnits":self.dataSetUnits, 
            "possibleDataSetUnits":self.GetPossibleDataSetUnits(),
            "plotType":self.plotType
        }
        
        return info
        
    def SetDataSetInfo(self, info):
        
        self.dataSetUnits = info["dataSetUnits"]
        self.plotType = info["plotType"]