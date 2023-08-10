"""
This file is part of VisualPIC.

The module contains the definitions of different field classes.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""

from openpmd_viewer import OpenPMDTimeSeries

from visualpic.helper_functions import get_common_timesteps
from .unit_converters import OpenPMDUnitConverter


class Field():
    def __init__(self, field_name, field_timesteps, unit_converter,
                 species_name=None):
        self.field_name = field_name
        self.timesteps = field_timesteps
        self.species_name = species_name
        self.unit_converter = unit_converter

    @property
    def iterations(self):
        return self.timesteps

    def get_name(self):
        fld_name = self.field_name
        if self.species_name is not None:
            fld_name += ' [{}]'.format(self.species_name)
        return fld_name

    def get_data(self, iteration, field_units=None, axes_units=None,
                 axes_to_convert=None, time_units=None, slice_i=0.5,
                 slice_j=0.5, slice_dir_i=None, slice_dir_j=None, m='all',
                 theta=0, max_resolution_3d=None, only_metadata=False):
        raise NotImplementedError

    def get_only_metadata(self, iteration, field_units=None, axes_units=None,
                          axes_to_convert=None, time_units=None,
                          slice_dir_i=None, slice_dir_j=None, m='all',
                          theta=0, max_resolution_3d=None):
        fld, fld_md = self.get_data(
            iteration, field_units=field_units, axes_units=axes_units,
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
        self,
        field_name: str,
        component: str,
        timeseries: OpenPMDTimeSeries,
        unit_converter: OpenPMDUnitConverter,
        species_name: str = None
    ):
        super().__init__(
            field_name=field_name,
            field_timesteps=timeseries.iterations,
            unit_converter=unit_converter,
            species_name=species_name
        )
        self.component = component
        self.timeseries = timeseries

    def get_data(self, iteration, field_units=None, axes_units=None,
                 axes_to_convert=None, time_units=None, slice_i=0.5,
                 slice_j=0.5, slice_dir_i=None, slice_dir_j=None, m='all',
                 theta=0, max_resolution_3d=None, only_metadata=False):
        fld, fld_md = self.timeseries.get_field(
            field=self.field_name,
            coord=self.component,
            iteration=iteration,
            m=m,
            theta=theta,
            slice_across=slice_dir_i,
            slice_relative_position=slice_i,
            max_resolution_3d=max_resolution_3d
        )
        # perform unit conversion
        unit_list = [field_units, axes_units, time_units]
        if any(unit is not None for unit in unit_list):
            fld, fld_md = self.unit_converter.convert_field_units(
                fld, fld_md, target_field_units=field_units,
                target_axes_units=axes_units, axes_to_convert=axes_to_convert,
                target_time_units=time_units)
        return fld, fld_md


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

    def get_data(self, iteration, field_units=None, axes_units=None,
                 axes_to_convert=None, time_units=None, slice_i=0.5,
                 slice_j=0.5, slice_dir_i=None, slice_dir_j=None, m='all',
                 theta=0, max_resolution_3d=None, only_metadata=False):
        field_data = []
        for field in self.base_fields:
            fld, fld_md = field.get_data(
                iteration, field_units='SI',
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
