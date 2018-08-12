# -*- coding: utf-8 -*-

#Copyright 2016-2018 Angel Ferran Pousa, DESY
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
        self.__field_geometry = field.get_field_geometry() # original dimension of the field, as simulated
        self.__colorMapsCollection = colorMapsCollection
        self.__isPartOfMultiplot = isPartOfMultiplot
        self.__fieldProperties = {
            "name":field.get_name(), 
            "species_name":field.get_species_name(),
            "time_steps":field.get_time_steps(), 
            "fieldUnits":copy.copy(field.get_data_original_units()), 
            "originalFieldUnits":field.get_data_original_units(),
            "possibleFieldUnits":field.get_possible_data_units(),
            "axesUnits":copy.copy(field.get_axis_original_units()), #dictionary
            "originalAxesUnits":field.get_axis_original_units(), 
            "possibleAxisUnits":field.get_possible_axis_units(),
            "autoScale": True,
            "maxVal":1,
            "minVal":0,
            "possibleColorMaps":self.__GetPossibleColorMaps(),
            "cMap":"",
            "possiblePlotTypes":self.__get_plot_typeOptions(),
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
        
    def __get_plot_typeOptions(self):
        if self.__dataToPlotDimension == "2D":
            plotTypeOptions = ["Image", "Surface"]
        elif self.__dataToPlotDimension == "1D":
            plotTypeOptions = ["Line"]
        return plotTypeOptions  
            
    def __SetDefaultColorMap(self):
        if self.__isPartOfMultiplot:
            if self.__field.get_name() == "Normalized Vector Potential":
                colorMap = "Orange"
            else:
                colorMap = "Base gray"
        else:
            fieldISUnits = self.__field.get_data_si_units()
            if fieldISUnits== "V/m" or fieldISUnits== "T":
                colorMap = "RdBu"
            elif fieldISUnits== "C/m^2":
                colorMap = "YlGnBu"
            else:
                colorMap = "jet"
        self.__fieldProperties["cMap"] = colorMap    
        
    def __SetDefaultPlotType(self):
        self.__fieldProperties["plotType"] = self.__fieldProperties["possiblePlotTypes"][0]
    
    def get_data_to_plot_dimension(self):
        return self.__dataToPlotDimension
        
    def get_property(self, propertyName):
        return self.__fieldProperties[propertyName]

    def SetProperty(self, propertyName, value):
        self.__fieldProperties[propertyName] = value

    def GetFieldProperties(self):
        return self.__fieldProperties
        
    def SetFieldProperties(self, props):
        self.__fieldProperties = props

    def __get_axis_data(self, axis, time_step):
        return self.__field.get_axis_in_units( axis, self.get_property("axesUnits")[axis], time_step)
            
    def __get_1d_slice(self, time_step, slice_pos_x, slice_pos_y = None):
        # slice along the longitudinal axis
        # slice_pos has to be a double between 0 and 100
        #this gives the position in the transverse axis as a 
        fieldSlice = self.__field.get_1d_slice(time_step, self.get_property("fieldUnits"), slice_pos_x, slice_pos_y) # Y data
        return self.__get_axis_data("z", time_step), fieldSlice

    def __get_2d_slice(self, slice_axis, slice_pos, time_step):
        fieldSlice = self.__field.get_2d_slice(slice_axis, slice_pos, time_step, self.get_property("fieldUnits"))
        if self.__field_geometry == "thetaMode":
            transv_axis = "r"
        else:
            transv_axis = "x"
        return self.__get_axis_data("z", time_step),self.__get_axis_data(transv_axis, time_step),fieldSlice

    def __Get2DField(self, time_step):
        return self.__get_axis_data("z", time_step),self.__get_axis_data("x", time_step),self.__field.get_all_field_data(time_step, self.get_property("fieldUnits"))
    
    def get_data(self, time_step):
        if self.__field_geometry == "3D":
            if self.__dataToPlotDimension == "2D":
                return self.__get_2d_slice("z", 50, time_step)
            elif self.__dataToPlotDimension == "1D":
                return self.__get_1d_slice(time_step, 50, 50)
            else:
                raise NotImplementedError
        elif self.__field_geometry == "2D":
            if self.__dataToPlotDimension == "2D":
                return self.__Get2DField(time_step)
            elif self.__dataToPlotDimension == "1D":
                return self.__get_1d_slice(time_step, 50)
        elif self.__field_geometry == "thetaMode":
            if self.__dataToPlotDimension == "2D":
                return self.__get_2d_slice("z", 50, time_step)
            elif self.__dataToPlotDimension == "1D":
                return self.__get_1d_slice(time_step, 50, 50)