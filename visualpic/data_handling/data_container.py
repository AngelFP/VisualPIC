"""
This file is part of VisualPIC.

The module contains the DataContainer class.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""


from visualpic.data_handling.derived_field_definitions import (
    derived_field_definitions)
from visualpic.data_handling.fields import DerivedField
from visualpic.data_handling.particle_species import ParticleSpecies
from visualpic.data_reading.folder_scanners import (
    OsirisFolderScanner, OpenPMDFolderScanner, HiPACEFolderScanner)


class DataContainer():

    """Class containing a providing access to all the simulation data"""

    def __init__(self, simulation_code, data_folder_path, plasma_density=None,
                 laser_wavelength=0.8e-6, opmd_backend='openpmd-api'):
        """
        Initialize the data container.

        Parameters
        ----------

        simulation_code : str
            Name of the simulation code from which the data comes from.
            Possible values are 'osiris, 'hipace' or 'openpmd' for any
            openPMD-compliant code.

        data_folder_path : str
            Path to the folder containing the simulation data.

        plasma_density : float
            (Optional) Value of the plasma density in m^{-3}. Needed only for
            'osiris' and 'hipace' data to allow for conversion to
            non-normalized units.

        laser_wavelength : float
            Wavelength (in metres) of the laser in the simulation. Needed for
            computing the normalized vector potential.

        opmd_backend : str
            Used only if `simulation_code='openpmd'`. Specifies the backend to
            be used by the DataReader of the openPMD-viewer. Possible values
            are 'h5py' or 'openpmd-api'.

        """
        self.simulation_code = simulation_code.lower()
        self.data_folder_path = data_folder_path
        self.sim_params = {'n_p': plasma_density,
                           'lambda_0': laser_wavelength}
        self.opmd_backend = opmd_backend
        self._set_folder_scanner()
        self.folder_fields = []
        self.particle_species = []
        self.derived_fields = []

    def load_data(self, force_reload=False, iterations=None):
        """Load the data into the data container."""
        if not self.folder_fields or force_reload:
            self.folder_fields = self.folder_scanner.get_list_of_fields(
                self.data_folder_path, iterations)
        if not self.particle_species or force_reload:
            self.particle_species = self.folder_scanner.get_list_of_species(
                self.data_folder_path, iterations)
            self._add_associated_species_fields()
        if not self.derived_fields or force_reload:
            self._generate_derived_fields()

    def get_list_of_fields(self, include_derived=True):
        """Returns a list with the names of all available fields."""
        fields_list = []
        available_fields = self.folder_fields
        if include_derived:
            available_fields = available_fields + self.derived_fields
        for field in available_fields:
            fld_name = field.field_name
            fld_species = field.species_name
            if fld_species is not None:
                fld_name += ' [{}]'.format(fld_species)
            fields_list.append(fld_name)
        return fields_list

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
        for species in self.particle_species:
            if species.contains(required_data):
                species_list.append(species.species_name)
        return species_list

    def get_field(self, field_name, species_name=None):
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
        for field in self.folder_fields + self.derived_fields:
            if (field_name == field.field_name and
                    species_name == field.species_name):
                return field
        # raise error if no field has been found
        if species_name is not None:
            field_name = field_name + species_name
        available_fields = self.get_list_of_fields()
        raise ValueError("Field '{}' not found. ".format(field_name) +
                         "Available fields are {}.".format(available_fields))

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
        for species in self.particle_species:
            if species_name == species.species_name:
                return species
        # raise error if no species has been found
        available_species = self.get_list_of_species()
        raise ValueError("Species '{}' not found. ".format(species_name) +
                         "Available species are {}.".format(available_species))

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
        sim_geometry = self._get_simulation_geometry()
        if sim_geometry is not None:
            folder_field_names = self.get_list_of_fields(include_derived=False)
            required_fields = derived_field['requirements'][sim_geometry]
            if set(required_fields).issubset(folder_field_names):
                base_fields = []
                for field_name in required_fields:
                    base_fields.append(self.get_field(field_name))

                self.derived_fields.append(DerivedField(
                    derived_field, sim_geometry, self.sim_params,
                    base_fields))

    def _set_folder_scanner(self):
        """Return the folder scanner corresponding to the simulation code."""
        plasma_density = self.sim_params['n_p']
        sim_code = self.simulation_code
        if sim_code == 'osiris':
            fs = OsirisFolderScanner(plasma_density=plasma_density)
        elif sim_code == 'hipace':
            fs = HiPACEFolderScanner(plasma_density=plasma_density)
        elif sim_code == 'openpmd':
            fs = OpenPMDFolderScanner(opmd_backend=self.opmd_backend)
        else:
            raise ValueError("Unsupported code '{}'.".format(sim_code) +
                             " Possible values are 'osiris', 'hipace' or " +
                             "'openpmd'.")
        self.folder_scanner = fs

    def _generate_derived_fields(self):
        """Generate the predefined derived fields."""
        for derived_field in derived_field_definitions:
            self.add_derived_field(derived_field)

    def _get_simulation_geometry(self):
        """Returns a string with the geometry used in the simulation."""
        if len(self.folder_fields) > 0:
            time_steps = self.folder_fields[0].timesteps
            fld_md = self.folder_fields[0].get_only_metadata(time_steps[0])
            return fld_md['field']['geometry']
        else:
            return None

    def _add_associated_species_fields(self):
        """
        Checks if any field in the data container is associated to a particle
        species. If so, the field is added to the species. In case that no
        ParticleSpecies object exists (because no particle data is available
        for this species), a new instance of ParticleSpecies is created
        containing only the associated field.

        """
        for field in self.folder_fields + self.derived_fields:
            if field.species_name is not None:
                try:
                    species = self.get_species(field.species_name)
                except:
                    species = ParticleSpecies(
                        field.species_name, [], [], [], None, None)
                    self.particle_species.append(species)
                species.add_associated_field(field)
