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


from VisualPIC.DataHandling.dataElement import DataElement
from VisualPIC.DataReading.dataReaderSelectors import *
from scipy import interpolate as ip


class FolderDataElement(DataElement):
    """Base class for all data elements (fields and rawDataSets)"""
    def __init__(self, simulation_code, name_in_code, standard_name, location,
                 time_steps, species_name="", internal_name="",
                 has_non_si_units=True):
        DataElement.__init__(self, standard_name, time_steps, species_name,
                             has_non_si_units)
        # name of the variable in the simulation code (e.g. "e1-savg" for the 
        # averaged longitudinal E field in Osiris)
        self.data_name_in_code = name_in_code 
        self.data_location = location
        self.data_reader = None # Each subclass will load its own

    def get_name_in_code(self):
        return self.data_name_in_code
        
    def get_data_original_units(self):
        return self.data_reader.get_data_units()

    def get_time_in_original_units(self, time_step):
        return self.data_reader.get_time(time_step)
        
    def get_time_original_units(self):
        return self.data_reader.get_time_units()


class FolderField(FolderDataElement):
    def __init__(self, simulation_code, name_in_code, standard_name, location,
                 time_steps, species_name="", has_non_si_units=True):
        FolderDataElement.__init__(self, simulation_code, name_in_code,
                                   standard_name, location, time_steps,
                                   species_name,
                                   has_non_si_units=has_non_si_units)
        self.data_reader = FieldReaderSelector.get_reader(
            simulation_code, location, species_name, name_in_code,
            time_steps[0])
          
    def get_field_geometry(self):
        return self.data_reader.field_geometry

    def get_possible_axis_units(self):
        return self.unit_converter.get_possible_axis_units(self)

    def get_axis_data_in_original_units(self, axis, time_step):
        return self.data_reader.get_axis_data(time_step)[axis] #dictionary
        
    def get_axis_original_units(self):
        return self.data_reader.get_axis_units()

    """
    Get data in original units
    """
    def get_1d_slice_in_original_units(self, time_step, slice_pos_x,
                                       slice_pos_y=None):
        return self.data_reader.get_1d_slice(time_step, slice_pos_x,
                                             slice_pos_y)

    def get_2d_slice_in_original_units(self, slice_axis, slice_pos, time_step):
        return self.data_reader.get_2d_slice(slice_axis, slice_pos, time_step)

    def get_all_field_data_in_original_units(self, time_step):
        return  self.data_reader.get_all_field_data(time_step)

    def get_3d_field_from_2d_slice_in_original_units(
            self, time_step, transvEl, longEl, fraction):
        # TODO: share same method with customfield.
        """
            fraction: used to define the range of data we want to visualize in the transverse direction.
                - fraction = 1 -> get all the data
                - fraction = 0.5 -> get only from x=0 to x=x_max/2
        """
        field2D = self.get_all_field_data_in_original_units(time_step)
        nx = field2D.shape[0]
        field2D = field2D[int(nx/2):int(nx/2+nx/2*fraction)] # we get only half
        cilShape = field2D.shape
        Rin,Zin = np.mgrid[0:cilShape[0], 0:cilShape[1]] # cyl. coordinates of original data
        Zin = np.reshape(Zin, Zin.shape[0]*Zin.shape[1])
        Rin = np.reshape(Rin, Rin.shape[0]*Rin.shape[1])
        field2D = np.reshape(field2D, field2D.shape[0]*field2D.shape[1])
        transvSpacing = cilShape[0]*2/transvEl
        lonSpacing = cilShape[1]/longEl
        field3D = np.zeros((transvEl, transvEl, longEl))
        X, Y, Z = np.mgrid[0:cilShape[0]:transvSpacing,0:cilShape[0]:transvSpacing,0:cilShape[1]:lonSpacing] # cart. coordinates of 3D field
        Rout = np.sqrt(X**2 + Y**2)
        # Fill the field sector by sector (only the first has to be calculated. The rest are simlpy mirrored)
        field3D[int(transvEl/2):transvEl+1,int(transvEl/2):transvEl+1] = ip.griddata(np.column_stack((Rin,Zin)), field2D, (Rout, Z), method='nearest', fill_value = 0) # top right section when looking back from z to the x-y plane.
        field3D[0:int(transvEl/2),int(transvEl/2):transvEl+1] = np.flip(field3D[int(transvEl/2):transvEl+1,int(transvEl/2):transvEl+1], 0)
        field3D[0:int(transvEl/2),0:int(transvEl/2)] = np.flip(field3D[0:int(transvEl/2),int(transvEl/2):transvEl+1], 1)
        field3D[int(transvEl/2):transvEl+1,0:int(transvEl/2)] = np.flip(field3D[int(transvEl/2):transvEl+1,int(transvEl/2):transvEl+1], 1)
        return field3D
    
    """
    Get data in any units
    """
    def get_1d_slice(self, time_step, units, slice_pos_x, slice_pos_y=None):
        slice_data = self.data_reader.get_1d_slice(time_step, slice_pos_x,
                                                   slice_pos_y)
        originalDataUnits = self.data_reader.get_data_units()
        return self.unit_converter.get_data_in_units(self, units, slice_data)

    def get_2d_slice(self, slice_axis, slice_pos, time_step, units):
        slice_data = self.data_reader.get_2d_slice(slice_axis, slice_pos,
                                                   time_step)
        originalDataUnits = self.data_reader.get_data_units()
        return self.unit_converter.get_data_in_units(self, units, slice_data)

    def get_all_field_data(self, time_step, units):
        fieldData = self.data_reader.get_all_field_data(time_step)
        originalDataUnits = self.data_reader.get_data_units()
        return self.unit_converter.get_data_in_units(self, units, fieldData)

    """
    Get data in IS units
    """
    def get_1d_slice_si_units(self, time_step, slice_pos_x, slice_pos_y=None):
        slice_data = self.data_reader.get_1d_slice(time_step, slice_pos_x,
                                                   slice_pos_y)
        originalDataUnits = self.data_reader.get_data_units()
        return self.unit_converter.get_data_in_si_units(self, slice_data)

    def get_2d_slice_si_units(self, slice_axis, slice_pos, time_step):
        slice_data = self.data_reader.get_2d_slice(slice_axis, slice_pos,
                                                   time_step)
        originalDataUnits = self.data_reader.get_data_units()
        return self.unit_converter.get_data_in_si_units(self, slice_data)

    def get_all_field_data_si_units(self, time_step):
        fieldData = self.data_reader.get_all_field_data(time_step)
        originalDataUnits = self.data_reader.get_data_units()
        return self.unit_converter.get_data_in_si_units(self, fieldData)


class FolderRawDataSet(FolderDataElement):
    def __init__(self, simulation_code, name_in_code, standard_name, location,
                 time_steps, species_name, internal_name,
                 has_non_si_units=True):
        FolderDataElement.__init__(self, simulation_code, name_in_code, 
                                   standard_name, location, time_steps,
                                   species_name, internal_name,
                                   has_non_si_units)
        self.data_reader = RawDataReaderSelector.get_reader(
            simulation_code, location, species_name, name_in_code,
            internal_name, time_steps[0])

    """
    Get data in original units
    """
    def get_data_in_original_units(self, time_step):
        return self.data_reader.get_data(time_step)

    """
    Get data in any units
    """
    def get_data_in_units(self, units, time_step):
        return self.unit_converter.get_data_in_units(
            self, units,self.data_reader.get_data(time_step))

    """
    Get data in IS units
    """
    def get_data_in_si_units(self, time_step):
        return self.unit_converter.get_data_in_si_units(
            self, self.data_reader.get_data(time_step))
