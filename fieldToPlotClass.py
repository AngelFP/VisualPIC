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
    def __init__(self, field: Field, unitConverter, fieldUnits = "Norm", axisUnits = "Norm", plotType = None, colorMap = None, position = 1, vMax = "auto", vMin ="auto"):
        
        self.field = field
        self.unitConverter = unitConverter
        self.fieldUnits = fieldUnits
        self.axisUnits = axisUnits
        self.plotType = plotType
        self.colorMap = colorMap
        self.position = position
        self.vMax = vMax
        self.vMin = vMin
        
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
        self.vMax = "auto"
        self.vMin = "auto"
        
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
        return self.vMax != "auto"
        
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