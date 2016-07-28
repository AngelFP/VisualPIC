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

import copy

class Subplot:
    
    def __init__(self, subplotPosition, colorMapsCollection, fieldsToPlotList = list(), axisData = {}):
        
        self.subplotName = ""
        self.plottedSpeciesName = ""
        self.subplotPosition = subplotPosition
        
        self.dataType = "" # Two possible data types: "Field" and "Axis".
        self.possiblePlotTypes = list()
        self.colorMapsCollection = colorMapsCollection
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
        
        # colorBar
        self.colorbarProps = {}
        
        # plot settings
        self.plotProps = {}
        
        
        self.xLims = [] # contains min and max values in x axis
        self.yLims = []
        self.zLims = []
        
        self.SetSubplotName()  
        self.SetPlottedSpeciesName()
        self.LoadPossiblePlotTypes()
        self.SetDefaultValues()
    
# Initialization    
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
                        
    def LoadPossiblePlotTypes(self):
        self.possiblePlotTypes.clear()
        if self.dataType == "Field":
            if len(self.fieldsToPlotList) > 1:
                self.possiblePlotTypes = ["Image"]
            else:
                self.possiblePlotTypes = ["Image", "Surface"]
                
        if self.dataType == "Axis":
            self.possiblePlotTypes = ["Histogram", "Scatter"]
            
    def SetDefaultValues(self):
        
        self.LoadDefaultAxesValues()
        self.SetAxesToDefaultValues()
        
        self.LoadDefaultColorBarValues()
        self.SetColorbarToDefaultValues()
        
        self.LoadDefaultTitleValues()
        self.SetTitleToDefaultValues()
        
        self.LoadDefaultPlotProperties()
        self.SetPlotPropertiesToDefault()
        
    def LoadDefaultAxesValues(self):
        defaultFontSize = 20  
        if self.dataType == "Axis":
            self.SetAxisProperty("x", "DefaultLabelText", self.axisData["x"].GetName())
            self.SetAxisProperty("y", "DefaultLabelText", self.axisData["y"].GetName())
            self.SetAxisProperty("x", "DefaultUnits", self.axisData["x"].GetUnits())
            self.SetAxisProperty("y", "DefaultUnits", self.axisData["y"].GetUnits())
            self.SetAxisProperty("x", "DefaultLabelFontSize", defaultFontSize)
            self.SetAxisProperty("y", "DefaultLabelFontSize", defaultFontSize)
            if "z" in self.axisData:
                self.SetAxisProperty("z", "DefaultLabelText", self.axisData["z"].GetName())
                self.SetAxisProperty("z", "DefaultUnits", self.axisData["z"].GetUnits())
                self.SetAxisProperty("z", "DefaultLabelFontSize", defaultFontSize)
        elif self.dataType == "Field":
            self.SetAxisProperty("x", "DefaultLabelText", "z")
            self.SetAxisProperty("y", "DefaultLabelText", "y")
            #self.SetAxisProperty("z", "DefaultLabelText", "x")
            
            self.SetAxisProperty("x", "DefaultUnits", self.fieldsToPlotList[0].GetAxisUnits("x"))
            self.SetAxisProperty("y", "DefaultUnits", self.fieldsToPlotList[0].GetAxisUnits("y"))
            #self.SetAxisProperty("z", "DefaultUnits", self.fieldsToPlotList[0].GetAxisUnits("z"))
            
            self.SetAxisProperty("x", "DefaultLabelFontSize", defaultFontSize)
            self.SetAxisProperty("y", "DefaultLabelFontSize", defaultFontSize)
            
            
    def SetAxesToDefaultValues(self):
        self.SetAxisProperty("x", "LabelText", self.GetAxisProperty("x", "DefaultLabelText"))
        self.SetAxisProperty("y", "LabelText", self.GetAxisProperty("y", "DefaultLabelText"))
        self.SetAxisProperty("x", "AutoLabel", True)
        self.SetAxisProperty("y", "AutoLabel", True)
        self.SetAxisProperty("x", "Units", self.GetAxisProperty("x", "DefaultUnits"))
        self.SetAxisProperty("y", "Units", self.GetAxisProperty("y", "DefaultUnits"))
        self.SetAxisProperty("x", "LabelFontSize", self.GetAxisProperty("x", "DefaultLabelFontSize"))
        self.SetAxisProperty("y", "LabelFontSize", self.GetAxisProperty("y", "DefaultLabelFontSize"))
        if len(self.zAxisProps)>0:
            self.SetAxisProperty("z", "LabelText", self.GetAxisProperty("z", "DefaultLabelText"))
            self.SetAxisProperty("z", "Units", self.GetAxisProperty("z", "DefaultUnits"))
            self.SetAxisProperty("z", "LabelFontSize", self.GetAxisProperty("z", "DefaultLabelFontSize"))
            
    def LoadDefaultColorBarValues(self):
        self.colorbarProps["DefaultFontSize"] = 20
        self.colorbarProps["DefaultAutoTickLabelSpacing"] = True
        
    def SetColorbarToDefaultValues(self):
        self.colorbarProps["FontSize"] = self.colorbarProps["DefaultFontSize"]
        self.colorbarProps["AutoTickLabelSpacing"] = self.colorbarProps["DefaultAutoTickLabelSpacing"]
        
    def LoadDefaultTitleValues(self):
        self.SetTitleProperty("DefaultFontSize", 20)
        self.SetTitleProperty("DefaultText", self.subplotName)
        self.SetTitleProperty("DefaultAutoText", True)
        
    def SetTitleToDefaultValues(self):
        self.SetTitleProperty("FontSize", self.GetTitleProperty("DefaultFontSize"))
        self.SetTitleProperty("Text", self.GetTitleProperty("DefaultText"))
        self.SetTitleProperty("AutoText", self.GetTitleProperty("DefaultAutoText"))
        
    def LoadDefaultPlotProperties(self):
        if self.dataType == "Field":
            self.plotProps["DefaultPlotType"] = "Image"
        elif self.dataType == "Axis":
            self.plotProps["DefaultPlotType"] = "Histogram"
            self.plotProps["DefaultXBins"] = 100
            self.plotProps["DefaultYBins"] = 100
            self.plotProps["DefaultUseChargeWeighting"] = True
            self.plotProps["DefaultChargeUnits"] = self.axisData["weight"].GetUnits()
            self.plotProps["DefaultCMap"] = self.GetAxisDefaultColorMap(self.plotProps["DefaultPlotType"])
            self.plotProps["DefaultDisplayColorbar"] = True
        self.plotProps["DefaultAxesDimension"] = self.GetAxesDimension(self.plotProps["DefaultPlotType"])
            
    def SetPlotPropertiesToDefault(self):
        if self.dataType == "Field":
            self.plotProps["PlotType"] = self.plotProps["DefaultPlotType"]
        elif self.dataType == "Axis":
            self.plotProps["PlotType"] = self.plotProps["DefaultPlotType"]
            self.plotProps["XBins"] = self.plotProps["DefaultXBins"]
            self.plotProps["YBins"] = self.plotProps["DefaultYBins"]
            self.plotProps["UseChargeWeighting"] = self.plotProps["DefaultUseChargeWeighting"]
            self.plotProps["ChargeUnits"] = self.plotProps["DefaultChargeUnits"]
            self.plotProps["CMap"] = self.plotProps["DefaultCMap"]
            self.plotProps["DisplayColorbar"] = self.plotProps["DefaultDisplayColorbar"]
        self.plotProps["AxesDimension"] = self.plotProps["DefaultAxesDimension"]
        
# Interface methods

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
    
    def GetAxesUnitsOptions(self):
        unitsOptions = {}
        if self.dataType == "Field":
            unitsOptions["x"] = self.fieldsToPlotList[0].GetPossibleAxisUnits()
            unitsOptions["y"] = self.fieldsToPlotList[0].GetPossibleAxisUnits()
        if self.dataType == "Axis":
            unitsOptions["x"] = self.axisData["x"].GetPossibleDataSetUnits()
            unitsOptions["y"] = self.axisData["y"].GetPossibleDataSetUnits()
        return unitsOptions
        
    def GetWeightingUnitsOptions(self):
        return self.axisData["weight"].GetPossibleDataSetUnits()
        
    def GetAxisColorMapOptions(self, plotType):
        if plotType == "Histogram":
            return self.colorMapsCollection.GetAllColorMapNames()
        elif plotType == "Scatter":
            return self.colorMapsCollection.GetAllColorMapNamesWithTransparency()
            
    def GetAxisDefaultColorMap(self, plotType):
        if plotType == "Histogram":
            return "BlueT"
        elif plotType == "Scatter":
            return "Uniform Blue Transparent"
    def GetAxesDimension(self, plotType):
        ThreeDplotTypes = ["Surface", "Scatter3D"]
        if plotType in ThreeDplotTypes:
            return "3D"
        else:
            return "2D"
        
    def SetFieldAxisUnits(self, axis, units):
        for fieldToPlot in self.fieldsToPlotList:
            fieldToPlot.SetAxisUnits(axis, units)
        
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
            
    def SetAllAxisProperties(self, axis, properties):
        if axis == "x":
            self.xAxisProps = properties
        elif axis == "y":
            self.yAxisProps = properties
        if self.dataType == "Field":    
            self.SetFieldAxisUnits(axis, properties["Units"])
            
    def GetCopyAllAxisProperties(self, axis):
        if axis == "x":
            return copy.copy	(self.xAxisProps)
        elif axis == "y":
            return copy.copy(self.yAxisProps)
            
    def SetPosition(self, position):
        self.subplotPosition = position
        
    def GetPosition(self):
        return self.subplotPosition
            
    def GetPossiblePlotTypes(self):
        return self.possiblePlotTypes
        
    def GetPlotType(self):
        return self.plotProps["PlotType"]
        
    def GetDataType(self):
        return self.dataType
                        
    def GetName(self):
        return self.subplotName
        
    def GetPlottedSpeciesName(self):
        return self.plottedSpeciesName
        
    def GetFieldsToPlot(self):
        return self.fieldsToPlotList
        
    def GetAxisData(self):
        return self.axisData
        
    def SetColorBarProperty(self, prop, value):
        self.colorbarProps[prop] = value
    
    def GetColorBarProperty(self, prop):
        return self.colorbarProps[prop]
    
    def GetCopyAllColorbarProperties(self):
        return copy.copy(self.colorbarProps)
        
    def SetAllColorbarProperties(self, properties):
        self.colorbarProps = properties
        
    def GetCopyAllTitleProperties(self):
        return copy.copy(self.axisTitleProps)
        
    def SetAllTitleProperties(self, properties):
        self.axisTitleProps = properties
        
    def GetCopyAllPlotProperties(self):
        return copy.copy(self.plotProps)
        
    def SetAllPlotProperties(self, properties):
        self.plotProps = properties
        
    def GetPlotProperty(self, targetProperty):
        return self.plotProps[targetProperty]