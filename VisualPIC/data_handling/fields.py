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

from copy import copy

from VisualPIC.helper_functions import get_common_timesteps


class Field():
    def __init__(self, field_name, field_timesteps, unit_converter,
                 species_name=None):
        self.field_name = field_name
        self.timesteps = field_timesteps
        self.species_name = species_name
        self.unit_converter = unit_converter
        self._current_data_params = None
        self._fld_data = None
        self._fld_metadata = None

    def get_data(self, time_step, field_units=None, axes_units=None,
                 axes_to_convert=None, time_units=None, slice_i=0.5,
                 slice_j=0.5, slice_dir_i=None, slice_dir_j=None, m='all',
                 theta=0, only_metadata=False):
        params = [time_step, field_units, axes_units, axes_to_convert,
                  time_units, slice_i, slice_j, slice_dir_i, slice_dir_j, m,
                  theta]
        # Avoid reading data more than once in a consecutive way
        if (params != self._current_data_params or
            (not only_metadata and self._fld_data is None)):
            self._current_data_params = params
            fld_data, fld_metadata = self._get_data(
                time_step, field_units=field_units, axes_units=axes_units,
                axes_to_convert=axes_to_convert, time_units=time_units,
                slice_dir_i=slice_dir_i, slice_dir_j=slice_dir_j, m=m,
                theta=theta, only_metadata=only_metadata)
            if only_metadata:
                self._fld_data = None
            else:
                self._fld_data = fld_data
            self._fld_metadata = fld_metadata
        if only_metadata:
            return [], copy(self._fld_metadata)
        else:
            return copy(self._fld_data), copy(self._fld_metadata)

    def get_only_metadata(self, time_step, field_units=None, axes_units=None,
                          axes_to_convert=None, time_units=None,
                          slice_dir_i=None, slice_dir_j=None, m='all',
                          theta=0):
        fld, fld_md = self.get_data(
            time_step, field_units=field_units, axes_units=axes_units,
            axes_to_convert=axes_to_convert, time_units=time_units,
            slice_dir_i=slice_dir_i, slice_dir_j=slice_dir_j, m=m,
            theta=theta, only_metadata=True)
        return fld_md

    def get_geometry(self):
        field_md = self.get_only_metadata(self.timesteps[0])
        return field_md['field']['geometry']

    def _get_data(self, time_step, field_units=None, axes_units=None,
                  time_units=None, slice_i=0.5, slice_j=0.5, slice_dir_i=None,
                  slice_dir_j=None, m='all', theta=0, only_metadata=False):
        raise NotImplementedError


class FolderField(Field):
    def __init__(self, field_name, field_path, field_files, field_timesteps,
                 field_reader, unit_converter, species_name=None):
        super().__init__(field_name, field_timesteps, unit_converter,
                         species_name)
        self.field_path = field_path
        self.field_files = field_files
        self.field_reader = field_reader

    def _get_data(self, time_step, field_units=None, axes_units=None,
                  axes_to_convert=None, time_units=None, slice_i=0.5,
                  slice_j=0.5, slice_dir_i=None, slice_dir_j=None, m='all',
                  theta=0, only_metadata=False):
        file_path = self._get_file_path(time_step)
        fld, fld_md = self.field_reader.read_field(
            file_path, self.field_path, slice_i, slice_j, slice_dir_i,
            slice_dir_j, m, theta, only_metadata)
        # perform unit conversion
        unit_list = [field_units, axes_units, time_units]
        if any(unit is not None for unit in unit_list):
            fld, fld_md  = self.unit_converter.convert_field_units(
                fld, fld_md, target_field_units=field_units,
                target_axes_units=axes_units, axes_to_convert=axes_to_convert,
                target_time_units=time_units)
        return fld, fld_md

    def _get_file_path(self, time_step):
        ts_i = self.timesteps.tolist().index(time_step)
        return self.field_files[ts_i]
    

class DerivedField(Field):
    def __init__(self, field_dict, sim_geometry, sim_params, base_fields):
        self.field_dict = field_dict
        self.sim_geometry = sim_geometry
        self.sim_params = sim_params
        self.base_fields = base_fields
        field_timesteps = get_common_timesteps(base_fields)
        field_name = field_dict['name']
        unit_converter = base_fields[0].unit_converter
        super().__init__(field_name, field_timesteps, unit_converter)

    def _get_data(self, time_step, field_units=None, axes_units=None,
                  axes_to_convert=None, time_units=None, slice_i=0.5,
                  slice_j=0.5, slice_dir_i=None, slice_dir_j=None, m='all',
                  theta=0, only_metadata=False):
        field_data = []
        for field in self.base_fields:
            fld, fld_md = field.get_data(
                time_step, field_units='SI', axes_units=axes_units,
                axes_to_convert=axes_to_convert, time_units=time_units,
                slice_i=slice_i, slice_j=slice_j, slice_dir_i=slice_dir_i,
                slice_dir_j=slice_dir_j, m=m, theta=theta,
                only_metadata=only_metadata)
            field_data.append(fld)
        if not only_metadata:
            fld = self.field_dict['recipe'](field_data, self.sim_geometry,
                                            self.sim_params)
        fld_md['field']['units'] = self.field_dict['units']
        # perform unit conversion
        unit_list = [field_units, axes_units, time_units]
        if any(unit is not None for unit in unit_list):
            fld, fld_md  = self.unit_converter.convert_field_units(
                fld, fld_md, target_field_units=field_units,
                target_axes_units=axes_units, axes_to_convert=axes_to_convert,
                target_time_units=time_units)
        return fld, fld_md
