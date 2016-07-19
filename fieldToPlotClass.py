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

from fieldClass import Field
class FieldToPlot:
    def __init__(self, field: Field, unitConverter, colorMapsCollection, isPartOfMultiplot = False, fieldUnits = "Norm", axisUnits = "Norm", plotType = None, colorMap = None, position = 1, useCustomScale = False, vMax = 1, vMin = 0):
        
        self.field = field
        self.unitConverter = unitConverter
        self.colorMapsCollection = colorMapsCollection
        self.isPartOfMultiplot = isPartOfMultiplot
        self.fieldUnits = fieldUnits
        self.axisUnits = axisUnits
        self.plotType = plotType
        self.colorMap = colorMap
        self.position = position
        self.useCustomScale = useCustomScale
        self.vMax = vMax
        self.vMin = vMin
        self.SetDefaultColorMap()
    
    def SetDefaultColorMap(self):
        if self.isPartOfMultiplot:
            self.colorMap = "Base gray"
        else:
            name = self.GetName()
            if "e1" in name or "e2" in name or "e3" in name or "b1" in name or "b2" in name or "b3" in name:
                self.colorMap = "RdBu"
            elif "charge" in name:
                self.colorMap = "YlGnBu"
            else:
                self.colorMap = "jet"
    
    def GetPosition(self):
        return self.position
        
    def GetFieldPlotData(self, timeStep):
        
        return self.unitConverter.GetPlotDataInUnits(timeStep, self.field, self.fieldUnits, self.axisUnits)
        
    def GetColorMap(self):
        return self.colorMap
        
    def GetName(self):
        return self.field.GetName()
        
    def GetScale(self):
        return self.vMin, self.vMax
        
    def SetScale(self, vMin, vMax):
        self.vMax = vMax
        self.vMin = vMin
        
    def SetAutoScale(self):
        self.useCustomScale = False
        
    def SetPlotPosition(self, position):
        self.position = position;
        
    def GetSpeciesName(self):
        return self.field.GetSpeciesName()
    
    def SetColorMap(self, colorMap):
        self.colorMap = colorMap
        
    def SetPlotType(self, plotType):
        self.plotType = plotType
        
    def GetPlotType(self, plotType):
        return self.plotType
        
    def IsScaleCustom(self):
        return self.useCustomScale
        
    def GetPossibleFieldUnits(self):
        self.fieldUnitsOptions = self.unitConverter.getFieldUnitsOptions(self.field)
        return self.fieldUnitsOptions
        
    def GetPossibleAxisUnits(self):
        self.axisUnitsOptions = self.unitConverter.getAxisUnitsOptions()
        return self.axisUnitsOptions
        
    def SetFieldUnits(self, units):
        self.fieldUnits = units
        
    def SetAxisUnits(self, units):
        self.axisUnits = units
        
    def GetPossibleColorMaps(self):
        if self.isPartOfMultiplot:
            return self.colorMapsCollection.GetTransparentColorMapsNames()
        else:
            return self.colorMapsCollection.GetSingleColorMapsNamesList()
        
    def GetFieldInfo(self):
        
        info = {
            "name":self.GetName(), 
            "speciesName":self.GetSpeciesName(), 
            "fieldUnits":self.fieldUnits, 
            "possibleFieldUnits":self.GetPossibleFieldUnits(),
            "axisUnits":self.axisUnits, 
            "possibleAxisUnits":self.GetPossibleAxisUnits(),
            "autoScale":not self.IsScaleCustom(),
            "maxVal":self.vMax,
            "minVal":self.vMin,
            "cMap":self.colorMap,
            "possibleColorMaps":self.GetPossibleColorMaps(),
            "plotType":self.plotType
        }
        
        return info
        
    def SetFieldInfo(self, info):
        
        self.fieldUnits = info["fieldUnits"]
        self.axisUnits = info["axisUnits"]
        if info["autoScale"]:
            self.SetAutoScale()
        else:
            self.vMax = info["maxVal"]
            self.vMin = info["minVal"]
        self.colorMap = info["cMap"]
        self.plotType = info["plotType"]