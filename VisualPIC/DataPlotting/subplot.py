# -*- coding: utf-8 -*-

#Copyright 2016-2017 Ángel Ferran Pousa
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
import numpy as np


class Subplot(object):
    def __init__(self, subplotPosition, colorMapsCollection, dataToPlot):
        self.subplotName = ""
        self.plottedSpeciesName = ""
        self.subplotPosition = subplotPosition
        self.colorMapsCollection = colorMapsCollection
        self.dataToPlot = dataToPlot
        self.possiblePlotTypes = list()
        self.dataType = ""
        self.axisProps = {"x":{},
                          "y":{},
                          "z":{}}
        self.axisTitleProps = {}
        self.colorbarProps = {}
        self.defaultFontSize = 10
        self._SetSubplotName()  
        self._SetPlottedSpeciesName()
        self._LoadPossiblePlotTypes()
        self._SetDefaultValues()
    
# Initialization    
    def _SetSubplotName(self):
        raise NotImplementedError
        
    def _SetPlottedSpeciesName(self):
        raise NotImplementedError   
                        
    def _LoadPossiblePlotTypes(self):
        raise NotImplementedError

    def _SetTimeSteps(self):
        raise NotImplementedError
            
    def _SetDefaultValues(self):
        self.LoadDefaultAxesValues()
        self.SetAxesToDefaultValues()
        
        self.LoadDefaultColorBarValues()
        self.SetColorbarToDefaultValues()
        
        self.LoadDefaultTitleValues()
        self.SetTitleToDefaultValues()
        
    def LoadDefaultAxesValues(self):
        self.SetAxisProperty("x", "DefaultLabelFontSize", self.defaultFontSize)
        self.SetAxisProperty("y", "DefaultLabelFontSize", self.defaultFontSize)
        self.SetAxisProperty("x", "DefaultAutoAxisLimits", True)
        self.SetAxisProperty("y", "DefaultAutoAxisLimits", True)
        self.SetAxisProperty("x", "DefaultAxisLimits", {"Min":0, "Max":1})
        self.SetAxisProperty("y", "DefaultAxisLimits", {"Min":0, "Max":1})

            
    def SetAxesToDefaultValues(self):
        self.SetAxisProperty("x", "LabelText", self.GetAxisProperty("x", "DefaultLabelText"))
        self.SetAxisProperty("y", "LabelText", self.GetAxisProperty("y", "DefaultLabelText"))
        self.SetAxisProperty("x", "AutoLabel", True)
        self.SetAxisProperty("y", "AutoLabel", True)
        self.SetAxisProperty("x", "Units", self.GetAxisProperty("x", "DefaultUnits"))
        self.SetAxisProperty("y", "Units", self.GetAxisProperty("y", "DefaultUnits"))
        self.SetAxisProperty("x", "LabelFontSize", self.GetAxisProperty("x", "DefaultLabelFontSize"))
        self.SetAxisProperty("y", "LabelFontSize", self.GetAxisProperty("y", "DefaultLabelFontSize"))
        self.SetAxisProperty("x", "AutoAxisLimits", self.GetAxisProperty("x", "DefaultAutoAxisLimits"))
        self.SetAxisProperty("y", "AutoAxisLimits", self.GetAxisProperty("y", "DefaultAutoAxisLimits"))
        self.SetAxisProperty("x", "AxisLimits", self.GetAxisProperty("x", "DefaultAxisLimits"))
        self.SetAxisProperty("y", "AxisLimits", self.GetAxisProperty("y", "DefaultAxisLimits"))
        if len(self.axisProps["z"])>0:
            self.SetAxisProperty("z", "LabelText", self.GetAxisProperty("z", "DefaultLabelText"))
            self.SetAxisProperty("z", "AutoLabel", True)
            self.SetAxisProperty("z", "Units", self.GetAxisProperty("z", "DefaultUnits"))
            self.SetAxisProperty("z", "LabelFontSize", self.GetAxisProperty("z", "DefaultLabelFontSize"))
            self.SetAxisProperty("z", "AutoAxisLimits", self.GetAxisProperty("z", "DefaultAutoAxisLimits"))
            self.SetAxisProperty("z", "AxisLimits", self.GetAxisProperty("z", "DefaultAxisLimits"))
            
    def LoadDefaultColorBarValues(self):
        self.colorbarProps["DefaultFontSize"] = 10
        self.colorbarProps["DefaultAutoTickLabelSpacing"] = True
        
    def SetColorbarToDefaultValues(self):
        self.colorbarProps["FontSize"] = self.colorbarProps["DefaultFontSize"]
        self.colorbarProps["AutoTickLabelSpacing"] = self.colorbarProps["DefaultAutoTickLabelSpacing"]
        
    def LoadDefaultTitleValues(self):
        self.SetTitleProperty("DefaultFontSize", 10)
        self.SetTitleProperty("DefaultText", self.subplotName)
        self.SetTitleProperty("DefaultAutoText", True)
        
    def SetTitleToDefaultValues(self):
        self.SetTitleProperty("FontSize", self.GetTitleProperty("DefaultFontSize"))
        self.SetTitleProperty("Text", self.GetTitleProperty("DefaultText"))
        self.SetTitleProperty("AutoText", self.GetTitleProperty("DefaultAutoText"))
        
# Interface methods
    def GetTimeSteps(self):
        return self._timeSteps
    
    def GetAxesUnitsOptions(self):
        raise NotImplementedError
            
    def GetAxesDimension(self):
        raise NotImplementedError
        
    def SetTitleProperty(self, targetProperty, value):
        self.axisTitleProps[targetProperty] = value
        
    def GetTitleProperty(self, targetProperty):
        return self.axisTitleProps[targetProperty]
        
    def SetAxisProperty(self, axis, targetPropery, value):
        self.axisProps[axis][targetPropery] = value
            
    def GetAxisProperty(self, axis, targetPropery):
        return self.axisProps[axis][targetPropery]
            
    def SetAllAxisProperties(self, axis, properties):
        self.axisProps[axis] = properties
            
    def GetCopyAllAxisProperties(self, axis):
        return copy.copy(self.axisProps[axis])
            
    def SetPosition(self, position):
        self.subplotPosition = position
        
    def GetPosition(self):
        return self.subplotPosition
            
    def GetPossiblePlotTypes(self):
        return self.possiblePlotTypes
                        
    def GetName(self):
        return self.subplotName
        
    def GetPlottedSpeciesName(self):
        return self.plottedSpeciesName
        
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

    def GetDataToPlot(self):
        return self.dataToPlot

    def GetDataType(self):
        return self.dataType


class FieldSubplot(Subplot):
    def __init__(self, subplotPosition, colorMapsCollection, dataToPlot):
        super(FieldSubplot, self).__init__(subplotPosition, colorMapsCollection, dataToPlot)
        self.dataType = "Field"
        self._SetTimeSteps()

    # Initialization    
    def _SetSubplotName(self):
        for fieldToPlot in self.dataToPlot:
            if self.subplotName == "":
                self.subplotName = fieldToPlot.GetProperty("name")
            elif self.subplotName != fieldToPlot.GetProperty("name"):
                self.subplotName = "Mult. fields"
        
    def _SetPlottedSpeciesName(self):
        for fieldToPlot in self.dataToPlot:
            if self.plottedSpeciesName == "":
                self.plottedSpeciesName = fieldToPlot.GetProperty("speciesName")
            elif self.plottedSpeciesName != fieldToPlot.GetProperty("speciesName"):
                self.plottedSpeciesName = "Mult. species"
                        
    def _LoadPossiblePlotTypes(self):
        self.possiblePlotTypes[:] = []
        if len(self.dataToPlot) > 1:
            self.possiblePlotTypes = ["Image"]
        else:
            self.possiblePlotTypes = ["Image", "Surface"]
        
    def LoadDefaultAxesValues(self):
        super().LoadDefaultAxesValues()
        self.SetAxisProperty("x", "DefaultLabelText", "z")
        self.SetAxisProperty("y", "DefaultLabelText", "y")
        #self.SetAxisProperty("z", "DefaultLabelText", "x")
        self.SetAxisProperty("x", "DefaultUnits", self.dataToPlot[0].GetProperty("axesUnits")["x"])
        self.SetAxisProperty("y", "DefaultUnits", self.dataToPlot[0].GetProperty("axesUnits")["y"])
        #self.SetAxisProperty("z", "DefaultUnits", self.dataToPlot[0].GetProperty("axesUnits")["z"])

    def _SetTimeSteps(self):
        i = 0
        for dataElementToPlot in self.dataToPlot:
            if i == 0:
                self._timeSteps = dataElementToPlot.GetProperty("timeSteps")
            else :
                self._timeSteps = np.intersect1d(self._timeSteps, dataElementToPlot.GetProperty("timeSteps"))

    # Interface methods
    def AddFieldToPlot(self, fieldToPlot):
        self.dataToPlot.append(fieldToPlot)
        self._SetSubplotName()
        self._SetPlottedSpeciesName()
        self._SetTimeSteps()
    
    def GetAxesUnitsOptions(self):
        unitsOptions = {}
        unitsOptions["x"] = self.dataToPlot[0].GetProperty("possibleAxisUnits")
        unitsOptions["y"] = self.dataToPlot[0].GetProperty("possibleAxisUnits")
        return unitsOptions
            
    def GetAxesDimension(self):
        ThreeDplotTypes = ["Surface", "Scatter3D"]
        for fieldToPlot in self.dataToPlot:
            if fieldToPlot.GetProperty("plotType") in ThreeDplotTypes:
                return "3D"
        return "2D"
        
    def GetFieldsToPlotWithDimension(self, dimension):
        fieldList = list()
        for fieldToPlot in self.dataToPlot:
            if fieldToPlot.GetDataToPlotDimension() == dimension:
                fieldList.append(fieldToPlot)
        return fieldList
        
    def RemoveField(self, index):
        del self.dataToPlot[index]


class RawDataSubplot(Subplot):
    def __init__(self, subplotPosition, colorMapsCollection, dataToPlot):
        self.plotProps = {"General":{}, "Histogram":{}, "Scatter":{}, "Arrows":{}}
        self.defaultPlotProps = {"General":{}, "Histogram":{}, "Scatter":{}, "Scatter3D":{}, "Arrows":{}}
        super(RawDataSubplot, self).__init__(subplotPosition, colorMapsCollection, dataToPlot)
        self.dataType = "Raw"
        self._SetTimeSteps()

    # Initialization    
    def _SetSubplotName(self):
        if len(self.dataToPlot) > 1:
            xName = self.dataToPlot["x"].GetProperty("name")
            yName = self.dataToPlot["y"].GetProperty("name")
            self.subplotName = xName + " vs " + yName
            if "z" in self.dataToPlot:
                zName = self.dataToPlot["z"].GetProperty("name")
                self.subplotName += " vs " + zName
        
    def _SetPlottedSpeciesName(self):
        if len(self.dataToPlot) > 1:
            xSpeciesName = self.dataToPlot["x"].GetProperty("speciesName")
            self.plottedSpeciesName = xSpeciesName
            ySpeciesName = self.dataToPlot["y"].GetProperty("speciesName")
            if ySpeciesName != self.plottedSpeciesName:
                self.plottedSpeciesName = "Mult. Species"
            if "z" in self.dataToPlot:
                zSpeciesName = self.dataToPlot["z"].GetProperty("speciesName")
                if zSpeciesName != self.plottedSpeciesName:
                    self.plottedSpeciesName = "Mult. Species"   
                        
    def _LoadPossiblePlotTypes(self):
        self.possiblePlotTypes[:] = []
        if "z" in self.dataToPlot:
            self.possiblePlotTypes = ["Scatter3D"]
        else:
            self.possiblePlotTypes = ["Histogram", "Scatter", "Arrows"]
    
    def _SetDefaultValues(self):
        super(RawDataSubplot, self)._SetDefaultValues()
        self.LoadDefaultPlotProperties()
        self.SetPlotPropertiesToDefault()

    def LoadDefaultAxesValues(self):
        super().LoadDefaultAxesValues()
        self.SetAxisProperty("x", "DefaultLabelText", self.dataToPlot["x"].GetProperty("name"))
        self.SetAxisProperty("y", "DefaultLabelText", self.dataToPlot["y"].GetProperty("name"))
        self.SetAxisProperty("x", "DefaultUnits", self.dataToPlot["x"].GetProperty("dataSetUnits"))
        self.SetAxisProperty("y", "DefaultUnits", self.dataToPlot["y"].GetProperty("dataSetUnits"))
        if "z" in self.dataToPlot:
            self.SetAxisProperty("z", "DefaultLabelText", self.dataToPlot["z"].GetProperty("name"))
            self.SetAxisProperty("z", "DefaultUnits", self.dataToPlot["z"].GetProperty("dataSetUnits"))
            self.SetAxisProperty("z", "DefaultLabelFontSize", self.defaultFontSize)
            self.SetAxisProperty("z", "DefaultAutoAxisLimits", True)
            self.SetAxisProperty("z", "DefaultAxisLimits", {"Min":0, "Max":1})

        
    def LoadDefaultPlotProperties(self):
        # General
        self.defaultPlotProps["General"]["PlotType"] = self.possiblePlotTypes[0]
        self.defaultPlotProps["General"]["PlotLimits"] = {"XMin":0, "XMax":1, "YMin":0, "YMax":1}
        self.defaultPlotProps["General"]["UseLimits"] = False
        self.defaultPlotProps["General"]["DisplayColorbar"] = True
        # Histogram
        self.defaultPlotProps["Histogram"]["Bins"] = {"XBins":100, "YBins":100}
        self.defaultPlotProps["Histogram"]["UseChargeWeighting"] = True
        if "weight" in self.dataToPlot:
            self.defaultPlotProps["Histogram"]["ChargeUnits"] = self.dataToPlot["weight"].GetProperty("dataSetUnits")
        self.defaultPlotProps["Histogram"]["CMap"] = self.GetAxisDefaultColorMap("Histogram")
        # Scatter
        self.defaultPlotProps["Scatter"]["UseChargeWeighting"] = True
        if "weight" in self.dataToPlot:
            self.defaultPlotProps["Scatter"]["ChargeUnits"] = self.dataToPlot["weight"].GetProperty("dataSetUnits")
        self.defaultPlotProps["Scatter"]["CMap"] = self.GetAxisDefaultColorMap("Scatter")
        # Scatter3D
        self.defaultPlotProps["Scatter3D"]["UseChargeWeighting"] = True
        if "weight" in self.dataToPlot:
            self.defaultPlotProps["Scatter3D"]["ChargeUnits"] = self.dataToPlot["weight"].GetProperty("dataSetUnits")
        self.defaultPlotProps["Scatter3D"]["CMap"] = self.GetAxisDefaultColorMap("Scatter3D")
        # Arrows
        self.defaultPlotProps["Arrows"]["MakeGrid"] = True
        self.defaultPlotProps["Arrows"]["Bins"] = {"XBins":100, "YBins":100}
        self.defaultPlotProps["Arrows"]["UseChargeWeighting"] = True
        if "Px" in self.dataToPlot:
            self.defaultPlotProps["Arrows"]["MomentumUnits"] = self.dataToPlot["Px"].GetProperty("dataSetUnits")
        self.defaultPlotProps["Arrows"]["NormalizationMode"] = "ToMaximum" # Options: "ToMaximum", "AllSameSize"
        self.defaultPlotProps["Arrows"]["ColorMode"] = "Momentum" # Options: "Momentum", "Uniform"
        self.defaultPlotProps["Arrows"]["CMap"] = self.GetAxisDefaultColorMap("Arrows")
            
    def SetPlotPropertiesToDefault(self):
        self.plotProps = copy.copy(self.defaultPlotProps)

    def _SetTimeSteps(self):
        self._timeSteps = self.dataToPlot["x"].GetProperty("timeSteps")
        
# Interface methods
    def AddDataToPlot(self, data, axis):
        # axis should be a string ("x", "y", "z" or "weight")
        self.dataToPlot[axis] = data
        self._SetSubplotName()
        self._SetPlottedSpeciesName()
        self._SetTimeSteps()

    def GetAxisColorMapOptions(self, plotType):
        if plotType == "Histogram" or plotType == "Arrows":
            return self.colorMapsCollection.GetAllColorMapNames()
        elif plotType == "Scatter" or plotType == "Scatter3D":
            return self.colorMapsCollection.GetAllColorMapNamesWithTransparency()
            
    def GetAxisDefaultColorMap(self, plotType):
        if plotType == "Histogram":
            return "BlueT"
        elif plotType == "Scatter":
            return "Uniform Blue Transparent"
        elif plotType == "Scatter3D":
            return "Uniform Blue Transparent"
        elif plotType == "Arrows":
            return "jet"
    
    def GetAxesUnitsOptions(self):
        unitsOptions = {}
        unitsOptions["x"] = self.dataToPlot["x"].GetProperty("possibleDataSetUnits")
        unitsOptions["y"] = self.dataToPlot["y"].GetProperty("possibleDataSetUnits")
        if "z" in self.dataToPlot:
            unitsOptions["z"] = self.dataToPlot["z"].GetProperty("possibleDataSetUnits")
        return unitsOptions
        
    def GetWeightingUnitsOptions(self):
        if "weight" in self.dataToPlot:
            return self.dataToPlot["weight"].GetProperty("possibleDataSetUnits")
        else:
            return list()

    def GetMomentumUnitsOptions(self):
        if "Px" in self.dataToPlot:
            return self.dataToPlot["Px"].GetProperty("possibleDataSetUnits")
        else:
            return list()

    def GetAxesDimension(self):
        ThreeDplotTypes = ["Surface", "Scatter3D"]
        if self.plotProps["General"]["PlotType"] in ThreeDplotTypes:
                return "3D"
        return "2D"
        
    def GetPlotType(self):
        return self.plotProps["General"]["PlotType"]

    def SetPlotType(self, plotType):
        self.plotProps["General"]["PlotType"] = plotType

    def GetCopyAllPlotProperties(self):
        return copy.copy(self.plotProps)
        
    def SetAllPlotProperties(self, properties):
        self.plotProps = properties
        
    def GetPlotProperty(self, propertyType, targetProperty):
        return self.plotProps[propertyType][targetProperty]

    def SetPlotProperty(self, propertzType, targetProperty, value):
        self.plotProps[propertzType][targetProperty] = value


class RawDataEvolutionSubplot(Subplot):
    def __init__(self, subplotPosition, colorMapsCollection, dataToPlot, speciesName):
        super(RawDataEvolutionSubplot, self).__init__(subplotPosition, colorMapsCollection, dataToPlot)
        self.dataType = "RawEvolution"
        self.plottedSpeciesName = speciesName

    def _SetSubplotName(self):
        if len(self.dataToPlot[0]) > 1:
            xName = self.dataToPlot[0]["x"].GetProperty("name")
            yName = self.dataToPlot[0]["y"].GetProperty("name")
            self.subplotName = xName + " vs " + yName
            if "z" in self.dataToPlot[0]:
                zName = self.dataToPlot[0]["z"].GetProperty("name")
                self.subplotName += " vs " + zName
        
    def _SetPlottedSpeciesName(self):
        pass

    def _LoadPossiblePlotTypes(self):
        pass

    def LoadDefaultAxesValues(self):
        super().LoadDefaultAxesValues()
        self.SetAxisProperty("x", "DefaultLabelText", self.dataToPlot[0]["x"].GetProperty("name"))
        self.SetAxisProperty("y", "DefaultLabelText", self.dataToPlot[0]["y"].GetProperty("name"))
        self.SetAxisProperty("x", "DefaultUnits", self.dataToPlot[0]["x"].GetProperty("dataSetUnits"))
        self.SetAxisProperty("y", "DefaultUnits", self.dataToPlot[0]["y"].GetProperty("dataSetUnits"))
        if "z" in self.dataToPlot[0]:
            self.SetAxisProperty("z", "DefaultLabelText", self.dataToPlot[0]["z"].GetProperty("name"))
            self.SetAxisProperty("z", "DefaultUnits", self.dataToPlot[0]["z"].GetProperty("dataSetUnits"))
            self.SetAxisProperty("z", "DefaultLabelFontSize", self.defaultFontSize)

    def GetAxesDimension(self):
        if "z" in self.dataToPlot[0]:
                return "3D"
        return "2D"

    def GetAxisColorMapOptions(self, plotType):
        return self.colorMapsCollection.GetAllColorMapNames()

    def RemoveParticle(self, index):
        del self.dataToPlot[index]