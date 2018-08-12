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

import numpy as np

from VisualPIC.DataHandling.dataElement import DataElement


class SelfContainedDataElement(DataElement):
    def __init__(self, standard_name, data_values, data_units,
                 has_non_si_units, time_values, time_units, time_steps,
                 species_name=''):
        """Constructor
        Keyword arguments:
        standard_name -- standard VisualPIC name of the data.
        data_values -- a matrix containing all the data, where the columns are
            the particles and the rows are time steps. Data should be in the
            original units from the data file.
        data_units  -- string containing the data units.
        time_values -- a 1D array containing the time values on each time step.
            Same number of elements as rows in data_values. Data should be in
            the original units from the data file.
        time_units  -- string containing the time units.
        time_steps  -- a 1D array containing the number of each time step saved
            to disk during the simulation.
        """
        DataElement.__init__(self, standard_name, time_steps, species_name,
                             has_non_si_units)
        self.data_values = data_values
        self.data_units = data_units
        self.time_values = time_values
        self.time_units = time_units

    def get_data_original_units(self):
        return self.data_units

    def get_time_in_original_units(self, time_step):
        index = np.where(self.time_steps == time_step)[0][0]
        return self.time_values[index]
        
    def get_time_original_units(self):
        return self.time_units


class SelfContainedRawDataSet(SelfContainedDataElement):
    def __init__(self, standard_name, data_values, data_units,
                 has_non_si_units, time_values, time_units, time_steps,
                 species_name=''):
        return super().__init__(standard_name, data_values, data_units,
                                has_non_si_units, time_values, time_units,
                                time_steps, species_name)
    
    """
    Get data in original units
    """
    def get_data_in_original_units(self, time_step):
        index = np.where(self.time_steps == time_step)[0][0]
        rawValues = self.data_values[index] # migth contain NaN values
        dataMask = np.isfinite(rawValues)
        return rawValues[dataMask] # return the data without the NaN values
    
    """
    Get data in any units
    """
    def get_data_in_units(self, units, time_step):
        return self.unit_converter.get_data_in_units(
            self, units, self.get_data_in_original_units(time_step))

    """
    Get data in IS units
    """
    def get_data_in_si_units(self, time_step):
        return self.unit_converter.get_data_in_si_units(
            self, self.get_data_in_original_units(time_step))


class EvolutionData(SelfContainedDataElement):
    def __init__(self, standard_name, data_values, data_units,
                 has_non_si_units, time_values, time_units, time_steps,
                 species_name=''):
        return super().__init__(standard_name, data_values, data_units,
                                has_non_si_units, time_values, time_units,
                                time_steps, species_name)

    def get_all_data_in_original_units(self):
        return self.data_values

    def get_all_data_in_units(self, units):
        return self.unit_converter.get_data_in_units(self, units,
                                                     self.data_values)

    def get_all_time_in_original_units(self):
        return self.time_values

    def get_all_data_in_si_units(self):
        return self.unit_converter.get_data_in_si_units(
            self, self.get_all_data_in_original_units())
