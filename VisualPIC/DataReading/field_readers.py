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

from h5py import File as H5F
import numpy as np
from opmd_viewer.openpmd_timeseries.data_reader.params_reader import (
    read_openPMD_params)
import opmd_viewer.openpmd_timeseries.data_reader.field_reader as opmd_fr


class FieldReader():
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def read_field(self, file_path, field_path, slice_i=None, slice_j=None,
                   slice_dir_i=None, slice_dir_j=None, transv_ax='r', m=0,
                   theta=0):
        fld_metadata = self.read_field_metadata(file_path, field_path)
        geom = fld_metadata['field']['geometry']
        if geom == "1D":
            fld = self.read_field_1d(file_path, field_path)
        elif geom == "2D-cart":
            fld = self.read_field_2d_cart(file_path, field_path, slice_i,
                                          slice_dir_i)
        elif geom == "3D-cart":
            fld = self.read_field_3d_cart(file_path, field_path, slice_i,
                                          slice_j, slice_dir_i, slice_dir_j)
        elif geom == "2D-cyl":
            fld = self.read_field_2d_cyl(file_path, field_path, slice_i,
                                         slice_dir_i)
        elif geom == "thetaMode":
            fld = self.read_field_theta(file_path, field_path, m, theta,
                                        transv_ax, slice_i, slice_dir_i)
        self.readjust_metadata(fld_metadata, slice_dir_i, slice_dir_j,
                               transv_ax)
        return fld, fld_metadata

    def readjust_metadata(self, field_metadata, slice_dir_i, slice_dir_j,
                          transv_ax):
        geom = field_metadata['field']['geometry']
        if geom in ["2D-cyl", "thetaMode"]:
            if transv_ax != 'r':
                r_array = field_metadata['axis']['r']['array']
                r_units = field_metadata['axis']['r']['units']
                new_ax_array = np.linspace(-max(r_array), max(r_array),
                                           len(r_array)*2)
                field_metadata['axis'][transv_ax] = {}
                field_metadata['axis'][transv_ax]['units'] = r_units
                field_metadata['axis'][transv_ax]['array'] = new_ax_array
                del field_metadata['axis']['r']
        if slice_dir_i is not None:
            del field_metadata['axis'][slice_dir_i]
        if slice_dir_j is not None:
            del field_metadata['axis'][slice_dir_j]

    def read_field_1d(self, file_path, field_path):
        raise NotImplementedError

    def read_field_2d_cart(self, file_path, field_path, slice_i=None,
                           slice_dir_i='z'):
        raise NotImplementedError

    def read_field_3d_cart(self, file_path, field_path, slice_i=None,
                           slice_j=None, slice_dir_i=None, slice_dir_j=None):
        raise NotImplementedError

    def read_field_2d_cyl(self, file_path, field_path, transv_ax='r', 
                          slice_i=None, slice_dir_i=None):
        raise NotImplementedError

    def read_field_theta(self, file_path, field_path, m=0, theta=0,
                         transv_ax='r', slice_i=None, slice_dir_i=None):
        raise NotImplementedError

    def read_field_metadata(self, file_path, field_path):
        raise NotImplementedError


class OsirisFieldReader(FieldReader):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def read_field_1d(self, file_path, field_path):
        file = H5F(file_path, 'r')
        return file[field_path]
    
    def read_field_2d_cart(self, file_path, field_path, slice_i=None,
                           slice_dir_i=None):
        file = H5F(file_path, 'r')
        fld = file[field_path]
        if slice_i is not None:
            fld_shape = fld.shape
            axis_order = ['x', 'z']
            slice_list = [slice(None)] * fld.ndim
            axis_idx_i = axis_order.index(slice_dir_i)
            axis_elements_i = fld_shape[axis_idx_i] 
            slice_idx_i = int(round(axis_elements_i * slice_i))
            slice_list[axis_idx_i] = slice_idx_i
            fld = fld[tuple(slice_list)]
        return fld

    def read_field_3d_cart(self, file_path, field_path, slice_i=None,
                           slice_j=None, slice_dir_i=None, slice_dir_j=None):
        file = H5F(file_path, 'r')
        fld = file[field_path]
        if slice_i is not None:
            fld_shape = fld.shape
            axis_order = ['x', 'y', 'z']
            slice_list = [slice(None)] * fld.ndim
            axis_idx_i = axis_order.index(slice_dir_i)
            axis_elements_i = fld_shape[axis_idx_i] 
            slice_idx_i = int(round(axis_elements_i * slice_i))
            slice_list[axis_idx_i] = slice_idx_i
            if slice_j is not None:
                axis_idx_j = axis_order.index(slice_dir_j)
                axis_elements_j = fld_shape[axis_idx_j] 
                slice_idx_j = int(round(axis_elements_j * slice_j))
                slice_list[axis_idx_j] = slice_idx_j
            fld = fld[tuple(slice_list)]
        return fld

    def read_field_metadata(self, file_path, field_path):
        file = H5F(file_path, 'r')
        md = {}
        field_units = self.get_field_units(file, field_path)
        field_shape = self.get_field_shape(file, field_path)
        field_geometry = self.determine_geometry(file)
        md['field'] = {}
        md['field']['units'] = field_units
        md['field']['geometry'] = field_geometry
        md['axis'] = self.get_axis_data(file, field_path, field_geometry,
                                       field_shape)
        md['time'] = self.get_time_data(file)
        file.close()
        return md
        
    def get_field_units(self, file, field_path):
        """ Returns the field units"""
        return str(list(file[field_path].attrs["UNITS"])[0])[2:-1].replace(
            "\\\\","\\")

    def get_field_shape(self, file, field_path):
        """ Returns shape of field array"""
        return file[field_path].shape

    def determine_geometry(self, file):
        """ Determines the field geometry """
        if '/AXIS/AXIS3' in file:
            return "3D-cart"
        elif '/AXIS/AXIS2' in file:
            return "2D-cart"
        else:
            return "1D"

    def get_axis_data(self, file, field_path, field_geometry, field_shape):
        """ Returns dictionary with the array and units of each field axis """
        axis_data = {}
        axis_data['z'] = {}
        axis_data["z"]["units"] = str(list(file['/AXIS/AXIS1'].attrs[
            "UNITS"])[0])[2:-1].replace("\\\\","\\")
        axis_data["z"]["array"] = np.linspace(file.attrs['XMIN'][0],
                                              file.attrs['XMAX'][0],
                                              field_shape[0])
        if field_geometry in ["2D-cart", "3D-cart"]:
            axis_data['x'] = {}
            axis_data["x"]["units"] = str(list(file['/AXIS/AXIS2'].attrs[
                "UNITS"])[0])[2:-1].replace("\\\\","\\")
            axis_data["x"]["array"] = np.linspace(file.attrs['XMIN'][1],
                                                  file.attrs['XMAX'][1],
                                                  field_shape[1])
        if field_geometry == "3D-cart":
            axis_data['y'] = {}
            axis_data["y"]["units"] = str(list(file['/AXIS/AXIS3'].attrs[
                "UNITS"])[0])[2:-1].replace("\\\\","\\")
            axis_data["y"]["array"] = np.linspace(file.attrs['XMIN'][2],
                                                  file.attrs['XMAX'][2],
                                                  field_shape[2])
        return axis_data

    def get_time_data(self, file):
        """ Returns dictionary with value and units of the simulation time """
        time_data = {}
        time_data["value"] = file.attrs["TIME"][0]
        time_data["units"] = str(file.attrs["TIME UNITS"][0])[2:-1].replace(
            "\\\\","\\")
        return time_data


class OpenPMDFieldReader(FieldReader):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def read_field_theta(self, file_path, field_path, m=0, theta=0,
                         transv_ax='r', slice_i=None, slice_dir_i=None):
        if transv_ax == 'r':
            fld, _ = opmd_fr.read_field_circ(file_path, field_path, m, theta)
        else:
            # Code from openpmd-viewer
            # For Cartesian components, combine r and t components
            field, coord = field_path.split('/')
            fld_r, _ = opmd_fr.read_field_circ(file_path, field + '/r', m,
                                               theta)
            fld_t, _ = opmd_fr.read_field_circ(file_path, field + '/t', m,
                                               theta)
            if transv_ax == 'x':
                fld = np.cos(theta) * fld_r - np.sin(theta) * fld_t
            elif transv_ax == 'y':
                fld = np.sin(theta) * fld_r + np.cos(theta) * fld_t
            # Revert the sign below the axis
            fld[: int(fld.shape[0] / 2)] *= -1
        if slice_dir_i is not None:
            fld_shape = fld.shape
            axis_order = [transv_ax, 'z']
            slice_list = [slice(None)] * fld.ndim
            axis_idx_i = axis_order.index(slice_dir_i)
            axis_elements_i = fld_shape[axis_idx_i] 
            slice_idx_i = int(round(axis_elements_i * slice_i))
            slice_list[axis_idx_i] = slice_idx_i
            fld = fld[tuple(slice_list)]
        return fld

    def read_field_metadata(self, file_path, field_path):
        file = H5F(file_path, 'r')
        field, coord = field_path.split('/')
        md = {}
        t, params = read_openPMD_params(file_path)
        md['time'] = {}
        md['time']['value'] = t
        md['time']['units'] = 's'
        field_geometry = params['fields_metadata'][field]['geometry']
        field_units = self.determine_field_units(field)
        md['field'] = {}
        md['field']['units'] = field_units
        md['field']['geometry'] = field_geometry
        ax_el, ax_lims = opmd_fr.get_grid_parameters(file, [field],
                                                     params['fields_metadata'])
        axes = ax_el.keys()
        md['axis'] = {}
        for axis in axes:
            md['axis'][axis] = {}
            md['axis'][axis]['units'] = 'm'
            md['axis'][axis]['array'] = np.linspace(ax_lims[axis][0], 
                                                    ax_lims[axis][1],
                                                    ax_el[axis])
        return md

    def determine_field_units(self, field):
        if field == 'E':
            return 'V/m'
        if field == 'B':
            return 'T'
        if field == 'rho':
            return 'C/m^3'
