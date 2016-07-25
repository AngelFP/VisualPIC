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

class Subplot:
    
    def __init__(self, subplotPosition, fieldsToPlotList = list(), axisData = {}):
        
        self.subplotName = ""
        self.plottedSpeciesName = ""
        self.subplotPosition = subplotPosition
        
        self.dataType = "" # Two possible data types: "Field" and "Axis".
        self.plotType = ""
        self.possiblePlotTypes = list()
        # the fieldsToPlotList would contain 2D fields to plot, which already contain x and y coordinates and the values at each point
        self.fieldsToPlotList = fieldsToPlotList        
        if len(fieldsToPlotList) > 0:
            self.dataType = "Field"
        
        # axisData, on the other side, would be for plots that are made individually 
        #stating wich quantities go in each axis. For example x1 vs p1.
        # Up to 3 axis can be included (x,y and z). It is a dictionary.
        self.axisData = axisData
        if len(axisData) > 0:
            self.dataType = "Axis"
        
        # axis properties
        self.xAxisProps = {}
        self.yAxisProps = {}
        self.zAxisProps = {}
        self.axisTitleProps = {}
        
        self.xLims = [] # contains min and max values in x axis
        self.yLims = []
        self.zLims = []
        
        self.SetSubplotName()  
        self.SetPlottedSpeciesName()
        self.LoadPossiblePlotTypes()
        self.SetDefaultValues()
        
    def SetTitleProperty(self, targetProperty, value):
        self.axisTitleProps[targetProperty] = value
        
    def GetTitleProperty(self, targetProperty):
        return self.axisTitleProps[targetProperty]
        
    def SetAxisProperty(self, axis, targetPropery, value):
        if axis == "x":
            self.xAxisProps[targetPropery] = value
        elif axis == "y":
            self.yAxisProps[targetPropery] = value
        elif axis == "z":
            self.zAxisProps[targetPropery] = value
            
    def GetAxisProperty(self, axis, targetPropery):
        if axis == "x":
            return self.xAxisProps[targetPropery]
        elif axis == "y":
            return self.yAxisProps[targetPropery]
        elif axis == "z":
            return self.zAxisProps[targetPropery]
        
    def GetPosition(self):
        return self.subplotPosition
        
    def SetDefaultValues(self):
        if self.dataType == "Axis":
            self.SetAxisProperty("x", "LabelText", self.axisData["x"].GetName())
            self.SetAxisProperty("y", "LabelText", self.axisData["y"].GetName())
            if "z" in self.axisData:
                    self.SetAxisProperty("z", "LabelText", self.axisData["z"].GetName())
        elif self.dataType == "Field":
            self.SetAxisProperty("x", "LabelText", "z")
            self.SetAxisProperty("y", "LabelText", "y")
            self.SetAxisProperty("z", "LabelText", "x")
        
        defaultFontSize = 20  
        self.SetAxisProperty("x", "LabelSize", defaultFontSize)
        self.SetAxisProperty("y", "LabelSize", defaultFontSize)
        self.SetAxisProperty("z", "LabelSize", defaultFontSize)
        self.SetTitleProperty("FontSize", defaultFontSize)
        self.SetTitleProperty("Text", self.subplotName)
        
    def SetPosition(self, position):
        self.subplotPosition = position
        
    def LoadPossiblePlotTypes(self):
        self.possiblePlotTypes.clear()
        if self.dataType == "Field":
            if len(self.fieldsToPlotList) > 1:
                self.possiblePlotTypes = ["Image"]
            else:
                self.possiblePlotTypes = ["Image", "Surface"]
                
        if self.dataType == "Axis":
            self.possiblePlotTypes = ["Line", "Scatter"]
            
    def GetPossiblePlotTypes(self):
        return self.possiblePlotTypes
        
    def SetPlotType(self, plotType):
        self.plotType = plotType
        
    def GetPlotType(self):
        return self.plotType
        
    def GetDataType(self):
        return self.dataType
        
    def AddFieldToPlot(self, fieldToPlot):
        self.dataType = "Field"
        self.fieldsToPlotList.append(fieldToPlot)
        self.SetSubplotName()
        self.SetPlottedSpeciesName()
        
    def AddAxisData(self, data, axis):
        # axis should be a string ("x", "y", "z" or "weight")
        self.dataType = "Axis"
        self.axisData[axis] = data
        self.SetSubplotName()
        self.SetPlottedSpeciesName()
        
    def SetSubplotName(self):
        if self.dataType == "Field":
            for fieldToPlot in self.fieldsToPlotList:
                if self.subplotName == "":
                    self.subplotName = fieldToPlot.GetName()
                elif self.subplotName != fieldToPlot.GetName():
                    self.subplotName = "Mult. fields"
                    
        elif self.dataType == "Axis":
            if len(self.axisData) > 1:
                xName = self.axisData["x"].GetName()
                yName = self.axisData["y"].GetName()
                self.subplotName = xName + " vs " + yName
                
                if "z" in self.axisData:
                    zName = self.axisData["z"].GetName()
                    self.subplotName += " vs " + zName
        
    def SetPlottedSpeciesName(self):
        if self.dataType == "Field":
            for fieldToPlot in self.fieldsToPlotList:
                if self.plottedSpeciesName == "":
                    self.plottedSpeciesName = fieldToPlot.GetSpeciesName()
                elif self.plottedSpeciesName != fieldToPlot.GetSpeciesName():
                    self.plottedSpeciesName = "Mult. species"
                    
        elif self.dataType == "Axis":
            if len(self.axisData) > 1:
                xSpeciesName = self.axisData["x"].GetSpeciesName()
                self.plottedSpeciesName = xSpeciesName
                
                ySpeciesName = self.axisData["y"].GetSpeciesName()
                if ySpeciesName != self.plottedSpeciesName:
                    self.plottedSpeciesName = "Mult. Species"
                if "z" in self.axisData:
                    zSpeciesName = self.axisData["z"].GetSpeciesName()
                    if zSpeciesName != self.plottedSpeciesName:
                        self.plottedSpeciesName = "Mult. Species"
                        
    def GetName(self):
        return self.subplotName
        
    def GetPlottedSpeciesName(self):
        return self.plottedSpeciesName
        
    def GetFieldsToPlot(self):
        return self.fieldsToPlotList
        
    def GetAxisData(self):
        return self.axisData