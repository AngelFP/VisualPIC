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
import numpy as np
import copy

class FieldToPlot:
    def __init__(self, field, dataToPlotDimension, unitConverter, colorMapsCollection, isPartOfMultiplot = False):
        self.__field = field
        self.__dataToPlotDimension = dataToPlotDimension # dimension of the data we want to plot
        self.__fieldDimension = field.GetFieldDimension() # original dimension of the field, as simulated
        self.__unitConverter = unitConverter
        self.__colorMapsCollection = colorMapsCollection
        self.__isPartOfMultiplot = isPartOfMultiplot
        self.__fieldProperties = {
            "name":field.GetName(), 
            "speciesName":field.GetSpeciesName(),
            "totalTimeSteps":field.GetTotalTimeSteps(), 
            "fieldUnits":field.GetDataUnits()[0], 
            "originalFieldUnits":copy.copy(field.GetDataUnits()[0]), 
            "possibleFieldUnits":self.__GetPossibleFieldUnits(),
            "axesUnits":field.GetDataUnits()[1], 
            "originalAxesUnits":copy.copy(field.GetDataUnits()[1]), 
            "possibleAxisUnits":self.__GetPossibleAxisUnits(),
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
               
    def __GetPossibleFieldUnits(self):
        return self.__unitConverter.getFieldUnitsOptions(self.__field)
                
    def __GetPossibleAxisUnits(self):
        return self.__unitConverter.getAxisUnitsOptions(self.__field)
            
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
            colorMap = "Base gray"
        else:
            name = self.__fieldProperties["name"]
            if "e1" in name or "e2" in name or "e3" in name or "b1" in name or "b2" in name or "b3" in name:
                colorMap = "RdBu"
            elif "charge" in name:
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
       
    def __GetAllData(self, timeStep):
        #returns fieldData, extent
        return self.__unitConverter.GetDataInUnits(timeStep, self.__field, self.GetProperty("fieldUnits"), self.GetProperty("axesUnits"), self.GetProperty("originalFieldUnits"), self.GetProperty("originalAxesUnits"))
            
    def __Get1DSlice(self, slicePosition, timeStep):
        # slice along the longitudinal axis
        # slicePosition has to be a double between 0 and 100
        #this gives the position in the transverse axis as a %
        plotData = self.__GetAllData(timeStep)
        fieldData = plotData[0]
        extent = plotData[1]
        xMin = extent[0]
        xMax = extent[1]
        elementsX = len(fieldData[0]) # number of elements in the longitudinal direction
        elementsY = len(fieldData) # number of elements in the transverse direction
        
        selectedRow = round(elementsY*(float(slicePosition)/100))
        fieldSlice = fieldData[selectedRow] # Y data
        
        X = np.linspace(xMin, xMax, elementsX) # X data
        
        return X, fieldSlice

    def __Get2DSlice(self, sliceAxis, slicePosition, timeStep):
        plotData = self.__GetAllData(timeStep)
        fieldData = plotData[0]
        extent = plotData[1]
        elementsX1 = len(fieldData[0][0]) # number of elements in the longitudinal direction
        elementsX2 = len(fieldData[0]) # number of elements in the transverse direction
        elementsX3 = len(fieldData) # number of elements in the transverse direction

        selectedRow = round(elementsX3*(float(slicePosition)/100))
        fieldSlice = fieldData[selectedRow]
        extent2D = extent[0:4]
        return fieldSlice, extent2D
    
    def GetData(self, timeStep):
        if self.__fieldDimension == "3D":
            if self.__dataToPlotDimension == "2D":
                return self.__Get2DSlice("x", 50, timeStep)
            else:
                raise NotImplementedError
        elif self.__fieldDimension == "2D":
            if self.__dataToPlotDimension == "2D":
                return self.__GetAllData(timeStep)
            elif self.__dataToPlotDimension == "1D":
                return self.__Get1DSlice(50, timeStep)