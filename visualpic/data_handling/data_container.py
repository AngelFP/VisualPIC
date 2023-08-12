"""
This file is part of VisualPIC.

The module contains the DataContainer class.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""
import os
from typing import Optional, Union, List, Dict

from visualpic.data_handling.fields import Field
from visualpic.data_handling.particle_species import ParticleSpecies
from openpmd_viewer import OpenPMDTimeSeries


class DataContainer():
    """Class containing a providing access to all the simulation data.    

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
    """
    def __init__(
        self,
        data_path=None,
        backend='openpmd-api',
        load_data=True,
        *args,
        **kwargs
    ):
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
                check_all_files=True,
                backend=self._backend
            )

    @property
    def available_fields(self) -> Union[List[str], None]:
        return self._ts.avail_fields

    @property
    def available_field_components(self) -> Dict:
        return {field: self._ts.fields_metadata[field]['avail_components']
                for field in self.available_fields}

    @property
    def available_species(self) -> List[str]:
        return self._ts.avail_species

    @property
    def available_species_components(self) -> Dict:
        return self._ts.avail_record_components

    def get_list_of_fields(
        self,
        include_derived: Optional[bool] = True
    ) -> Union[List[str], None]:
        """Returns a list with the names of all available fields."""
        # TODO: deprecate argument.
        return self.available_fields

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
        component: Optional[str] = None,
        species_name: Optional[str] = None,
    ) -> Field:
        """
        Get a specified field from the available ones.

        Parameters
        ----------
        field_name : str
            Name of the field (in VisualPIC convention).
        species_name : str
            (Optional) Name of the particle species to which the field belongs.
            Only needed if the field actually belongs to a species.

        Returns
        -------
        Field
        """
        # Check if field name follows the old v0.5 API.
        if (component is None) and (name not in self.available_fields):
            out = self._check_name_for_backward_compatibility(name)
            if out:
                name, component = out
        assert name in self.available_fields, (
            f"Field {name} not found. "
            f"Available fields are {self.available_fields}."
        )
        available_components = self.available_field_components[name]
        if component is None:
            assert not available_components
        else:
            assert component in available_components, (
                f"Component {component} not found in field {name}. "
                f"Available components are {available_components}."
        )
        return Field(
            field_name=name,
            component=component,
            timeseries=self._ts,
            species_name=species_name
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
            species_name=species_name,
            timeseries=self._ts
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
                    if os.path.exists(os.path.dirname(backend)):
                        data_path = backend
                    # `laser_wavelength` and `opmd_backend` cannot be given as
                    # args for openPMD data (because they where after
                    # `plasma_density`).
        elif 'simulation_code' in kwargs:
            self._check_data_format(kwargs['simulation_code'].lower())
        if 'data_folder_path' in kwargs:
            print(
                '`data_folder_path` has been renamed to `data_path` '
                'since v0.6. This name will be fully deprecated in '
                'future versions. Please update this parameter.'
            )
            data_path = kwargs['data_folder_path']
        if 'laser_wavelength' in kwargs:
            print(
                '`laser_wavelength` parameter no longer used since '
                'v0.6. It will be ignored.'
            )
        if 'opmd_backend' in kwargs:
            print(
                '`opmd_backend` has been renamed to `backend` since '
                'v0.6. This name will be fully deprecated in future '
                'versions. Please update this parameter.'
            )
            backend = kwargs['opmd_backend']
        else:
            backend = 'openpmd-api'
        return data_path, backend

    def _check_data_format(self, simulation_code):
        """Check that no deprecated data format is requested.
        
        This is needed to maintain compatibility with the old v0.5 API.
        The user will be notified and, if an unsupported format is requested,
        an error will be raised.
        """
        print(
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
