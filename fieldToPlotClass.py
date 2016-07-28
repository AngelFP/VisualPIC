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

class FieldToPlot:
    def __init__(self, field, unitConverter, colorMapsCollection, isPartOfMultiplot = False, plotType = None, colorMap = None, position = 1, useCustomScale = False, vMax = 1, vMin = 0):
        
        self.field = field
        self.unitConverter = unitConverter
        self.colorMapsCollection = colorMapsCollection
        self.isPartOfMultiplot = isPartOfMultiplot
        self.normUnits = {}
        self.fieldUnits = ""
        self.axesUnits = {}
        self.plotType = plotType
        self.colorMap = colorMap
        self.position = position
        self.useCustomScale = useCustomScale
        self.vMax = vMax
        self.vMin = vMin
        self.SetDefaultColorMap()
        self.dataType = "Field"
        self.SetNormalizedUnits()
    
    def SetNormalizedUnits(self):
        self.normUnits["Field"] = self.field.GetNormalizedUnits("Field")
        self.normUnits["x"] = self.field.GetNormalizedUnits("x")
        self.normUnits["y"] = self.field.GetNormalizedUnits("y")
        
        self.fieldUnits = self.normUnits["Field"]
        self.axesUnits["x"] = self.normUnits["x"]
        self.axesUnits["y"] = self.normUnits["y"]
        
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
        
        return self.unitConverter.GetPlotDataInUnits(timeStep, self.field, self.fieldUnits, self.axesUnits, self.normUnits)
        
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
        self.axisUnitsOptions = self.unitConverter.getAxisUnitsOptions(self.field)
        return self.axisUnitsOptions
        
    def SetFieldUnits(self, units):
        self.fieldUnits = units
        
    def SetAxisUnits(self, axis, units):
        # axis = "x", "y" or "z"
        self.axesUnits[axis] = units
        
    def GetPossibleColorMaps(self):
        if self.isPartOfMultiplot:
            return self.colorMapsCollection.GetTransparentColorMapsNames()
        else:
            return self.colorMapsCollection.GetSingleColorMapsNamesList()
            
    def GetDataType(self):
        return self.dataType
        
    def GetFieldUnits(self):
        return self.fieldUnits
        
    def GetAxisUnits(self, axis):
        # axis = "x", "y" or "z"
        return self.axesUnits[axis]

        
    def GetFieldInfo(self):
        
        info = {
            "name":self.GetName(), 
            "speciesName":self.GetSpeciesName(), 
            "fieldUnits":self.fieldUnits, 
            "possibleFieldUnits":self.GetPossibleFieldUnits(),
            "axesUnits":self.axesUnits, 
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
        self.axesUnits = info["axesUnits"]
        self.useCustomScale = not info["autoScale"]
        self.vMax = info["maxVal"]
        self.vMin = info["minVal"]
        self.colorMap = info["cMap"]
        self.plotType = info["plotType"]