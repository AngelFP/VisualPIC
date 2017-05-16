# -*- coding: utf-8 -*-

#Copyright 2016-2017 Angel Ferran Pousa, DESY
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


class FieldToPlot:
    def __init__(self, field, dataToPlotDimension, colorMapsCollection, isPartOfMultiplot = False):
        self.__field = field
        self.__dataToPlotDimension = dataToPlotDimension # dimension of the data we want to plot
        self.__fieldDimension = field.GetFieldDimension() # original dimension of the field, as simulated
        self.__colorMapsCollection = colorMapsCollection
        self.__isPartOfMultiplot = isPartOfMultiplot
        self.__fieldProperties = {
            "name":field.GetName(), 
            "speciesName":field.GetSpeciesName(),
            "timeSteps":field.GetTimeSteps(), 
            "fieldUnits":copy.copy(field.GetDataOriginalUnits()), 
            "originalFieldUnits":field.GetDataOriginalUnits(),
            "possibleFieldUnits":field.GetPossibleDataUnits(),
            "axesUnits":copy.copy(field.GetAxisOriginalUnits()), #dictionary
            "originalAxesUnits":field.GetAxisOriginalUnits(), 
            "possibleAxisUnits":field.GetPossibleAxisUnits(),
            "autoScale": True,
            "maxVal":1,
            "minVal":0,
            "possibleColorMaps":self.__GetPossibleColorMaps(),
            "cMap":"",
            "possiblePlotTypes":self.__GetPlotTypeOptions(),
            "plotType":""
        }
        self.__SetDefaultProperties()
        
    def __SetDefaultProperties(self):
        self.__SetDefaultColorMap()
        self.__SetDefaultPlotType()
            
    def __GetPossibleColorMaps(self):
        if self.__isPartOfMultiplot:
            return self.__colorMapsCollection.GetTransparentColorMapsNames()
        else:
            return self.__colorMapsCollection.GetSingleColorMapsNamesList()
        
    def __GetPlotTypeOptions(self):
        if self.__dataToPlotDimension == "2D":
            plotTypeOptions = ["Image", "Surface"]
        elif self.__dataToPlotDimension == "1D":
            plotTypeOptions = ["Line"]
        return plotTypeOptions  
            
    def __SetDefaultColorMap(self):
        if self.__isPartOfMultiplot:
            if self.__field.GetName() == "Normalized Vector Potential":
                colorMap = "Orange"
            else:
                colorMap = "Base gray"
        else:
            fieldISUnits = self.__field.GetDataISUnits()
            if fieldISUnits== "V/m" or fieldISUnits== "T":
                colorMap = "RdBu"
            elif fieldISUnits== "C/m^2":
                colorMap = "YlGnBu"
            else:
                colorMap = "jet"
        self.__fieldProperties["cMap"] = colorMap    
        
    def __SetDefaultPlotType(self):
        self.__fieldProperties["plotType"] = self.__fieldProperties["possiblePlotTypes"][0]
    
    def GetDataToPlotDimension(self):
        return self.__dataToPlotDimension
        
    def GetProperty(self, propertyName):
        return self.__fieldProperties[propertyName]

    def SetProperty(self, propertyName, value):
        self.__fieldProperties[propertyName] = value

    def GetFieldProperties(self):
        return self.__fieldProperties
        
    def SetFieldProperties(self, props):
        self.__fieldProperties = props

    def __GetAxisData(self, axis, timeStep):
        return self.__field.GetAxisInUnits( axis, self.GetProperty("axesUnits")[axis], timeStep)
            
    def __Get1DSlice(self, timeStep, slicePositionX, slicePositionY = None):
        # slice along the longitudinal axis
        # slicePosition has to be a double between 0 and 100
        #this gives the position in the transverse axis as a 
        fieldSlice = self.__field.Get1DSlice(timeStep, self.GetProperty("fieldUnits"), slicePositionX, slicePositionY) # Y data
        return self.__GetAxisData("x", timeStep), fieldSlice

    def __Get2DSlice(self, sliceAxis, slicePosition, timeStep):
        fieldSlice = self.__field.Get2DSlice(sliceAxis, slicePosition, timeStep, self.GetProperty("fieldUnits"))
        return self.__GetAxisData("x", timeStep),self.__GetAxisData("y", timeStep),fieldSlice

    def __Get2DField(self, timeStep):
        return self.__GetAxisData("x", timeStep),self.__GetAxisData("y", timeStep),self.__field.GetAllFieldData(timeStep, self.GetProperty("fieldUnits"))
    
    def GetData(self, timeStep):
        if self.__fieldDimension == "3D":
            if self.__dataToPlotDimension == "2D":
                return self.__Get2DSlice("z", 50, timeStep)
            elif self.__dataToPlotDimension == "1D":
                return self.__Get1DSlice(timeStep, 50, 50)
            else:
                raise NotImplementedError
        elif self.__fieldDimension == "2D":
            if self.__dataToPlotDimension == "2D":
                return self.__Get2DField(timeStep)
            elif self.__dataToPlotDimension == "1D":
                return self.__Get1DSlice(timeStep, 50)