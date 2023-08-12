"""
This file is part of VisualPIC.

The module contains the definitions of different field classes.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""

import numpy as np
from openpmd_viewer import OpenPMDTimeSeries

from .field_data import FieldData


class Field():
    def __init__(
        self,
        name: str,
        component: str,
        timeseries: OpenPMDTimeSeries,
        species_name: str = None
    ) -> None:
        self._name = name
        self._iterations = timeseries.fields_iterations[name]
        self._species_name = species_name
        self._component = component
        self._ts = timeseries

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def iterations(self) -> np.ndarray:
        return self._iterations
    
    @property
    def timesteps(self) -> np.ndarray:
        return self.iterations
    
    @property
    def geometry(self) -> str:
        return self._ts.fields_metadata[self._name]['geometry']
    
    @property
    def field_name(self) -> str:
        # TODO: deprecate
        return self.name
    
    @property
    def species_name(self) -> str:
        # TODO: deprecate
        return None

    def get_name(self) -> str:
        fld_name = self._name
        if self._species_name is not None:
            fld_name += ' [{}]'.format(self._species_name)
        return fld_name

    def get_data(
            self,
            iteration,
            slice_i=0.5,
            slice_j=0.5,
            slice_dir_i=None,
            slice_dir_j=None,
            m='all',
            theta=0,
            max_resolution_3d=None,
            only_metadata=False
        ) -> FieldData:
        fld, fld_md = self._ts.get_field(
            field=self._name,
            coord=self._component,
            iteration=iteration,
            m=m,
            theta=theta,
            slice_across=slice_dir_i,
            slice_relative_position=slice_i,
            max_resolution_3d=max_resolution_3d
        )
        return FieldData(
            name=self._name,
            component=self._component,
            array=fld,
            metadata=fld_md,
            geometry=self.geometry,
            iteration=iteration,
            time=self._get_time(iteration)
        )
    
    def get_geometry(self):
        # TODO: deprecate
        return self.geometry
    
    def _get_time(self, iteration) -> float:
        field_its = self._ts.fields_iterations[self._name]
        field_t = self._ts.fields_t[self._name]
        return field_t[np.where(field_its == iteration)[0][0]]
