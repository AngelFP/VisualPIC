"""
This file is part of VisualPIC.

The module contains the definitions of different field classes.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""

import numpy as np
from openpmd_viewer import OpenPMDTimeSeries

from visualpic.helper_functions import get_common_timesteps
from .field_data import FieldData


class Field():
    def __init__(self, field_name, field_timesteps,
                 species_name=None):
        self.field_name = field_name
        self.timesteps = field_timesteps
        self.species_name = species_name

    @property
    def iterations(self):
        return self.timesteps
    
    @property
    def geometry(self):
        return self._get_geometry()

    def get_name(self):
        fld_name = self.field_name
        if self.species_name is not None:
            fld_name += ' [{}]'.format(self.species_name)
        return fld_name

    def get_data(self, iteration, slice_i=0.5,
                 slice_j=0.5, slice_dir_i=None, slice_dir_j=None, m='all',
                 theta=0, max_resolution_3d=None, only_metadata=False):
        raise NotImplementedError

    def _get_geometry(self):
        raise NotImplementedError


class FolderField(Field):
    def __init__(
        self,
        field_name: str,
        component: str,
        timeseries: OpenPMDTimeSeries,
        species_name: str = None
    ):
        super().__init__(
            field_name=field_name,
            field_timesteps=timeseries.fields_iterations[field_name],
            species_name=species_name
        )
        self.component = component
        self.timeseries = timeseries

    def get_data(self, iteration, slice_i=0.5,
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
        return FieldData(
            name=self.field_name,
            component=self.component,
            array=fld,
            metadata=fld_md,
            geometry=self._get_geometry(),
            iteration=iteration,
            time=self._get_time(iteration)
        )
    
    def _get_time(self, iteration):
        field_its = self.timeseries.fields_iterations[self.field_name]
        field_t = self.timeseries.fields_t[self.field_name]
        return field_t[np.where(field_its == iteration)[0][0]]
    
    def _get_geometry(self):
        return self.timeseries.fields_metadata[self.field_name]['geometry']


class DerivedField(Field):
    def __init__(self, field_dict, sim_geometry, sim_params, base_fields):
        self.field_dict = field_dict
        self.sim_geometry = sim_geometry
        self.sim_params = sim_params
        self.base_fields = base_fields
        field_timesteps = get_common_timesteps(base_fields)
        field_name = field_dict['name']
        super().__init__(field_name, field_timesteps)

    def get_data(self, iteration, slice_i=0.5,
                 slice_j=0.5, slice_dir_i=None, slice_dir_j=None, m='all',
                 theta=0, max_resolution_3d=None, only_metadata=False):
        field_data = []
        for field in self.base_fields:
            fld, fld_md = field.get_data(
                iteration,
                slice_i=slice_i, slice_j=slice_j, slice_dir_i=slice_dir_i,
                slice_dir_j=slice_dir_j, m=m, theta=theta,
                max_resolution_3d=max_resolution_3d,
                only_metadata=only_metadata)
            field_data.append(fld)
        if not only_metadata:
            fld = self.field_dict['recipe'](field_data, self.sim_geometry,
                                            self.sim_params)
        fld_md['field']['units'] = self.field_dict['units']
        return fld, fld_md
