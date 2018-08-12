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


from VisualPIC.DataReading.dataReader import DataReader


class DataElement(object):
    """Base class for all data elements (fields and rawDataSets)"""
    unit_converter = None

    @classmethod
    def set_unit_converter(cls, unit_converter):
        cls.unit_converter = unit_converter

    def __init__(self, standard_name, time_steps, species_name = "",
                 has_non_si_units = True):
        self.data_standard_name = standard_name
        self.species_name = species_name
        self.time_steps = time_steps # array of integers
        self.has_non_si_units = has_non_si_units
        
    def get_name(self):
        return self.data_standard_name

    def get_species_name(self):
        return self.species_name

    def get_time_steps(self):
        return self.time_steps

    def get_first_time_step(self):
        return self.time_steps[0]

    def get_simulation_cell_size_in_original_units(self):
        return self.data_reader.grid_size / self.data_reader.grid_resolution

    def get_simulation_cell_size_in_si_units(self):
        return self.unit_converter.get_cell_size_in_si_units(self)

    """
    Possible units
    """
    def get_possible_data_units(self):
        return self.unit_converter.get_possible_data_units(self)

    def get_data_si_units(self):
        return self.unit_converter.get_data_si_units(self)
    
    def get_possible_time_units(self):
        return self.unit_converter.get_possible_time_units(self)

    def get_time_original_units(self):
        raise NotImplementedError
        
    def get_data_original_units(self):
        raise NotImplementedError

    """
    Conversion of units
    """
    def get_axis_in_units(self, axis, units, time_step):
        return self.unit_converter.get_axis_in_units(axis, self, units,
                                                     time_step)

    def get_axis_in_si_units(self, axis, time_step):
        return self.unit_converter.get_axis_in_si_units(axis, self, time_step)

    def get_time_in_units(self, units, time_step):
        return self.unit_converter.get_time_in_units(self, units, time_step)

    def get_time_in_original_units(self, time_step):
        raise NotImplementedError
