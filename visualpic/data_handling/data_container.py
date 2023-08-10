"""
This file is part of VisualPIC.

The module contains the DataContainer class.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""


from visualpic.data_handling.derived_field_definitions import (
    derived_field_definitions)
from visualpic.data_handling.fields import DerivedField, FolderField
from visualpic.data_handling.particle_species import ParticleSpecies
from visualpic.data_reading.folder_scanners import OpenPMDFolderScanner
from openpmd_viewer import OpenPMDTimeSeries


class DataContainer():

    """Class containing a providing access to all the simulation data"""

    def __init__(self, path,
                 laser_wavelength=0.8e-6, backend='openpmd-api',
                 load_data=True):
        """
        Initialize the data container.

        Parameters
        ----------

        simulation_code : str
            Name of the simulation code from which the data comes from.
            Possible values are 'osiris, 'hipace' or 'openpmd' for any
            openPMD-compliant code.

        path : str
            Path to the folder containing the simulation data.

        plasma_density : float
            (Optional) Value of the plasma density in m^{-3}. Needed only for
            'osiris' and 'hipace' data to allow for conversion to
            non-normalized units.

        laser_wavelength : float
            Wavelength (in metres) of the laser in the simulation. Needed for
            computing the normalized vector potential.

        backend : str
            Used only if `simulation_code='openpmd'`. Specifies the backend to
            be used by the DataReader of the openPMD-viewer. Possible values
            are 'h5py' or 'openpmd-api'.

        """
        self.path = path
        self.sim_params = {'lambda_0': laser_wavelength}
        self.backend = backend
        self._set_folder_scanner()
        self.folder_fields = []
        self.particle_species = []
        self.derived_fields = []
        self._ts = None
        if load_data:
            self.load_data()

    def load_data(self, force_reload=False):
        """Load the data into the data container."""
        if self._ts is None or force_reload:
            self._ts = OpenPMDTimeSeries(
                self.path,
                check_all_files=True,
                backend=self.backend
            )

    @property
    def available_fields(self):
        return self._ts.avail_fields
    
    @property
    def available_field_components(self):
        return {field: self._ts.fields_metadata[field]['avail_components']
                for field in self.available_fields}

    @property
    def available_species(self):
        return self._ts.avail_species
    
    @property
    def available_species_components(self):
        return self._ts.avail_record_components

    def get_list_of_fields(self, include_derived=True):
        """Returns a list with the names of all available fields."""
        return self.available_fields

    def get_list_of_species(self, required_data=[]):
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

    def get_field(self, name, component=None, species_name=None):
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
        A FolderField object containing the specified field.
        """
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
        return FolderField(
            field_name=name,
            component=component,
            timeseries=self._ts,
            species_name=species_name
        )

    def get_species(self, species_name):
        """
        Get a specified particle species from the available ones.

        Parameters
        ----------

        species_name : str
            Name of the particle species.

        Returns
        -------
        A ParticleSpecies object containing the specified species.
        """
        assert species_name in self.available_species, (
            f"Species '{species_name}' not found. "
            f"Available species are {self.available_species}."
        )
        return ParticleSpecies(
            species_name=species_name,
            timeseries=self._ts
        )

    def _set_folder_scanner(self):
        """Return the folder scanner corresponding to the simulation code."""
        self.folder_scanner = OpenPMDFolderScanner(opmd_backend=self.backend)