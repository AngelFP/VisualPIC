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


class RawDataSetToPlot:
    def __init__(self, dataSet):
        self._dataSet = dataSet
        self._dataProperties = {
            "name":dataSet.get_name(), 
            "species_name":dataSet.get_species_name(), 
            "time_steps":dataSet.get_time_steps(),
            "dataSetUnits":dataSet.get_data_original_units(), 
            "timeUnits":dataSet.get_time_original_units(),
            "possibleDataSetUnits":dataSet.get_possible_data_units(),
            "possibleTimeUnits":dataSet.get_possible_time_units()
        }

    def get_time(self, time_step):
        return self._dataSet.get_time_in_units(self._dataProperties["timeUnits"], time_step)
        
    def GetDataSetPlotData(self, time_step):
        return self._dataSet.get_data_in_units(self._dataProperties["dataSetUnits"], time_step)
    
    def get_property(self, propertyName):
        return self._dataProperties[propertyName]

    def SetProperty(self, propertyName, value):
        self._dataProperties[propertyName] = value

    def GetDataProperties(self):
        return self._dataProperties
        
    def SetDataProperties(self, props):
        self._dataProperties = props