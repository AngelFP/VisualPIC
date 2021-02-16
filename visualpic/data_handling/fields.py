"""
This file is part of VisualPIC.

The module contains the definitions of different field classes.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""


from visualpic.helper_functions import get_common_timesteps


class Field():
    def __init__(self, field_name, field_timesteps, unit_converter,
                 species_name=None):
        self.field_name = field_name
        self.timesteps = field_timesteps
        self.species_name = species_name
        self.unit_converter = unit_converter

    def get_name(self):
        fld_name = self.field_name
        if self.species_name is not None:
            fld_name += ' [{}]'.format(self.species_name)
        return fld_name

    def get_data(self, time_step, field_units=None, axes_units=None,
                 axes_to_convert=None, time_units=None, slice_i=0.5,
                 slice_j=0.5, slice_dir_i=None, slice_dir_j=None, m='all',
                 theta=0, max_resolution_3d=None, only_metadata=False):
        raise NotImplementedError

    def get_only_metadata(self, time_step, field_units=None, axes_units=None,
                          axes_to_convert=None, time_units=None,
                          slice_dir_i=None, slice_dir_j=None, m='all',
                          theta=0, max_resolution_3d=None):
        fld, fld_md = self.get_data(
            time_step, field_units=field_units, axes_units=axes_units,
            axes_to_convert=axes_to_convert, time_units=time_units,
            slice_dir_i=slice_dir_i, slice_dir_j=slice_dir_j, m=m,
            theta=theta, max_resolution_3d=max_resolution_3d,
            only_metadata=True)
        return fld_md

    def get_geometry(self):
        field_md = self.get_only_metadata(self.timesteps[0])
        return field_md['field']['geometry']


class FolderField(Field):
    def __init__(
            self, field_name, field_path, timestep_to_files, field_timesteps,
            field_reader, unit_converter, species_name=None):
        super().__init__(field_name, field_timesteps, unit_converter,
                         species_name)
        self.field_path = field_path
        if type(timestep_to_files) is list:
            if len(timestep_to_files) == len(field_timesteps):
                timestep_to_files = dict(
                    zip(field_timesteps, timestep_to_files))
        self.timestep_to_files = timestep_to_files
        self.field_reader = field_reader

    def get_data(self, time_step, field_units=None, axes_units=None,
                 axes_to_convert=None, time_units=None, slice_i=0.5,
                 slice_j=0.5, slice_dir_i=None, slice_dir_j=None, m='all',
                 theta=0, max_resolution_3d=None, only_metadata=False):
        file_path = self._get_file_path(time_step)
        fld, fld_md = self.field_reader.read_field(
            file_path, time_step, self.field_path, slice_i, slice_j,
            slice_dir_i, slice_dir_j, m, theta, max_resolution_3d,
            only_metadata)
        # perform unit conversion
        unit_list = [field_units, axes_units, time_units]
        if any(unit is not None for unit in unit_list):
            fld, fld_md = self.unit_converter.convert_field_units(
                fld, fld_md, target_field_units=field_units,
                target_axes_units=axes_units, axes_to_convert=axes_to_convert,
                target_time_units=time_units)
        return fld, fld_md

    def _get_file_path(self, time_step):
        return self.timestep_to_files[time_step]


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

    def get_data(self, time_step, field_units=None, axes_units=None,
                 axes_to_convert=None, time_units=None, slice_i=0.5,
                 slice_j=0.5, slice_dir_i=None, slice_dir_j=None, m='all',
                 theta=0, max_resolution_3d=None, only_metadata=False):
        field_data = []
        for field in self.base_fields:
            fld, fld_md = field.get_data(
                time_step, field_units='SI',
                slice_i=slice_i, slice_j=slice_j, slice_dir_i=slice_dir_i,
                slice_dir_j=slice_dir_j, m=m, theta=theta,
                max_resolution_3d=max_resolution_3d,
                only_metadata=only_metadata)
            field_data.append(fld)
        if not only_metadata:
            fld = self.field_dict['recipe'](field_data, self.sim_geometry,
                                            self.sim_params)
        fld_md['field']['units'] = self.field_dict['units']
        # perform unit conversion
        unit_list = [field_units, axes_units, time_units]
        if any(unit is not None for unit in unit_list):
            fld, fld_md = self.unit_converter.convert_field_units(
                fld, fld_md, target_field_units=field_units,
                target_axes_units=axes_units, axes_to_convert=axes_to_convert,
                target_time_units=time_units)
        return fld, fld_md
