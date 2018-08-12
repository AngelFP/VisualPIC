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


import math
import numpy as np


class GeneralUnitConverter(object):
    def __init__(self, simulation_params):
        # TODO: use scipy constants
        self.c = 299792458 #m/s
        self.e = 1.60217733 * 10**(-19) #C
        self.m_e = 9.1093897 * 10**(-31) #kg
        self.eps_0 = 8.854187817 * 10**(-12) #As/(Vm)
        self.normalization_factor = None
        self.set_simulation_parameters(simulation_params)

    def set_simulation_parameters(self, params):
        self.simulation_parameters = params

    """
    Possible units
    """
    def get_possible_data_units(self, data_element):
        data_si_units = self.get_data_si_units(data_element)
        original_units = list()
        all_other_units = list()
        original_units.append(data_element.get_data_original_units())
        all_other_units = self.get_all_other_data_units_options(data_si_units)
        all_units = list(set(list(set(original_units).union([
            data_si_units]))).union(all_other_units))
        return all_units

    def get_all_other_data_units_options(self, data_si_units):
        if data_si_units == "V/m":
            return ["V/m", "GV/m", "T"]
        if data_si_units == "V/m^2":
            return ["V/m^2", "GV/m^2", "T/m", "MT/m"]
        elif data_si_units == "T":
            return ["T", "V/m"]
        elif data_si_units == "C/m^2":
            return ["C/m^2"] #, "n/n_0"]
        elif data_si_units == "m":
            return ["m", "mm", "μm"]
        elif data_si_units == "kg*m/s":
            return ["kg*m/s", "MeV/c"]
        elif data_si_units == "J":
            return ["J", "MeV"]
        elif data_si_units == "rad":
            return ["rad", "mrad"]
        elif data_si_units == "s":
            return ["s", "fs"]
        else:
            return list()

    def get_possible_time_units(self, data_element):
        data_si_units = "s"
        original_units = list()
        all_other_units = list()
        original_units.append(data_element.get_time_original_units())
        all_other_units = self.get_all_other_time_units_options()
        all_units = list(set(original_units).union(all_other_units))
        return all_units

    def get_all_other_time_units_options(self):
        return ["s", "fs"]

    def get_possible_axis_units(self, data_element):
        original_units = list()
        all_other_units = list()
        all_other_units = self.get_all_other_axis_units_options()
        original_units.append(data_element.get_axis_original_units()["x"])
        all_units = list(set(original_units).union(all_other_units))
        return all_units

    def get_all_other_axis_units_options(self):
        return ["m", "mm", "μm"]

    """
    Unit conversion
    """
    def get_data_in_units(self, data_element, units, data):
        if units == data_element.get_data_original_units():
            return data
        elif units == self.get_data_si_units(data_element):
            return self.get_data_in_si_units(data_element, data)
        else:
            data_in_si_units = self.get_data_in_si_units(data_element, data)
            data_si_units = self.get_data_si_units(data_element)
            return self.make_conversion(units, data_si_units, data_in_si_units)

    def get_data_in_si_units(self, data_element, data):
        if not data_element.has_non_si_units:
            return data
        else:
            return self.convert_to_si_units(data_element, data)

    def make_conversion(self, units, data_si_units, data_in_si_units):
        if data_si_units == "V/m":
            if units == "GV/m":
                return data_in_si_units * 1e-9
            elif units == "T":
                return data_in_si_units / self.c
        elif data_si_units == "V/m^2":
            if units == "GV/m^2":
                return data_in_si_units * 1e-9
            elif units == "T/m":
                return data_in_si_units / self.c
            elif units == "MT/m":
                return data_in_si_units / self.c * 1e-6
        elif data_si_units == "C/m^2":
            pass
        elif data_si_units == "T":
            if units == "V/m":
                return data_in_si_units * self.c
        elif data_si_units == "m":
            if units == "μm":
                return data_in_si_units * 1e6
            elif units == "mm":
                return data_in_si_units * 1e3
        elif data_si_units == "kg*m/s":
            if units == "MeV/c":
                return data_in_si_units / self.e * self.c * 1e-6
        elif data_si_units == "J":
            if units == "MeV":
                return data_in_si_units / self.e * 1e-6
        elif data_si_units == "rad":
            if units == "mrad":
                return data_in_si_units * 1e3
        elif data_si_units == "s":
            if units == "fs":
                return data_in_si_units * 1e15

    def get_time_in_units(self, data_element, units, time_step):
        if data_element.has_non_si_units:
            if units == data_element.get_time_original_units():
                return data_element.get_time_in_original_units(time_step)
        if units == "s":
            return self.get_time_in_si_units(data_element, time_step)
        else:
            timeInISUnits = self.get_time_in_si_units(data_element, time_step)
            if units == "fs":
                return timeInISUnits * 1e15

    def get_axis_in_units(self, axis, data_element, units, time_step):
        if units == data_element.get_axis_original_units()[axis]:
                return data_element.get_axis_data_in_original_units(axis,
                                                                    time_step)
        if units == "m":
            return self.get_axis_in_si_units(axis, data_element, time_step)
        else:
            axisDataInISUnits = self.get_axis_in_si_units(axis, data_element,
                                                          time_step)
            if units == "μm":
                return axisDataInISUnits * 1e6
            elif units == "mm":
                return axisDataInISUnits * 1e3

    def get_data_si_units(self, data_element):
        """ Returns the IS units of the data (only the units, not the data!).
            The purpose of this is to identify"""
        if not data_element.has_non_si_units:
            return data_element.get_data_original_units()
        else:
            data_name = data_element.get_name()
            if data_name == "Ex" or data_name == "Ey" or data_name == "Ez":
                return "V/m"
            elif data_name == "Bx" or data_name == "By" or data_name == "Bz":
                return "T"
            elif data_name == "Charge density":
                return "C/m^2"
            elif data_name == "x" or data_name == "y" or data_name == "z":
                return "m"
            elif data_name == "Px" or data_name == "Py" or data_name == "Pz":
                return "kg*m/s"
            elif data_name == "Energy":
                return "J"
            elif data_name == "Charge":
                return "C"
            elif data_name == "Time":
                return "s"

    """
    To implement by children classes
    """
    def set_normalization_factor(self, value):
        raise NotImplementedError

    def get_axis_in_si_units(self, axis, data_element, time_step):
        raise NotImplementedError

    def get_time_in_si_units(self, data_element, time_step):
        raise NotImplementedError

    def get_grid_size_in_si_units(self, data_element):
        raise NotImplementedError

class OsirisUnitConverter(GeneralUnitConverter):
    def __init__(self, simulation_params):
        super(OsirisUnitConverter, self).__init__(simulation_params)

    def set_normalization_factor(self, value):
        """ In OSIRIS the normalization factor is the plasma density and it's
        given in units of 10^18 cm^-3 """
        self.normalization_factor = value * 1e24
        # plasma freq (1/s)
        self.w_p = math.sqrt(self.normalization_factor * (self.e)**2
                             / (self.m_e * self.eps_0)) 
        # skin depth (m)
        self.s_d = self.c / self.w_p
        # cold non-relativistic field in V/m
        self.E0 = self.c * self.m_e * self.w_p / self.e

    def set_simulation_parameters(self, params):
        super().set_simulation_parameters(params)
        self.set_normalization_factor(params["n_p"])

    def convert_to_si_units(self, data_element, data):
        data_name = data_element.get_name()
        if data_name == "Ex" or data_name == "Ey" or data_name == "Ez":
            return data*self.E0 # V/m
        elif data_name == "Bx" or data_name == "By" or data_name == "Bz":
            return data*self.E0/self.c # T
        elif data_name == "Charge density":
            return data * self.e * (self.w_p / self.c)**2 # C/m^2
        elif data_name == "x" or data_name == "y" or data_name == "z":
            return data*self.s_d # m
        elif data_name == "Px" or data_name == "Py" or data_name == "Pz":
            return data*self.m_e*self.c # kg*m/s
        elif data_name == "Energy":
            return data*self.m_e*self.c**2 # J
        elif data_name == "Charge":
            cell_size = self.get_cell_size_in_si_units(data_element)
            cell_vol = np.prod(cell_size)
            return data*self.e*cell_vol*self.normalization_factor # C
        elif data_name == "Time":
            return data/self.w_p # s

    def get_time_in_si_units(self, data_element, time_step):
        time = data_element.get_time_in_original_units(time_step)
        return time / self.w_p

    def get_axis_in_si_units(self, axis, data_element, time_step):
        axisData = data_element.get_axis_data_in_original_units(axis,
                                                                time_step)
        return axisData* self.c / self.w_p

    def get_cell_size_in_si_units(self, data_element):
        orig_size = data_element.get_simulation_cell_size_in_original_units()
        return orig_size * self.c / self.w_p


class HiPACEUnitConverter(GeneralUnitConverter):
    def __init__(self, simulation_params):
        super(HiPACEUnitConverter, self).__init__(simulation_params)

    def set_normalization_factor(self, value):
        """ In HiPACE the normalization factor is the plasma density and
        it's given in units of 10^18 cm^-3 """
        self.normalization_factor = value * 1e24
        # plasma freq (1/s)
        self.w_p = math.sqrt(self.normalization_factor * (self.e)**2
                             / (self.m_e * self.eps_0))
        # skin depth (m)
        self.s_d = self.c / self.w_p
        # cold non-relativistic field in V/m
        self.E0 = self.c * self.m_e * self.w_p / self.e

    def set_simulation_parameters(self, params):
        super().set_simulation_parameters(params)
        self.set_normalization_factor(params["n_p"])

    def convert_to_si_units(self, data_element):
        data_name = data_element.get_name()
        if data_name == "Ex" or data_name == "Ey" or data_name == "Ez":
            return data*self.E0 # V/m
        elif data_name == "Bx" or data_name == "By" or data_name == "Bz":
            return data*self.E0/self.c # T
        elif data_name == "Charge density":
            return data * self.e * (self.w_p / self.c)**2 # C/m^2
        elif data_name == "x" or data_name == "y" or data_name == "z":
            return data*self.s_d # m
        elif data_name == "Px" or data_name == "Py" or data_name == "Pz":
            return data*self.m_e*self.c # kg*m/s
        elif data_name == "Energy":
            return data*self.m_e*self.c**2 # J
        elif data_name == "Charge":
            return data*self.e # C
        elif data_name == "Time":
            return data/self.w_p # s

    def get_time_in_si_units(self, data_element, time_step):
        time = data_element.get_time_in_original_units(time_step)
        return time / self.w_p
    
    def get_axis_in_si_units(self, axis, data_element, time_step):
        axisData = data_element.get_axis_data_in_original_units(axis,
                                                                time_step)
        return axisData* self.c / self.w_p

    def get_grid_size_in_si_units(self, data_element):
        orig_size = data_element.get_simulation_cell_size_in_original_units()
        return orig_size * self.c / self.w_p


class OpenPMDUnitConverter(GeneralUnitConverter):
    def __init__(self, simulation_params):
        super(OpenPMDUnitConverter, self).__init__(simulation_params)

    def set_normalization_factor(self, value):
        # This function is kept for compatibility with VisualPIC
        # but is not needed for openPMD, since the data is returned in SI
        pass

    def set_simulation_parameters(self, params):
        super().set_simulation_parameters(params)
        self.set_normalization_factor(None)

    def convert_to_si_units(self, data_element, data):
        data_name = data_element.get_name()
        if data_name in ["x", "y", "z"]:
            return data * 1e-6
        elif data_name in ["Px", "Py", "Pz"]:
            return data * self.m_e * self.c # kg*m/s
        return data

    def get_time_in_si_units(self, data_element, time_step):
        time = data_element.get_time_in_original_units(time_step)
        return time

    def get_axis_in_si_units(self, axis, data_element, time_step):
        axisData = data_element.get_axis_data_in_original_units(axis,
                                                                time_step)
        return axisData


class UnitConverterSelector:
    unit_converters = {
        "Osiris": OsirisUnitConverter,
        "HiPACE": HiPACEUnitConverter,
        "openPMD": OpenPMDUnitConverter
        }
    @classmethod
    def get_unit_converter(cls, simulation_params):
        return cls.unit_converters[
            simulation_params["SimulationCode"]](simulation_params)
