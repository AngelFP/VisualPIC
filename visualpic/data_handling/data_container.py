"""
This file is part of VisualPIC.

The module contains the DataContainer class.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""
import os
from warnings import warn
from typing import Optional, Union, List, Dict

import numpy as np

from visualpic.data_handling.fields import Field, DerivedField
from visualpic.data_handling.particle_species import ParticleSpecies
from openpmd_viewer import OpenPMDTimeSeries


class DataContainer():
    """Class containing and providing access to all the simulation data.

    Parameters
    ----------
    data_path : str
        Path to the folder containing the simulation data.
    backend : str
        Used only if `simulation_code='openpmd'`. Specifies the backend to
        be used by the DataReader of the openPMD-viewer. Possible values
        are 'h5py' or 'openpmd-api'.
    load_data : bool
        Whether to load the data at initialization. If `False`, the
        `load_data` method must be called manually. By default, True.
    check_all_files : bool
        Whether to check the available data in all files. If disabled, only
        the first iteration is open, and it will be assumed that all other
        iterations have the same available species and fields.
    """
    def __init__(
        self,
        data_path: str = None,
        backend: Optional[str] = 'openpmd-api',
        load_data: Optional[bool] = True,
        check_all_files: Optional[bool] = True,
        *args,
        **kwargs
    ) -> None:
        # Check for inputs following the old v0.5 API.
        data_path, backend = self._check_backwards_compatibility(
            data_path, backend, kwargs
        )
        # We need to give a default value to `data_path` due to backwards
        # compatibility issues. Check however that a value is given.
        assert data_path is not None, ('Missing argument `data_path`.')
        self._path = data_path
        self._backend = backend
        self._ts = None
        self._check_all_files = check_all_files
        if load_data:
            self.load_data()

    def load_data(
        self,
        force_reload: Optional[bool] = False
    ) -> None:
        """Load the data into the data container.

        Parameters
        ----------
        force_reload : bool, optional
            Whether to force the data to be reloaded`, by default False.
        """
        if self._ts is None or force_reload:
            self._ts = OpenPMDTimeSeries(
                self._path,
                check_all_files=self._check_all_files,
                backend=self._backend
            )
            # The openpmd timeseries can reconstruct x and y from r and t
            # in thetaMode geometry.
            for field in self._available_fields_on_diags:
                f_comps = self._ts.fields_metadata[field]['avail_components']
                if set(['r', 't']) <= set(f_comps):
                    f_comps += ['x', 'y']
            self._derived_fields = []

    @property
    def _available_fields_on_diags(self) -> Union[List[str], None]:
        """Get the list of available fields in the diagnostics."""
        return self._ts.avail_fields
    
    @property
    def available_fields(self) -> Union[List[str], None]:
        """Get the list of all available fields."""
        derived_fields = [f.name for f in self._derived_fields]
        return self._available_fields_on_diags + derived_fields

    @property
    def available_field_components(self) -> Dict:
        """Get the components of all available fields."""
        field_comps = {
            field: self._ts.fields_metadata[field]['avail_components']
            for field in self._available_fields_on_diags
        }
        derived_fields = {field.name: [] for field in self._derived_fields}
        return {**field_comps, **derived_fields}

    @property
    def available_species(self) -> List[str]:
        return self._ts.avail_species

    @property
    def available_species_components(self) -> Dict:
        return self._ts.avail_record_components

    @property
    def iterations(self) -> np.ndarray:
        return self._ts.iterations
    
    @property
    def iteration_times(self) -> np.ndarray:
        return self._ts.t
    
    @property
    def geometry(self) -> Optional[str]:
        """Get the simulation geometry.
        
        The geometry is inferred from the fields available in the diagnostics.
        """
        available_geoms = list(self._ts.avail_geom)
        geom_order = ["3dcartesian", "2dcartesian", "thetaMode"]
        sorted_geoms = [
            geom for x in geom_order for geom in available_geoms if geom == x
        ]
        # There are available geometries, return the highest one.
        if sorted_geoms:
            return sorted_geoms[0]

    def get_list_of_fields(
        self,
        include_derived: Optional[bool] = True
    ) -> Union[List[str], None]:
        """Returns a list with the names of all available fields.

        This method is only kept for backward compatibility.
        """
        legacy_fields = []
        for field, comps in self.available_field_components.items():
            if comps:
                for comp in comps:
                    legacy_fields.append(field + comp)
            else:
                legacy_fields.append(field)
        derived_fields = [f.name for f in self._derived_fields]
        if not include_derived:
            legacy_fields = [f for f in legacy_fields if f not in derived_fields]
        return legacy_fields

    def get_list_of_species(
        self,
        required_data: Optional[List] = []
    ) -> List[str]:
        """
        Returns a list with the names of all available particle species.

        Parameters
        ----------
        required_data : str or list of strings
            String or list of strings with the names of the particle components
            and/or fields that the species should contain. If specified,
            only the species containing the required data will be returned.

        """
        species_list = []
        for species, components in self.available_species_components.items():
            if set(required_data) <= set(components):
                species_list.append(species)
        return species_list

    def get_field(
        self,
        name: str,
        component: Optional[str] = None
    ) -> Field:
        """
        Get a specified field from the available ones.

        Parameters
        ----------
        name : str
            Name of the field.
        component : str, optional
            Component of the field to be read.

        Returns
        -------
        Field
        """
        # Check if field name follows the old v0.5 API.
        if (component is None) and (name not in self.available_fields):
            out = self._check_name_for_backward_compatibility(name)
            if out:
                name, component = out
        for field in self._derived_fields:
            if field.name == name:
                return field
        assert name in self.available_fields, (
            f"Field {name} not found. "
            f"Available fields are {self.available_fields}."
        )
        available_components = self.available_field_components[name]
        if component is None:
            assert not available_components, (
                f"Please specify which field component to read. "
                f"Available components are {available_components}."
            )
        else:
            assert component in available_components, (
                f"Component {component} not found in field {name}. "
                f"Available components are {available_components}."
            )
        return Field(
            name=name,
            component=component,
            timeseries=self._ts
        )

    def get_species(
        self,
        species_name: str
    ) -> ParticleSpecies:
        """
        Get a specified particle species from the available ones.

        Parameters
        ----------
        species_name : str
            Name of the particle species.

        Returns
        -------
        ParticleSpecies
        """
        assert species_name in self.available_species, (
            f"Species '{species_name}' not found. "
            f"Available species are {self.available_species}."
        )
        return ParticleSpecies(
            name=species_name,
            timeseries=self._ts
        )

    def add_derived_field(self, derived_field):
        """Adds a derived field.

        Parameters
        ----------
        derived_field : dict
            Dictionary containing the information to build the derived field.
            It needs the following keys:
            'name': a string with the name to the derived field.
            'units': a string with the units of the field.
            'requirements': a dict containing the list of required fields
                with the geometry type of the data as keys.
            'recipe': a callable function to calculate the derived field
                from the required fields.
        """
        sim_geometry = self.geometry
        if sim_geometry is not None:
            folder_field_names = self.get_list_of_fields(include_derived=False)
            required_fields = derived_field['requirements'][sim_geometry]
            if set(required_fields).issubset(folder_field_names):
                base_fields = []
                for field_name in required_fields:
                    base_fields.append(self.get_field(field_name))
            self._derived_fields.append(
                DerivedField(derived_field, sim_geometry, base_fields)
            )

    def _check_backwards_compatibility(self, data_path, backend, kwargs):
        """Check for inputs following old v0.5 API

        If any old inputs are found, this method will notify the user and try
        to correct them to allow for backwards compatibility.
        """
        if data_path is not None:
            if not os.path.exists(os.path.dirname(data_path)):
                # `simulation_code` given as arg.
                if data_path.lower() in ['openpmd', 'osiris', 'hipace']:
                    self._check_data_format(data_path.lower())
                    # The code below is only reached if `openpmd` has been
                    # requested. Thus, no need to handle `plasma_density`.
                    # `data_folder_path` given as arg.
                    data_path = backend
                    backend = 'openpmd-api'
                    # `laser_wavelength` and `opmd_backend` cannot be given as
                    # args for openPMD data (because they where after
                    # `plasma_density`).
        elif 'simulation_code' in kwargs:
            self._check_data_format(kwargs['simulation_code'].lower())
        if 'data_folder_path' in kwargs:
            warn(
                '`data_folder_path` has been renamed to `data_path` '
                'since v0.6. This name will be fully deprecated in '
                'future versions. Please update this parameter.'
            )
            data_path = kwargs['data_folder_path']
        if 'laser_wavelength' in kwargs:
            warn(
                '`laser_wavelength` parameter no longer used since '
                'v0.6. It will be ignored.'
            )
        if 'opmd_backend' in kwargs:
            warn(
                '`opmd_backend` has been renamed to `backend` since '
                'v0.6. This name will be fully deprecated in future '
                'versions. Please update this parameter.'
            )
            backend = kwargs['opmd_backend']
        return data_path, backend

    def _check_data_format(self, simulation_code):
        """Check that no deprecated data format is requested.

        This is needed to maintain compatibility with the old v0.5 API.
        The user will be notified and, if an unsupported format is requested,
        an error will be raised.
        """
        warn(
            "For VisualPIC v0.6 and higher only openPMD data is "
            "supported. The `simulation_code` parameter has "
            "therefore been removed and should not be provided."
        )
        if simulation_code.lower() in ['osiris', 'hipace']:
            raise ValueError(
                "From version 0.6, {simulation_code} is no longer "
                "supported."
            )

    def _check_name_for_backward_compatibility(self, field_name):
        """If field name follows old API, separate into name and component."""
        old_name_relations = {
            'e/z': 'Ez',
            'e/x': 'Ex',
            'e/y': 'Ey',
            'e/r': 'Er',
            'e/t': 'Et',
            'b/z': 'Bz',
            'b/x': 'Bx',
            'b/y': 'By',
            'b/r': 'Br',
            'b/t': 'Bt',
            'j/z': 'Jz',
            'j/x': 'Jx',
            'j/y': 'Jy',
            'j/r': 'Jr',
            'j/t': 'Jt'
        }
        if field_name in old_name_relations.values():
            name = field_name[0]
            comp = field_name[1]
            return name, comp
