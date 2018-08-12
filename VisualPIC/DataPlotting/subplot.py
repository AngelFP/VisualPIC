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
import numpy as np


class Subplot(object):
    def __init__(self, subplot_position, cmaps_collection, data_to_plot):
        self.subplot_name = ""
        self.plotted_species_name = ""
        self.subplot_position = subplot_position
        self.cmaps_collection = cmaps_collection
        self.data_to_plot = data_to_plot
        self.possible_plot_types = list()
        self.data_type = ""
        self.axis_props = {"x":{},
                          "y":{},
                          "z":{}}
        self.axis_title_props = {}
        self.cbar_props = {}
        self.default_font_size = 10
        self.set_subplot_name()  
        self.set_plotted_species_name()
        self.load_possible_plot_types()
        self.set_default_values()
    
# Initialization    
    def set_subplot_name(self):
        raise NotImplementedError
        
    def set_plotted_species_name(self):
        raise NotImplementedError   
                        
    def load_possible_plot_types(self):
        raise NotImplementedError

    def set_time_steps(self):
        raise NotImplementedError
            
    def set_default_values(self):
        self.load_default_axes_values()
        self.set_axes_to_default_values()
        self.load_default_cbar_values()
        self.set_cbar_to_default_values()
        self.load_default_title_values()
        self.set_title_to_default_values()
        
    def load_default_axes_values(self):
        self.set_axis_property("x", "DefaultLabelFontSize",
                               self.default_font_size)
        self.set_axis_property("y", "DefaultLabelFontSize",
                               self.default_font_size)
        self.set_axis_property("x", "DefaultAutoAxisLimits", True)
        self.set_axis_property("y", "DefaultAutoAxisLimits", True)
        self.set_axis_property("x", "DefaultAxisLimits", {"Min":0, "Max":1})
        self.set_axis_property("y", "DefaultAxisLimits", {"Min":0, "Max":1})
            
    def set_axes_to_default_values(self):
        self.set_axis_property("x", "LabelText", self.get_axis_property(
            "x", "DefaultLabelText"))
        self.set_axis_property("y", "LabelText", self.get_axis_property(
            "y", "DefaultLabelText"))
        self.set_axis_property("x", "AutoLabel", True)
        self.set_axis_property("y", "AutoLabel", True)
        self.set_axis_property("x", "Units", self.get_axis_property(
            "x", "DefaultUnits"))
        self.set_axis_property("y", "Units", self.get_axis_property(
            "y", "DefaultUnits"))
        self.set_axis_property("x", "LabelFontSize", self.get_axis_property(
            "x", "DefaultLabelFontSize"))
        self.set_axis_property("y", "LabelFontSize", self.get_axis_property(
            "y", "DefaultLabelFontSize"))
        self.set_axis_property("x", "AutoAxisLimits", self.get_axis_property(
            "x", "DefaultAutoAxisLimits"))
        self.set_axis_property("y", "AutoAxisLimits", self.get_axis_property(
            "y", "DefaultAutoAxisLimits"))
        self.set_axis_property("x", "AxisLimits", self.get_axis_property(
            "x", "DefaultAxisLimits"))
        self.set_axis_property("y", "AxisLimits", self.get_axis_property(
            "y", "DefaultAxisLimits"))
        if len(self.axis_props["z"])>0:
            self.set_axis_property("z", "LabelText", self.get_axis_property(
                "z", "DefaultLabelText"))
            self.set_axis_property("z", "AutoLabel", True)
            self.set_axis_property("z", "Units", self.get_axis_property(
                "z", "DefaultUnits"))
            self.set_axis_property(
                "z", "LabelFontSize",
                self.get_axis_property("z", "DefaultLabelFontSize"))
            self.set_axis_property(
                "z", "AutoAxisLimits",
                self.get_axis_property("z", "DefaultAutoAxisLimits"))
            self.set_axis_property("z", "AxisLimits", self.get_axis_property(
                "z", "DefaultAxisLimits"))
            
    def load_default_cbar_values(self):
        self.cbar_props["DefaultFontSize"] = 10
        self.cbar_props["DefaultAutoTickLabelSpacing"] = True
        
    def set_cbar_to_default_values(self):
        self.cbar_props["FontSize"] = self.cbar_props["DefaultFontSize"]
        self.cbar_props["AutoTickLabelSpacing"] = self.cbar_props[
            "DefaultAutoTickLabelSpacing"]
        
    def load_default_title_values(self):
        self.set_title_property("DefaultFontSize", 10)
        self.set_title_property("DefaultText", self.subplot_name)
        self.set_title_property("DefaultAutoText", True)
        
    def set_title_to_default_values(self):
        self.set_title_property("FontSize",
                                self.get_title_property("DefaultFontSize"))
        self.set_title_property("Text",
                                self.get_title_property("DefaultText"))
        self.set_title_property("AutoText",
                                self.get_title_property("DefaultAutoText"))
        
# Interface methods
    def get_time_steps(self):
        return self._time_steps
    
    def get_axes_units_options(self):
        raise NotImplementedError
            
    def get_axes_dimension(self):
        raise NotImplementedError
        
    def set_title_property(self, target_property, value):
        self.axis_title_props[target_property] = value
        
    def get_title_property(self, target_property):
        return self.axis_title_props[target_property]
        
    def set_axis_property(self, axis, target_property, value):
        self.axis_props[axis][target_property] = value
            
    def get_axis_property(self, axis, target_property):
        return self.axis_props[axis][target_property]
            
    def set_all_axis_properties(self, axis, properties):
        self.axis_props[axis] = properties
            
    def get_copy_all_axis_properties(self, axis):
        return copy.copy(self.axis_props[axis])

    def get_copy_all_axes_properties(self):
        return copy.copy(self.axis_props)
            
    def set_position(self, position):
        self.subplot_position = position
        
    def get_position(self):
        return self.subplot_position
            
    def get_possible_plot_types(self):
        return self.possible_plot_types
                        
    def get_name(self):
        return self.subplot_name
        
    def get_plotted_species_name(self):
        return self.plotted_species_name
        
    def set_cbar_property(self, prop, value):
        self.cbar_props[prop] = value
    
    def get_cbar_property(self, prop):
        return self.cbar_props[prop]
    
    def get_copy_all_cbar_properties(self):
        return copy.copy(self.cbar_props)
        
    def set_all_cbar_properties(self, properties):
        self.cbar_props = properties
        
    def get_copy_all_title_properties(self):
        return copy.copy(self.axis_title_props)
        
    def set_all_title_properties(self, properties):
        self.axis_title_props = properties

    def get_data_to_plot(self):
        return self.data_to_plot

    def get_data_type(self):
        return self.data_type


class FieldSubplot(Subplot):
    def __init__(self, subplot_position, cmaps_collection, data_to_plot):
        super(FieldSubplot, self).__init__(subplot_position, cmaps_collection,
                                           data_to_plot)
        self.data_type = "Field"
        self.set_time_steps()

    # Initialization    
    def set_subplot_name(self):
        for field_to_plot in self.data_to_plot:
            if self.subplot_name == "":
                self.subplot_name = field_to_plot.get_property("name")
            elif self.subplot_name != field_to_plot.get_property("name"):
                self.subplot_name = "Mult. fields"
        
    def set_plotted_species_name(self):
        for field_to_plot in self.data_to_plot:
            if self.plotted_species_name == "":
                self.plotted_species_name = field_to_plot.get_property(
                    "species_name")
            elif self.plotted_species_name != field_to_plot.get_property(
                "species_name"):
                self.plotted_species_name = "Mult. species"
                        
    def load_possible_plot_types(self):
        self.possible_plot_types[:] = []
        if len(self.data_to_plot) > 1:
            self.possible_plot_types = ["Image"]
        else:
            self.possible_plot_types = ["Image", "Surface"]
        
    def load_default_axes_values(self):
        super().load_default_axes_values()
        self.set_axis_property("x", "DefaultLabelText", "z")
        self.set_axis_property("y", "DefaultLabelText", "x")
        #self.set_axis_property("z", "DefaultLabelText", "x")
        self.set_axis_property(
            "x", "DefaultUnits",
            self.data_to_plot[0].get_property("axesUnits")["z"])
        self.set_axis_property(
            "y", "DefaultUnits",
            self.data_to_plot[0].get_property("axesUnits")["x"])
        #self.set_axis_property(
        #    "z", "DefaultUnits",
        #    self.data_to_plot[0].get_property("axesUnits")["z"])

    def set_time_steps(self):
        i = 0
        for data_element_to_plot in self.data_to_plot:
            if i == 0:
                self._time_steps = data_element_to_plot.get_property(
                    "time_steps")
            else :
                self._time_steps = np.intersect1d(
                    self._time_steps, 
                    data_element_to_plot.get_property("time_steps"))

    # Interface methods
    def add_field_to_plot(self, field_to_plot):
        self.data_to_plot.append(field_to_plot)
        self.set_subplot_name()
        self.set_plotted_species_name()
        self.set_time_steps()
    
    def get_axes_units_options(self):
        unitsOptions = {}
        unitsOptions["x"] = self.data_to_plot[0].get_property(
            "possibleAxisUnits")
        unitsOptions["y"] = self.data_to_plot[0].get_property(
            "possibleAxisUnits")
        return unitsOptions
            
    def get_axes_dimension(self):
        ThreeDplotTypes = ["Surface", "Scatter3D"]
        for field_to_plot in self.data_to_plot:
            if field_to_plot.get_property("plotType") in ThreeDplotTypes:
                return "3D"
        return "2D"
        
    def get_fields_to_plot_with_dimension(self, dimension):
        fieldList = list()
        for field_to_plot in self.data_to_plot:
            if field_to_plot.get_data_to_plot_dimension() == dimension:
                fieldList.append(field_to_plot)
        return fieldList
        
    def remove_field(self, index):
        del self.data_to_plot[index]


class RawDataSubplot(Subplot):
    def __init__(self, subplot_position, cmaps_collection, data_to_plot):
        self.plot_props = {"General":{},
                           "Histogram":{},
                           "Scatter":{},
                           "Arrows":{}}
        self.default_plot_props = {"General":{},
                                   "Histogram":{},
                                   "Scatter":{},
                                   "Scatter3D":{},
                                   "Arrows":{}}
        super(RawDataSubplot, self).__init__(
            subplot_position, cmaps_collection, data_to_plot)
        self.data_type = "Raw"
        self.set_time_steps()

    # Initialization    
    def set_subplot_name(self):
        if len(self.data_to_plot) > 1:
            xName = self.data_to_plot["x"].get_property("name")
            yName = self.data_to_plot["y"].get_property("name")
            self.subplot_name = xName + " vs " + yName
            if "z" in self.data_to_plot:
                zName = self.data_to_plot["z"].get_property("name")
                self.subplot_name += " vs " + zName
        
    def set_plotted_species_name(self):
        if len(self.data_to_plot) > 1:
            xSpeciesName = self.data_to_plot["x"].get_property("species_name")
            self.plotted_species_name = xSpeciesName
            ySpeciesName = self.data_to_plot["y"].get_property("species_name")
            if ySpeciesName != self.plotted_species_name:
                self.plotted_species_name = "Mult. Species"
            if "z" in self.data_to_plot:
                zSpeciesName = self.data_to_plot["z"].get_property(
                    "species_name")
                if zSpeciesName != self.plotted_species_name:
                    self.plotted_species_name = "Mult. Species"   
                        
    def load_possible_plot_types(self):
        self.possible_plot_types[:] = []
        if "z" in self.data_to_plot:
            self.possible_plot_types = ["Scatter3D"]
        else:
            self.possible_plot_types = ["Histogram", "Scatter", "Arrows"]
    
    def set_default_values(self):
        super(RawDataSubplot, self).set_default_values()
        self.load_default_plot_properties()
        self.set_plot_properties_to_default()

    def load_default_axes_values(self):
        super().load_default_axes_values()
        self.set_axis_property(
            "x", "DefaultLabelText", 
            self.data_to_plot["x"].get_property("name"))
        self.set_axis_property(
            "y", "DefaultLabelText",
            self.data_to_plot["y"].get_property("name"))
        self.set_axis_property(
            "x", "DefaultUnits",
            self.data_to_plot["x"].get_property("dataSetUnits"))
        self.set_axis_property(
            "y", "DefaultUnits",
            self.data_to_plot["y"].get_property("dataSetUnits"))
        if "z" in self.data_to_plot:
            self.set_axis_property(
                "z", "DefaultLabelText",
                self.data_to_plot["z"].get_property("name"))
            self.set_axis_property(
                "z", "DefaultUnits",
                self.data_to_plot["z"].get_property("dataSetUnits"))
            self.set_axis_property(
                "z", "DefaultLabelFontSize", self.default_font_size)
            self.set_axis_property(
                "z", "DefaultAutoAxisLimits", True)
            self.set_axis_property(
                "z", "DefaultAxisLimits", {"Min":0, "Max":1})

        
    def load_default_plot_properties(self):
        # General
        self.default_plot_props[
            "General"]["PlotType"] = self.possible_plot_types[0]
        self.default_plot_props[
            "General"]["PlotLimits"] = {"XMin":0, "XMax":1, "YMin":0, "YMax":1}
        self.default_plot_props["General"]["UseLimits"] = False
        self.default_plot_props["General"]["DisplayColorbar"] = True
        # Histogram
        self.default_plot_props["Histogram"]["Bins"] = {"XBins":100,
                                                        "YBins":100}
        self.default_plot_props["Histogram"]["UseChargeWeighting"] = True
        if "weight" in self.data_to_plot:
            self.default_plot_props["Histogram"]["ChargeUnits"] = (
                self.data_to_plot["weight"].get_property("dataSetUnits"))
        self.default_plot_props[
            "Histogram"]["CMap"] = self.get_axis_default_cmap("Histogram")
        # Scatter
        self.default_plot_props["Scatter"]["UseChargeWeighting"] = True
        if "weight" in self.data_to_plot:
            self.default_plot_props["Scatter"]["ChargeUnits"] = (
                self.data_to_plot["weight"].get_property("dataSetUnits"))
        self.default_plot_props[
            "Scatter"]["CMap"] = self.get_axis_default_cmap("Scatter")
        # Scatter3D
        self.default_plot_props["Scatter3D"]["UseChargeWeighting"] = True
        if "weight" in self.data_to_plot:
            self.default_plot_props["Scatter3D"]["ChargeUnits"] = (
                self.data_to_plot["weight"].get_property("dataSetUnits"))
        self.default_plot_props[
            "Scatter3D"]["CMap"] = self.get_axis_default_cmap("Scatter3D")
        # Arrows
        self.default_plot_props["Arrows"]["MakeGrid"] = True
        self.default_plot_props["Arrows"]["Bins"] = {"XBins":100, "YBins":100}
        self.default_plot_props["Arrows"]["UseChargeWeighting"] = True
        if "Px" in self.data_to_plot:
            self.default_plot_props["Arrows"]["MomentumUnits"] = (
                self.data_to_plot["Px"].get_property("dataSetUnits"))
        # Options: "ToMaximum", "AllSameSize"
        self.default_plot_props["Arrows"]["NormalizationMode"] = "ToMaximum"
        # Options: "Momentum", "Uniform"
        self.default_plot_props["Arrows"]["ColorMode"] = "Momentum"
        self.default_plot_props[
            "Arrows"]["CMap"] = self.get_axis_default_cmap("Arrows")
            
    def set_plot_properties_to_default(self):
        self.plot_props = copy.copy(self.default_plot_props)

    def set_time_steps(self):
        self._time_steps = self.data_to_plot["x"].get_property("time_steps")
        
# Interface methods
    def add_data_to_plot(self, data, axis):
        # axis should be a string ("x", "y", "z" or "weight")
        self.data_to_plot[axis] = data
        self.set_subplot_name()
        self.set_plotted_species_name()
        self.set_time_steps()

    def get_axis_cmap_options(self, plotType):
        if plotType == "Histogram" or plotType == "Arrows":
            return self.cmaps_collection.get_all_cmap_names()
        elif plotType == "Scatter" or plotType == "Scatter3D":
            return self.cmaps_collection.get_all_cmap_names_with_tansparency()
            
    def get_axis_default_cmap(self, plotType):
        if plotType == "Histogram":
            return "BlueT"
        elif plotType == "Scatter":
            return "Uniform Blue Transparent"
        elif plotType == "Scatter3D":
            return "Uniform Blue Transparent"
        elif plotType == "Arrows":
            return "jet"
    
    def get_axes_units_options(self):
        unitsOptions = {}
        unitsOptions["x"] = self.data_to_plot["x"].get_property(
            "possibleDataSetUnits")
        unitsOptions["y"] = self.data_to_plot["y"].get_property(
            "possibleDataSetUnits")
        if "z" in self.data_to_plot:
            unitsOptions["z"] = self.data_to_plot["z"].get_property(
                "possibleDataSetUnits")
        return unitsOptions
        
    def get_weighting_units_options(self):
        if "weight" in self.data_to_plot:
            return self.data_to_plot["weight"].get_property(
                "possibleDataSetUnits")
        else:
            return list()

    def get_momentum_units_options(self):
        if "Px" in self.data_to_plot:
            return self.data_to_plot["Px"].get_property("possibleDataSetUnits")
        else:
            return list()

    def get_axes_dimension(self):
        ThreeDplotTypes = ["Surface", "Scatter3D"]
        if self.plot_props["General"]["PlotType"] in ThreeDplotTypes:
                return "3D"
        return "2D"
        
    def get_plot_type(self):
        return self.plot_props["General"]["PlotType"]

    def set_plot_type(self, plotType):
        self.plot_props["General"]["PlotType"] = plotType

    def get_copy_all_plot_properties(self):
        return copy.copy(self.plot_props)
        
    def set_all_plot_properties(self, properties):
        self.plot_props = properties
        
    def get_plot_property(self, property_type, target_property):
        return self.plot_props[property_type][target_property]

    def set_plot_property(self, property_type, target_property, value):
        self.plot_props[property_type][target_property] = value


class RawDataEvolutionSubplot(Subplot):
    def __init__(self, subplot_position, cmaps_collection, data_to_plot,
                 species_name):
        super(RawDataEvolutionSubplot, self).__init__(subplot_position,
                                                      cmaps_collection,
                                                      data_to_plot)
        self.data_type = "RawEvolution"
        self.plotted_species_name = species_name

    def set_subplot_name(self):
        if len(self.data_to_plot[0]) > 1:
            xName = self.data_to_plot[0]["x"].get_property("name")
            yName = self.data_to_plot[0]["y"].get_property("name")
            self.subplot_name = xName + " vs " + yName
            if "z" in self.data_to_plot[0]:
                zName = self.data_to_plot[0]["z"].get_property("name")
                self.subplot_name += " vs " + zName
        
    def set_plotted_species_name(self):
        pass

    def load_possible_plot_types(self):
        pass

    def load_default_axes_values(self):
        super().load_default_axes_values()
        self.set_axis_property(
            "x", "DefaultLabelText",
            self.data_to_plot[0]["x"].get_property("name"))
        self.set_axis_property(
            "y", "DefaultLabelText",
            self.data_to_plot[0]["y"].get_property("name"))
        self.set_axis_property(
            "x", "DefaultUnits",
            self.data_to_plot[0]["x"].get_property("dataSetUnits"))
        self.set_axis_property(
            "y", "DefaultUnits",
            self.data_to_plot[0]["y"].get_property("dataSetUnits"))
        if "z" in self.data_to_plot[0]:
            self.set_axis_property("z", "DefaultAutoAxisLimits", True)
            self.set_axis_property(
                "z", "DefaultAxisLimits", {"Min":0, "Max":1})
            self.set_axis_property(
                "z", "DefaultLabelText",
                self.data_to_plot[0]["z"].get_property("name"))
            self.set_axis_property(
                "z", "DefaultUnits",
                self.data_to_plot[0]["z"].get_property("dataSetUnits"))
            self.set_axis_property(
                "z", "DefaultLabelFontSize", self.default_font_size)

    def get_axes_dimension(self):
        if "z" in self.data_to_plot[0]:
                return "3D"
        return "2D"

    def get_axes_units_options(self):
        unitsOptions = {}
        unitsOptions["x"] = self.data_to_plot[0]["x"].get_property(
            "possibleDataSetUnits")
        unitsOptions["y"] = self.data_to_plot[0]["y"].get_property(
            "possibleDataSetUnits")
        if "z" in self.data_to_plot:
            unitsOptions["z"] = self.data_to_plot[0]["z"].get_property(
                "possibleDataSetUnits")
        return unitsOptions

    def get_axis_cmap_options(self, plotType):
        return self.cmaps_collection.get_all_cmap_names()

    def remove_particle(self, index):
        del self.data_to_plot[index]