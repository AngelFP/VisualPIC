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
            "timeSteps":field.GetTimeSteps(), 
            "fieldUnits":copy.copy(field.GetDataUnits()), 
            "originalFieldUnits":field.GetDataUnits(), 
            "possibleFieldUnits":self.__GetPossibleFieldUnits(),
            "axesUnits":copy.copy(field.GetAxisUnits()), #dictionary
            "originalAxesUnits":field.GetAxisUnits(), 
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
        return self.__unitConverter.GetPossibleDataUnits(self.__field)
                
    def __GetPossibleAxisUnits(self):
        return self.__unitConverter.GetPossibleAxisUnits(self.__field)
            
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
            fieldISUnits = self.__unitConverter.GetDataISUnits(self.__field)
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
       
    def __GetAllData(self, timeStep):
        #returns fieldData, extent
        return self.__unitConverter.GetDataInUnits(self.__field, self.GetProperty("fieldUnits"), timeStep)

    def __GetAxisData(self, axis, timeStep):
        return self.__unitConverter.GetAxisInUnits( axis, self.__field, self.GetProperty("axesUnits")[axis], timeStep)
            
    def __Get1DSlice(self, slicePosition, timeStep):
        # slice along the longitudinal axis
        # slicePosition has to be a double between 0 and 100
        #this gives the position in the transverse axis as a %
        fieldData = self.__GetAllData(timeStep)
        matrixSize = fieldData.shape
        elementsY = matrixSize[-2]
        selectedRow = round(elementsY*(float(slicePosition)/100))
        fieldSlice = fieldData[selectedRow] # Y data
        
        return self.__GetAxisData("x", timeStep), fieldSlice

    def __Get2DSlice(self, sliceAxis, slicePosition, timeStep):
        fieldData = self.__GetAllData(timeStep)
        matrixSize = self.fieldData.shape
        elementsX1 = matrixSize[-1] # number of elements in the longitudinal direction
        elementsX2 = matrixSize[-2] # number of elements in the transverse direction
        elementsX3 = matrixSize[-3] # number of elements in the transverse direction
        selectedRow = round(elementsX3*(float(slicePosition)/100))
        fieldSlice = fieldData[selectedRow]
        return self.__GetAxisData("x", timeStep),self.__GetAxisData("y", timeStep),fieldSlice

    def __Get2DField(self, timeStep):
        return self.__GetAxisData("x", timeStep),self.__GetAxisData("y", timeStep),self.__GetAllData(timeStep)
    
    def GetData(self, timeStep):
        if self.__fieldDimension == "3D":
            if self.__dataToPlotDimension == "2D":
                return self.__Get2DSlice("z", 50, timeStep)
            else:
                raise NotImplementedError
        elif self.__fieldDimension == "2D":
            if self.__dataToPlotDimension == "2D":
                return self.__Get2DField(timeStep)
            elif self.__dataToPlotDimension == "1D":
                return self.__Get1DSlice(50, timeStep)