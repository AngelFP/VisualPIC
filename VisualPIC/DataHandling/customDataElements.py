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
from scipy import interpolate as ip
from scipy.constants import c, e, m_e, epsilon_0
import math

from VisualPIC.DataHandling.dataElement import DataElement


"""
Base Class for Custom Fields and Raw Data Sets
"""
class CustomDataElement(DataElement):
    # List of necessary fields and simulation parameters.
    necessary_data = {"2D": [],
                      "3D": [],
                      "thetaMode": []}
    necessary_parameters = []
    units = ""
    si_units = True
    standard_name = ""

    def __init__(self, data_container, species_name = ''):
        self.data_container = data_container
        self.data_standard_name = self.standard_name
        self.species_name = species_name
        self.has_non_si_units = not self.si_units
        self.set_base_data()
        self.set_time_steps()

    def set_time_steps(self):
        i = 0
        for data_name, data_element in self.data.items():
            if i == 0:
                time_steps = data_element.get_time_steps()
            else:
                time_steps = np.intersect1d(
                    time_steps, data_element.get_time_steps())
        self.time_steps = time_steps

    def set_base_data(self):
        raise NotImplementedError

    def get_data_original_units(self):
        return self.units

    def get_time_in_original_units(self, time_step):
        return list(self.data.items())[0][1].get_time_in_original_units(
            time_step)

    def get_time_original_units(self):
        return list(self.data.items())[0][1].get_time_original_units()


"""
Custom Fields
"""
class CustomField(CustomDataElement):
    @classmethod
    def meets_requirements(cls, data_container):
        "Checks whether the required data and parameters are available"
        if data_container.get_simulation_geometry() in cls.necessary_data:
            # check data requirements
            data_requirements_met = set(
                data_container.get_available_domain_fields_names()).issuperset(
                    cls.necessary_data[
                        data_container.get_simulation_geometry()])
            # check parameter requirements
            parameter_requirements_met = set(
                data_container.get_names_of_available_parameters()).issuperset(
                    cls.necessary_parameters)
            return data_requirements_met and parameter_requirements_met
        else:
            return False

    def set_base_data(self):
        geometry = self.data_container.get_simulation_geometry()
        self.data = {}
        for field_name in self.necessary_data[geometry]:
            self.data[field_name] = self.data_container.get_domain_field(
                field_name)

    def get_field_geometry(self):
        return list(self.data.items())[0][1].get_field_geometry()

    def get_possible_axis_units(self):
        return self.unit_converter.get_possible_axis_units(self)

    def get_axis_data_in_original_units(self, axis, time_step):
        return list(self.data.items())[0][1].get_axis_data_in_original_units(
            axis, time_step)
        
    def get_axis_original_units(self):
        return list(self.data.items())[0][1].get_axis_original_units()

    """
    Get data in original units
    """
    def get_1d_slice_in_original_units(self, time_step, slice_pos_x,
                                  slice_pos_y = None):
        field_data = self.calculate_field(time_step)
        if self.get_field_geometry() == '2D':
            elements_x = field_data.shape[-2]
            selected_row = round(elements_x*(float(slice_pos_x)/100))
            slice_data = field_data[selected_row]
        elif self.get_field_geometry() == '3D':
            elements_x = field_data.shape[-3]
            elements_y = field_data.shape[-2]
            selected_x = round(elements_x*(float(slice_pos_x)/100))
            selected_y = round(elements_y*(float(slice_pos_y)/100))
            slice_data = field_data[selected_x, selected_y]
        return slice_data

    def get_2d_slice_in_original_units(self, slice_axis, slice_pos, time_step):
        field_data = self.calculate_field(time_step)
        elements_x3 = field_data.shape[-3]
        selected_row = round(elements_x3*(float(slice_pos)/100))
        slice_data = field_data[selected_row]
        return slice_data

    def get_all_field_data_in_original_units(self, time_step):
        return self.calculate_field(time_step)

    def get_3d_field_from_2d_slice_in_original_units(self, time_step, transvEl,
                                                     longEl, fraction):
        """
        fraction: used to define the range of data we want to visualize in the 
        transverse direction.
            - fraction = 1 -> get all the data
            - fraction = 0.5 -> get only from x=0 to x=x_max*0.5
        """
        field_2d = self.get_all_field_data_in_original_units(time_step)
        nx = field_2d.shape[0]
        # we get only half of the field data
        field_2d = field_2d[int(nx/2):int(nx/2+nx/2*fraction)]
        cilShape = field_2d.shape
        # cyl. coordinates of original data
        Rin,Zin = np.mgrid[0:cilShape[0], 0:cilShape[1]] 
        Zin = np.reshape(Zin, Zin.shape[0]*Zin.shape[1])
        Rin = np.reshape(Rin, Rin.shape[0]*Rin.shape[1])
        field_2d = np.reshape(field_2d, field_2d.shape[0]*field_2d.shape[1])
        transv_sp = cilShape[0]*2/transvEl
        lon_sp = cilShape[1]/longEl
        field3D = np.zeros((transvEl, transvEl, longEl))
        # cart. coordinates of 3D field
        X, Y, Z = np.mgrid[0:cilShape[0]:transv_sp,
                           0:cilShape[0]:transv_sp,
                           0:cilShape[1]:lon_sp] 
        Rout = np.sqrt(X**2 + Y**2)
        # Fill the field sector by sector
        # (only the first has to be calculated. The rest are simlpy mirrored)
        # Start with top right section (when looking back from z to the
        # x-y plane).
        field3D[int(transvEl/2):transvEl + 1, int(transvEl/2):transvEl + 1] = (
            ip.griddata(np.column_stack((Rin,Zin)),
                        field_2d,
                        (Rout, Z),
                        method='nearest',
                        fill_value = 0))
        # Now perform the mirroring
        field3D[0:int(transvEl/2), int(transvEl/2):transvEl + 1] = (
            np.flip(field3D[int(transvEl/2):transvEl + 1,
                            int(transvEl/2):transvEl + 1],0))
        field3D[0:int(transvEl/2), 0:int(transvEl/2)] = (
            np.flip(field3D[0:int(transvEl/2),
                            int(transvEl/2):transvEl + 1], 1))
        field3D[int(transvEl/2):transvEl + 1, 0:int(transvEl/2)] = (
            np.flip(field3D[int(transvEl/2):transvEl + 1,
                            int(transvEl/2):transvEl+1], 1))
        return field3D
    
    """
    Get data in any units
    """
    def get_1d_slice(self, time_step, units, slice_pos_x,
                   slice_pos_y = None):
        field_data = self.calculate_field(time_step)
        if self.get_field_geometry() in ['2D', 'thetaMode']:
            elements_x = field_data.shape[-2]
            selected_row = round(elements_x*(float(slice_pos_x)/100))
            slice_data = field_data[selected_row]
        elif self.get_field_geometry() == '3D':
            elements_x = field_data.shape[-3]
            elements_y = field_data.shape[-2]
            selected_x = round(elements_x*(float(slice_pos_x)/100))
            selected_y = round(elements_y*(float(slice_pos_y)/100))
            slice_data = field_data[selected_x, selected_y]
        return self.unit_converter.get_data_in_units(self, units, slice_data)

    def get_2d_slice(self, slice_axis, slice_pos, time_step, units):
        field_data = self.calculate_field(time_step)
        if self.get_field_geometry() == "thetaMode":
            slice_data = field_data
        else:
            elements_x3 = field_data.shape[-3]
            selected_row = round(elements_x3*(float(slice_pos)/100))
            slice_data = field_data[selected_row]
        return self.unit_converter.get_data_in_units(self, units, slice_data)

    def get_all_field_data(self, time_step, units):
        field_data = self.calculate_field(time_step)
        return self.unit_converter.get_data_in_units(self, units, field_data)

    """
    Get data in IS units
    """
    def get_1d_slice_si_units(self, time_step, slice_pos_x,
                          slice_pos_y = None):
        field_data = self.calculate_field(time_step)
        if self.get_field_geometry() == '2D':
            elements_x = field_data.shape[-2]
            selected_row = round(elements_x*(float(slice_pos_x)/100))
            slice_data = field_data[selected_row]
        elif self.get_field_geometry() == '3D':
            elements_x = field_data.shape[-3]
            elements_y = field_data.shape[-2]
            selected_x = round(elements_x*(float(slice_pos_x)/100))
            selected_y = round(elements_y*(float(slice_pos_y)/100))
            slice_data = field_data[selected_x, selected_y]
        return self.unit_converter.get_data_in_si_units(self, slice_data)

    def get_2d_slice_si_units(self, slice_axis, slice_pos, time_step):
        field_data = self.calculate_field(time_step)
        elements_x3 = field_data.shape[-3]
        selected_row = round(elements_x3*(float(slice_pos)/100))
        slice_data = field_data[selected_row]
        return self.unit_converter.get_data_in_si_units(self, slice_data)

    def get_all_field_data_si_units(self, time_step):
        field_data = self.calculate_field(time_step)
        return self.unit_converter.get_data_in_si_units(self, field_data)

    def calculate_field(self, time_step):
        raise NotImplementedError


class TransverseWakefieldX(CustomField):
    # List of necessary fields and simulation parameters.
    necessary_data = {"2D": ["Ex", "By"],
                     "3D": ["Ex", "By"],
                     "thetaMode": ["Ex", "By"]}
    necessary_parameters = []
    units = "V/m"
    si_units = True
    standard_name = "Wx"

    def calculate_field(self, time_step):
        Ex = self.data["Ex"].get_all_field_data_si_units(time_step)
        By = self.data["By"].get_all_field_data_si_units(time_step)
        Wx = Ex - c*By
        return Wx


class TransverseWakefieldY(CustomField):
    # List of necessary fields and simulation parameters.
    necessary_data = {"2D": ["Ey", "Bx"],
                     "3D": ["Ey", "Bx"],
                     "thetaMode": ["Ey", "Bx"]}
    necessary_parameters = []
    units = "V/m"
    si_units = True
    standard_name = "Wy"

    def calculate_field(self, time_step):
        Ey = self.data["Ey"].get_all_field_data_si_units(time_step)
        Bx = self.data["Bx"].get_all_field_data_si_units(time_step)
        Wy = Ey + c*Bx
        return Wy


class LaserIntensityField(CustomField):
    # TODO: Implement correcly in 2D 
    # (information about polarization plane is required).
    necessary_data = {"2D": ["Ex", "Ez"],
                     "3D": ["Ex", "Ey", "Ez"],
                     "thetaMode": ["Er", "Ez"]}
    necessary_parameters = []
    units = "W/m^2"
    si_units = True
    standard_name = "I"

    def calculate_field(self, time_step):
        if self.get_field_geometry() == 'thetaMode':
            Er = self.data["Er"].get_all_field_data_si_units(time_step)
            Ez = self.data["Ez"].get_all_field_data_si_units(time_step)
            E2 = np.square(Ez) + np.square(Er)
        else:
            Ex = self.data["Ex"].get_all_field_data_si_units(time_step)
            Ez = self.data["Ez"].get_all_field_data_si_units(time_step)
            if self.get_field_geometry() == '3D':
                Ey = self.data["Ey"].get_all_field_data_si_units(time_step)
                E2 = np.square(Ez) + np.square(Ey) + np.square(Ex)
            if self.get_field_geometry() == '2D':
                E2 = np.square(Ez) + np.square(Ex)
        # Assume index of refraction equal to 1
        intensity = c*epsilon_0/2*E2 
        return intensity


class NormalizedVectorPotential(CustomField):
    necessary_data = {"2D": ["Ex", "Ez"],
                     "3D": ["Ex", "Ey", "Ez"],
                     "thetaMode": ["Er", "Ez"]}
    necessary_parameters = ["n_p", "lambda_l"]
    units = "m_e*c^2/e"
    si_units = True
    standard_name = "a"

    def calculate_field(self, time_step):
        if self.get_field_geometry() == 'thetaMode':
            Er = self.data["Er"].get_all_field_data_si_units(time_step)
            Ez = self.data["Ez"].get_all_field_data_si_units(time_step)
            E2 = np.square(Ez) + np.square(Er)
        else:
            Ex = self.data["Ex"].get_all_field_data_si_units(time_step)
            Ez = self.data["Ez"].get_all_field_data_si_units(time_step)
            if self.get_field_geometry() == '3D':
                Ey = self.data["Ey"].get_all_field_data_si_units(time_step)
                E2 = np.square(Ez) + np.square(Ey) + np.square(Ex)
            if self.get_field_geometry() == '2D':
                E2 = np.square(Ez) + np.square(Ex)
        # Assume index of refraction equal to 1
        intensity = c*epsilon_0/2*E2 
        # laser wavelength (m)
        l = self.data_container.get_simulation_parameter("lambda_l") * 1e-9
        # normalized vector potential
        a = np.sqrt(7.3e-11 * l**2 * intensity) 
        return a


class TransverseWakefieldSlopeX(CustomField):
    # List of necessary fields and simulation parameters.
    necessary_data = {"2D": ["Ex", "By"],
                     "3D": ["Ex", "By"],
                     "thetaMode": ["Ex", "By"]}
    necessary_parameters = []
    units = "V/m^2"
    si_units = True
    standard_name = "dx Wx"

    def calculate_field(self, time_step):
        Ex = self.data["Ex"].get_all_field_data_si_units(time_step)
        By = self.data["By"].get_all_field_data_si_units(time_step)
        Wx = Ex - c*By
        if self.get_field_geometry() == 'thetaMode':
            x = self.data["Ex"].get_axis_in_si_units("r", time_step)
        else:
            x = self.data["Ex"].get_axis_in_si_units("x", time_step)
        dx = abs(x[1]-x[0]) # distance between data points in y direction
        
        if self.get_field_geometry() in ['2D', 'thetaMode']:
            slope = np.gradient(Wx, dx, axis=0)
        elif self.get_field_geometry() == '3D':
            slope = np.gradient(Wx, dx, axis=1)
        return slope


class TransverseWakefieldSlopeY(CustomField):
    # List of necessary fields and simulation parameters.
    necessary_data = {"2D": ["Ey", "Bx"],
                     "3D": ["Ey", "Bx"],
                     "thetaMode": ["Ey", "Bx"]}
    necessary_parameters = []
    units = "V/m^2"
    si_units = True
    standard_name = "dy Wy"

    def calculate_field(self, time_step):
        Ey = self.data["Ey"].get_all_field_data_si_units( time_step)
        Bx = self.data["Bx"].get_all_field_data_si_units( time_step)
        Wy = Ey + c*Bx
        if self.get_field_geometry() == 'thetaMode':
            y = self.data["Ey"].get_axis_in_si_units("r", time_step)
        else:
            y = self.data["Ey"].get_axis_in_si_units("y", time_step)
        dy = abs(y[1]-y[0]) # distance between data points in y direction
        
        if self.get_field_geometry() in ['2D', 'thetaMode']:
            slope = np.gradient(Wy, dy, axis=0)
        elif self.get_field_geometry() == '3D':
            slope = np.gradient(Wy, dy, axis=1)
        return slope


class EzSlope(CustomField):
    necessary_data = {"2D": ["Ez"],
                     "3D": ["Ez"],
                     "thetaMode": ["Ez"]}
    necessary_parameters = []
    units = "V/m^2"
    si_units = True
    standard_name = "dz Ez"

    def calculate_field(self, time_step):
        Ez = self.data["Ez"].get_all_field_data_si_units( time_step)
        z = self.data["Ez"].get_axis_in_si_units("z", time_step)
        dz = abs(z[1]-z[0]) # distance between data points in z direction
        if (self.get_field_geometry() == '2D'
            or self.get_field_geometry() == 'thetaMode'):
            slope = np.gradient(Ez, dz, axis=1)
        elif self.get_field_geometry() == '3D':
            slope = np.gradient(Ez, dz, axis=2)
        return slope


class CustomFieldCreator:
    custom_fields = [
        TransverseWakefieldX,
        TransverseWakefieldY,
        TransverseWakefieldSlopeX,
        TransverseWakefieldSlopeY,
        LaserIntensityField,
        NormalizedVectorPotential,
        EzSlope
        ]
    @classmethod
    def get_custom_fields(cls, data_container):
        field_list = list()
        for Field in cls.custom_fields:
            if Field.meets_requirements(data_container):
                field_list.append(Field(data_container))
        return field_list


"""
Custom Raw Data Sets
"""
class CustomRawDataSet(CustomDataElement):
    @classmethod
    def meets_requirements(cls, data_container, species_name):
        "Checks whether the required data and parameters are available"
        if data_container.get_simulation_geometry() in cls.necessary_data:
            data_requirements_met = set(
                data_container.get_species(
                    species_name).get_raw_dataset_names_list()).issuperset(
                        cls.necessary_data[
                            data_container.get_simulation_geometry()])
            parameter_requirements_met = set(
                data_container.get_names_of_available_parameters()).issuperset(
                    cls.necessary_parameters)
            return data_requirements_met and parameter_requirements_met
        else:
            return False

    def set_base_data(self):
        geometry = self.data_container.get_simulation_geometry()
        self.data = {}
        for data_name in self.necessary_data[geometry]:
            self.data[data_name] = self.data_container.get_species(
                self.species_name).get_raw_dataset(data_name)

    """
    Get data in original units (to be implemented in each subclass)
    """
    def get_data_in_original_units(self, time_step):
        raise NotImplementedError

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


class XPrimeDataSet(CustomRawDataSet):
    # List of necessary data sets and simulation parameters.
    necessary_data = {"2D": ["Px", "Pz"],
                     "3D": ["Px", "Pz"],
                     "thetaMode": ["Px", "Pz"]}
    necessary_parameters = []
    units = "rad"
    si_units = True
    standard_name = "x'"

    def get_data_in_original_units(self, time_step):
        Px = self.data["Px"].get_data_in_si_units( time_step)
        Pz = self.data["Pz"].get_data_in_si_units( time_step)
        xP = np.divide(Px, Pz)
        return xP


class YPrimeDataSet(CustomRawDataSet):
    # List of necessary data sets and simulation parameters.
    necessary_data = {"2D": ["Py", "Pz"],
                     "3D": ["Py", "Pz"],
                     "thetaMode": ["Py", "Pz"]}
    necessary_parameters = []
    units = "rad"
    si_units = True
    standard_name = "y'"

    def get_data_in_original_units(self, time_step):
        Py = self.data["Py"].get_data_in_si_units(time_step)
        Pz = self.data["Pz"].get_data_in_si_units(time_step)
        yP = np.divide(Py, Pz)
        return yP


class DeltaZPrimeDataSet(CustomRawDataSet):
    # List of necessary data sets and simulation parameters.
    necessary_data = {"2D": ["z", "Charge"],
                     "3D": ["z", "Charge"],
                     "thetaMode": ["z", "Charge"]}
    necessary_parameters = []
    units = "m"
    si_units = True
    standard_name = "Δz"

    def get_data_in_original_units(self, time_step):
        z = self.data["z"].get_data_in_si_units(time_step)
        q = self.data["Charge"].get_data_in_si_units(time_step)
        meanZ = np.average(z, weights=q)
        dZ = z-meanZ
        return dZ


class ForwardMomentumVariationDataSet(CustomRawDataSet):
    # List of necessary data sets and simulation parameters.
    necessary_data = {"2D": ["Pz", "Charge"],
                     "3D": ["Pz", "Charge"],
                     "thetaMode": ["Pz", "Charge"]}
    necessary_parameters = []
    units = "rad"
    si_units = True
    standard_name = "ΔPz/Pz"

    def get_data_in_original_units(self, time_step):
        Pz = self.data["Pz"].get_data_in_si_units(time_step)
        q = self.data["Charge"].get_data_in_si_units(time_step)
        meanPz = np.average(Pz, weights=q)
        dPz = np.divide(Pz - meanPz, meanPz)
        return dPz


class SpeedOfLightCoordinate(CustomRawDataSet):
    # List of necessary data sets and simulation parameters.
    necessary_data = {"2D": ["z"],
                     "3D": ["z"],
                     "thetaMode": ["z"]}
    necessary_parameters = []
    units = "m"
    si_units = True
    standard_name = "xi"

    def get_data_in_original_units(self, time_step):
        z = self.data["z"].get_data_in_si_units(time_step)
        t = self.data["z"].get_time_in_units("s", time_step)
        xi = z - c*t
        return xi


#class BeamComovingCoordinate(CustomRawDataSet):
#    # List of necessary data sets and simulation parameters.
#    necessary_data = {"2D": ["z"],
#                     "3D": ["z"],
#                     "thetaMode": ["z"]}
#    necessary_parameters = []
#    units = "m"
#    si_units = True
#    standard_name = "xi_beam"

#    def get_data_in_original_units(self, time_step):
#        z = self.data["z"].get_data_in_si_units(time_step)
#        xi_b = z - min(z)
#        return xi_b


#class UncorrelatedEnergyVariationDataSet(CustomRawDataSet):
#    # List of necessary data sets and simulation parameters.
#    necessary_data = {"2D": ["Pz", "Py", "z", "Charge"],
#                     "3D": ["Pz", "Py", "Pz", "z", "Charge"],
#                     "thetaMode": ["Pz", "Py", "Pz", "z", "Charge"]}
#    necessary_parameters = []
#    units = "."
#    si_units = True
#    standard_name = "UncEneSp"

#    def get_data_in_original_units(self, time_step):
#        Pz = self.data["Pz"].get_data_in_original_units(time_step)
#        Py = self.data["Py"].get_data_in_original_units(time_step)
#        z = self.data["z"].get_data_in_original_units(time_step)
#        q = self.data["Charge"].get_data_in_original_units(time_step)
#        gamma = np.sqrt(Pz**2 + Py**2)
#        mean_gamma = np.average(gamma, weights=np.abs(q))
#        rel_gamma_spread = (gamma-mean_gamma)/mean_gamma
#        dz = z - np.average(z, weights=q)
#        p = np.polyfit(dz, rel_gamma_spread, 1, w=q)
#        slope = p[0]
#        unc_gamma_spread = rel_gamma_spread - slope*dz
#        return unc_gamma_spread
 
    
class CustomRawDataSetCreator:
    custom_datasets = [
        XPrimeDataSet,
        YPrimeDataSet,
        DeltaZPrimeDataSet,
        ForwardMomentumVariationDataSet,
        SpeedOfLightCoordinate,
        ]
    @classmethod
    def get_custom_datasets(cls, data_container, species_name):
        dataset_list = list()
        for dataSet in cls.custom_datasets:
            if dataSet.meets_requirements(data_container, species_name):
                dataset_list.append(dataSet(data_container, species_name))
        return dataset_list
