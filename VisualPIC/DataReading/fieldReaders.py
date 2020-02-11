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


import abc
from h5py import File as H5File
import numpy as np

from VisualPIC.DataReading.dataReader import DataReader
from VisualPIC.DataReading.openPMDTimeSeriesSingleton import (
    OpenPMDTimeSeriesSingleton, openpmd_installed)
if openpmd_installed:
    from openpmd_viewer.openpmd_timeseries.data_reader.utilities import (
        get_shape as openpmd_get_shape)
    from openpmd_viewer.openpmd_timeseries.data_reader.field_reader import (
        find_dataset as openpmd_find_dataset)


class FieldReaderBase(DataReader):
    """Parent class for all FieldReaders"""
    __metaclass__  = abc.ABCMeta
    def __init__(self, location, species_name, data_name, first_time_step):
        DataReader.__init__(self, location, species_name, data_name)
        self.axis_units = {}
        self.axis_data = {}
        self.first_time_step = first_time_step
        self.current_time_step = {"Slice-1D": -1,
                                  "Slice-2D": -1,
                                  "AllData": -1}
        self.data = {"Slice-1D": [], "Slice-2D": [], "AllData": []}
        self.current_slice_axis = {"Slice-1D": -1, "Slice-2D": -1}
        self.current_slice_position = {"Slice-1D": -1, "Slice-2D": -1}
        self.read_basic_data()

    def get_1d_slice(self, time_step, slice_pos_x, slice_pos_y=None):
        if ((time_step != self.current_time_step["Slice-1D"])
            or ((slice_pos_x, slice_pos_y) != self.current_slice_position[
                "Slice-1D"])):
            self.current_time_step["Slice-1D"] = time_step
            self.current_slice_position["Slice-1D"] = (slice_pos_x,
                                                       slice_pos_y)
            self.data["Slice-1D"] = self.read_1d_slice(time_step, slice_pos_x,
                                                       slice_pos_y)
        return self.data["Slice-1D"]

    def get_2d_slice(self, slice_axis, slice_pos, time_step):
        if ((time_step != self.current_time_step["Slice-2D"]) 
            or (slice_pos != self.current_slice_position["Slice-2D"]) 
            or (slice_axis != self.current_slice_axis["Slice-2D"])):
            self.current_time_step["Slice-2D"] = time_step
            self.current_slice_position["Slice-2D"] = slice_pos
            self.current_slice_axis["Slice-2D"] = slice_axis
            self.data["Slice-2D"] = self.read_2d_slice(
                slice_axis, slice_pos, time_step)
        return self.data["Slice-2D"]

    def get_all_field_data(self, time_step):
        if time_step != self.current_time_step["AllData"]:
            self.current_time_step["AllData"] = time_step
            self.data["AllData"] = self.read_all_field_data(time_step)
        return self.data["AllData"]

    def get_time(self, time_step):
        self.read_time(time_step)
        return self.current_time

    def get_time_units(self):
        if self.time_units == "":
            self.read_units()
        return self.time_units

    def get_data_units(self):
        if self.data_units == "":
            self.read_units()
        return self.data_units

    def get_axis_data(self, time_step):
        self.axis_data = self.read_axis_data(time_step)
        return self.axis_data

    def get_axis_units(self):
        if self.data_units == "":
            self.read_units()
        return self.axis_units

    @abc.abstractmethod
    def read_basic_data(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_matrix_shape(self, file_content):
        raise NotImplementedError

    @abc.abstractmethod
    def read_internal_name(self, file_content):
        raise NotImplementedError

    @abc.abstractmethod
    def determine_field_geometry(self, file_content):
        raise NotImplementedError

    @abc.abstractmethod
    def read_1d_slice(self, time_step, slice_pos_x, slice_pos_y = None):
        raise NotImplementedError

    @abc.abstractmethod
    def read_2d_slice(self, slice_axis, slice_pos, time_step):
        raise NotImplementedError

    @abc.abstractmethod
    def read_all_field_data(self, time_step):
        raise NotImplementedError

    @abc.abstractmethod
    def read_axis_data(self, time_step):
        raise NotImplementedError

    @abc.abstractmethod
    def read_time(self, time_step):
        raise NotImplementedError


class OsirisFieldReader(FieldReaderBase):
    def __init__(self, location, species_name, data_name, first_time_step):
        FieldReaderBase.__init__(self, location, species_name, data_name,
                                 first_time_step)

    def read_basic_data(self):
        file_content = self.open_file(self.first_time_step)
        self.read_internal_name(file_content)
        self.determine_field_geometry(file_content)
        self.get_matrix_shape(file_content)
        self.read_simulation_properties(file_content)
        file_content.close()

    def get_matrix_shape(self, file_content):
        self.matrix_shape = file_content.get(self.internal_name).shape

    def read_internal_name(self, file_content):
        self.internal_name = list(file_content.keys())[1]

    def determine_field_geometry(self, file_content):
        # TODO: add support for cylindrical geometry
        if '/AXIS/AXIS3' in file_content:
            self.field_geometry = "3D"
        else:
            self.field_geometry = "2D"

    def read_1d_slice(self, time_step, slice_pos_x, slice_pos_y=None):
        file_content = self.open_file(time_step)
        field_data = file_content[self.internal_name]
        if self.field_geometry == '2D':
            elements_x = self.matrix_shape[-2]
            selected_row = round(elements_x*(float(slice_pos_x)/100))
            slice_data = np.array(field_data[selected_row])
        elif self.field_geometry == '3D':
            elements_x = self.matrix_shape[-3]
            elements_y = self.matrix_shape[-2]
            selected_x = round(elements_x*(float(slice_pos_x)/100))
            selected_y = round(elements_y*(float(slice_pos_y)/100))
            slice_data = np.array(field_data[selected_x, selected_y])
        file_content.close()
        return slice_data

    def read_2d_slice(self, slice_axis, slice_pos, time_step):
        # TODO: add support for selecting slice axis
        file_content = self.open_file(time_step)
        field_data = file_content[self.internal_name]
        # number of elements in thetransverse direction
        elements_tr = self.matrix_shape[-3] 
        selected_row = round(elements_tr*(float(slice_pos)/100))
        slice_data = np.array(field_data[selected_row])
        file_content.close()
        return slice_data

    def read_all_field_data(self, time_step):
        file_content = self.open_file(time_step)
        field_data = np.array(file_content[self.internal_name])
        file_content.close()
        return field_data

    def read_axis_data(self, time_step):
        file_content = self.open_file(time_step)
        # number of elements along the longitudinal z direction
        elements_z = self.matrix_shape[-1]
        # number of elements along the transverse x direction
        elements_x = self.matrix_shape[-2] 
        axis_data = {}
        axis_data["z"] = np.linspace(file_content.attrs['XMIN'][0],
                                     file_content.attrs['XMAX'][0],
                                     elements_z)
        axis_data["x"] = np.linspace(file_content.attrs['XMIN'][1],
                                     file_content.attrs['XMAX'][1],
                                     elements_x)
        if self.field_geometry == "3D":
            # number of elements along the transverse y direction
            elements_y = self.matrix_shape[-3] 
            axis_data["y"] = np.linspace(file_content.attrs['XMIN'][2],
                                         file_content.attrs['XMAX'][2],
                                         elements_y)
        file_content.close()
        return axis_data

    def read_time(self, time_step):
        file_content = self.open_file(time_step)
        self.current_time = file_content.attrs["TIME"][0]
        file_content.close()

    def read_units(self):
        file_content = self.open_file(self.first_time_step)
        self.axis_units["z"] = str(list(file_content['/AXIS/AXIS1'].attrs[
            "UNITS"])[0])[2:-1].replace("\\\\","\\")
        self.axis_units["x"] = str(list(file_content['/AXIS/AXIS2'].attrs[
            "UNITS"])[0])[2:-1].replace("\\\\","\\")
        self.data_units = str(list(file_content[self.internal_name].attrs[
            "UNITS"])[0])[2:-1].replace("\\\\","\\")
        self.time_units = str(file_content.attrs[
            "TIME UNITS"][0])[2:-1].replace("\\\\","\\")
        file_content.close()

    def read_simulation_properties(self, file_content):
        self.grid_resolution = np.array(file_content.attrs['NX'])
        self.grid_size = (np.array(file_content.attrs['XMAX'])
                          - np.array(file_content.attrs['XMIN']))
        self.grid_units = str(list(file_content['/AXIS/AXIS1'].attrs[
            "UNITS"])[0])[2:-1].replace("\\\\","\\")

    def open_file(self, time_step):
        file_name = self.data_name + "-"
        if self.species_name != "":
            file_name += self.species_name + "-"
        file_name += str(time_step).zfill(6)
        ending = ".h5"
        file_path = self.location + "/" + file_name + ending
        file_content = H5File(file_path, 'r')
        return file_content


class HiPACEFieldReader(FieldReaderBase):
    def __init__(self, location, species_name, data_name, first_time_step):
        FieldReaderBase.__init__(self, location, species_name, data_name,
                                 first_time_step)

    def read_basic_data(self):
        file_content = self.open_file(self.first_time_step)
        self.read_internal_name(file_content)
        self.determine_field_geometry(file_content)
        self.get_matrix_shape(file_content)
        self.read_simulation_properties(file_content)
        file_content.close()

    def get_matrix_shape(self, file_content):
        self.matrix_shape = file_content.get(self.internal_name).shape

    def read_internal_name(self, file_content):
        self.internal_name = list(file_content.keys())[0]

    def determine_field_geometry(self, file_content):
        self.field_geometry = "3D"

    def read_1d_slice(self, time_step, slice_pos_x, slice_pos_y=None):
        # TODO: add support for 3D fields
        file_content = self.open_file(time_step)
        field_data = file_content[self.internal_name]
        if self.field_geometry == '2D':
            elements_x = self.matrix_shape[-2]
            selected_row = round(elements_x*(float(slice_pos_x)/100))
            slice_data = np.array(field_data[selected_row])
        elif self.field_geometry == '3D':
            elements_x = self.matrix_shape[-3]
            elements_y = self.matrix_shape[-2]
            selected_x = round(elements_x*(float(slice_pos_x)/100))
            selected_y = round(elements_y*(float(slice_pos_y)/100))
            slice_data = np.array(field_data[selected_x, selected_y])
        file_content.close()
        return slice_data

    def read_2d_slice(self, slice_axis, slice_pos, time_step):
        file_content = self.open_file(time_step)
        field_data = file_content[self.internal_name]
        # number of elements in the transverse direction
        elements_x3 = self.matrix_shape[2]
        selected_row = round(elements_x3*(float(slice_pos)/100))
        slice_data = np.array(field_data[:,:,selected_row]).T
        file_content.close()
        return slice_data

    def read_all_field_data(self, time_step):
        file_content = self.open_file(time_step)
        field_data = np.array(file_content[self.internal_name])
        file_content.close()
        return field_data

    def read_axis_data(self, time_step):
        file_content = self.open_file(time_step)
        # number of elements in the longitudinal z direction
        elements_z = self.matrix_shape[-1]
        # number of elements in the transverse y direction
        elements_x = self.matrix_shape[-2]
        axis_data = {}
        axis_data["z"] = np.linspace(file_content.attrs['XMIN'][0],
                                     file_content.attrs['XMAX'][0],
                                     elements_z)
        axis_data["x"] = np.linspace(file_content.attrs['XMIN'][1],
                                     file_content.attrs['XMAX'][1],
                                     elements_x)
        if self.field_geometry == "3D":
            # number of elements in the transverse x direction
            elements_y = self.matrix_shape[-3]
            axis_data["y"] = np.linspace(file_content.attrs['XMIN'][2],
                                         file_content.attrs['XMAX'][2],
                                         elements_y)
        file_content.close()
        return axis_data

    def read_time(self, time_step):
        file_content = self.open_file(time_step)
        self.current_time = file_content.attrs["TIME"][0]
        file_content.close()

    def read_units(self):
        # No units information is currently stored by HiPACE
        if self.species_name != "":
            self.data_units = 'e \omega_p^3/ c^3'
        elif self.data_name == 'Ez':
            self.data_units = 'm_e c \omega_p e^{-1}'
        else:
            self.data_units = 'unknown'
        self.time_units = '1/ \omega_p'
        self.axis_units["x"] = 'c/ \omega_p'
        self.axis_units["y"] = 'c/ \omega_p'
        self.axis_units["z"] = 'c/ \omega_p'

    def read_simulation_properties(self, file_content):
        self.grid_resolution = np.array(file_content.attrs['NX'])
        self.grid_size = (np.array(file_content.attrs['XMAX'])
                          - np.array(file_content.attrs['XMIN']))
        self.grid_units = str(list(file_content['/AXIS/AXIS1'].attrs[
            "UNITS"])[0])[2:-1].replace("\\\\","\\")

    def open_file(self, time_step):
        if self.species_name != "":
            file_name = 'density_' + self.species_name + '_' + self.data_name
        else:
            file_name = 'field_' + self.data_name

        file_name += '_' + str(time_step).zfill(6)
        ending = ".h5"
        file_path = self.location + "/" + file_name + ending
        file_content = H5File(file_path, 'r')
        return file_content


class OpenPMDFieldReader(FieldReaderBase):
    def __init__(self, location, species_name, data_name, first_time_step):
        # First check whether openPMD is installed
        if not openpmd_installed:
            raise RunTimeError(
                "You need to install openPMD-viewer, e.g. with:\n"
                "pip install openPMD-viewer")
        # Store an openPMD timeseries object
        # (Its API is used in order to conveniently extract data from the file)
        self.openpmd_ts = OpenPMDTimeSeriesSingleton(location,
                                                     check_all_files=False)
        self.openpmd_data_name = data_name
        # Initialize the instance
        FieldReaderBase.__init__(self, location, species_name, data_name,
                                 first_time_step)

    def read_basic_data(self):
        file_content = self.open_file(self.first_time_step)
        self._determine_field_geometry()
        self._determine_internal_name()
        self.get_matrix_shape(file_content)
        file_content.close()

    def get_matrix_shape(self, file_content):
        _, dataset = openpmd_find_dataset( file_content, self.internal_name )
        self.matrix_shape = openpmd_get_shape( dataset )

    def _determine_internal_name(self):
        self.internal_name = self.openpmd_data_name
        # If field is vectorial, get component
        if '/' in self.openpmd_data_name:
            field = self.openpmd_data_name.split("/")[0]
            coord = self.openpmd_data_name.split("/")[1]
            # If component is carterian and geometry is thetaMode,
            # change internal name to radial component
            if self.field_geometry == "thetaMode" and coord in ['x', 'y']:
                self.internal_name = field + '/r'

    def _determine_field_geometry(self):
        # Find the name of the field; vector fields like E are encoded as "E/x"
        field_name = self.openpmd_data_name.split("/")[0]
        geometry = self.openpmd_ts.fields_metadata[field_name]['geometry']
        if geometry == '3dcartesian':
            self.field_geometry = "3D"
        elif geometry == '2dcartesian':
            self.field_geometry = "2D"
        elif geometry == 'thetaMode':
            self.field_geometry = "thetaMode"
        else:
            raise ValueError("Unsupported geometry: %s" %geometry)

    def read_1d_slice(self, time_step, slice_pos_x, slice_pos_y=None):
        # Find the name of the field; vector fields like E are encoded as "E/x"
        field_and_coord = self.openpmd_data_name.split("/")
        if self.field_geometry == '2D':
            field_data, _ = self.openpmd_ts.get_field(
                                *field_and_coord, iteration=time_step )
            elements_x = self.matrix_shape[-2]
            selected_row = round(elements_x*(float(slice_pos_x)/100))
            slice_data = np.array(field_data[selected_row])
        elif self.field_geometry == '3D':
            # Slice first along X
            field_data = self.read_2d_slice( None, slice_pos_x, time_step )
            # Then slice along Y
            elements_y = self.matrix_shape[-2]
            selected_y = round(elements_y*(float(slice_pos_y)/100))
            slice_data = np.array(field_data[selected_y])
        elif self.field_geometry == "thetaMode":
            field_data, _ = self.openpmd_ts.get_field(
                                *field_and_coord, iteration=time_step )
            elements_x = self.matrix_shape[-2]*2
            selected_row = round(elements_x*(float(slice_pos_x)/100))
            slice_data = np.array(field_data[selected_row])
        return slice_data

    def read_2d_slice(self, slice_axis, slice_pos, time_step):
        # Find the name of the field; vector fields like E are encoded as "E/x"
        field_and_coord = self.openpmd_data_name.split("/")
        # Convert the `slice_pos` from a 0-to-100 number to -1 to 1
        slicing = -1. + 2*slice_pos/100.
        # Extract the slice
        slice_data, _ = self.openpmd_ts.get_field(
                *field_and_coord, iteration=time_step,
                slicing_dir="x", slicing=slicing )
        return slice_data

    def read_all_field_data(self, time_step):
        # Find the name of the field; vector fields like E are encoded as "E/x"
        field_and_coord = self.openpmd_data_name.split("/")
        field_data, _ = self.openpmd_ts.get_field(
                        *field_and_coord, iteration=time_step, slicing=None )
        return field_data

    def read_axis_data(self, time_step):
        # Find the name of the field; vector fields like E are encoded as "E/x"
        field_and_coord = self.openpmd_data_name.split("/")
        # Note: the code below has very bad performance because
        # it automatically reads the field data, just to extract the metadata
        # TODO: improve in the future
        _, field_meta_data = self.openpmd_ts.get_field( *field_and_coord,
                                    iteration=time_step, slicing=None )
        # Construct the `axis_data` from the object `field_meta_data`
        axis_data = {}
        if self.field_geometry == "thetaMode":
            axis_data["z"] = getattr( field_meta_data, "z" )
            axis_data["r"] = getattr( field_meta_data, "r" )
        else:
            axis_data["z"] = getattr( field_meta_data, "z" )
            axis_data["x"] = getattr( field_meta_data, "x" )
            if self.field_geometry == "3D":
                axis_data["y"] = getattr( field_meta_data, "y" )
        return axis_data

    def read_time(self, time_step):
        # The line below sets the attribute `_current_i` of openpmd_ts
        self.openpmd_ts._find_output( None, time_step )
        # This sets the corresponding time
        self.current_time = self.openpmd_ts.t[ self.openpmd_ts._current_i ]

    def read_units(self):
        # TODO find the exact unit; needs navigation in file
        file_content = self.open_file(self.first_time_step)
        # OpenPMD data always provide conversion to SI units
        self.axis_units["x"] = "m"
        self.axis_units["y"] = "m"
        self.axis_units["z"] = "m"
        self.axis_units["r"] = "m"
        self.time_units = "s"
        self.data_units = "arb.u." 
        file_content.close()

    def open_file(self, time_step):
        # The line below sets the attribute `_current_i` of openpmd_ts
        self.openpmd_ts._find_output( None, time_step )
        # This finds the full path to the corresponding file
        file_name = self.openpmd_ts.h5_files[ self.openpmd_ts._current_i ]
        file_content = H5File(file_name, 'r')
        return file_content
