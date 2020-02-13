""" Module for the DataContainer class """

from VisualPIC.data_reading.folder_scanners import (OsirisFolderScanner,
                                                    OpenPMDFolderScanner,
                                                    HiPACEFolderScanner)


class DataContainer():
    
    """Class containing a providing access to all the simulation data"""

    def __init__(self, simulation_code, data_folder_path, plasma_density=None):
        self.simulation_code = simulation_code
        self.data_folder_path = data_folder_path
        self.plasma_density = plasma_density
        self.folder_scanner = self._get_folder_scanner(simulation_code,
                                                       plasma_density)

    def load_data(self):
        self.folder_fields = self.folder_scanner.get_list_of_fields(
            self.data_folder_path)
        self.particle_species = self.folder_scanner.get_list_of_species(
            self.data_folder_path)

    def get_list_of_fields(self):
        fields_list = []
        for field in self.folder_fields:
            fld_name = field.field_name
            fld_species = field.species_name
            if fld_species is not None:
                fld_name += ' [{}]'.format(fld_species)
            fields_list.append(fld_name)
        return fields_list

    def get_list_of_particle_species(self):
        species_list = []
        for species in self.particle_species:
            species_list.append(species.species_name)
        return species_list

    def get_field(self, field_name, species_name=None):
        for field in self.folder_fields:
            if (field_name == field.field_name and
                species_name == field.species_name):
                return field

    def get_particle_species(self, species_name):
        for species in self.particle_species:
            if species_name == species.species_name:
                return species

    def _get_folder_scanner(self, simulation_code, plasma_density=None):
        if simulation_code == 'Osiris':
            return OsirisFolderScanner(plasma_density=plasma_density)
        elif simulation_code == 'HiPACE':
            return HiPACEFolderScanner(plasma_density=plasma_density)
        elif simulation_code == 'openPMD':
            return OpenPMDFolderScanner()
        else:
            raise ValueError("Unsupported code '{}'.".format(simulation_code) +
                             " Possible values are 'Osiris', 'HiPACE' or " +
                             "'openPMD'.")

