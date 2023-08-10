"""
This file is part of VisualPIC.

The module contains the definitions of the different folder scanners.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""


import os
from warnings import warn

import numpy as np
from h5py import File as H5F
from .openpmd_data_reader import OpenPMDDataReader

import visualpic.data_reading.field_readers as fr
import visualpic.data_reading.particle_readers as pr
import visualpic.data_handling.unit_converters as uc
from visualpic.data_handling.fields import FolderField
from visualpic.data_handling.particle_species import ParticleSpecies


class FolderScanner():

    "Base class for all folder scanners."

    def get_list_of_fields(self, folder_path):
        """
        Get list of fields in the specified path. Should be implemented in the
        FolderScanner subclass for each simulation code.

        Parameters
        ----------

        folder_path : str
            Path to the folder containing the simulation data.

        Returns
        -------
        A list of FolderField objects
        """
        raise NotImplementedError

    def get_list_of_species(self, folder_path):
        """
        Get list of species in the specified path. Should be implemented in the
        FolderScanner subclass for each simulation code.

        Parameters
        ----------

        folder_path : str
            Path to the folder containing the simulation data.

        Returns
        -------
        A list of ParticleSpecies objects
        """
        raise NotImplementedError


class OpenPMDFolderScanner(FolderScanner):

    "Folder scanner class for openPMD data."

    def __init__(self, opmd_backend='openpmd-api'):
        """
        Initialize the folder scanner and assign corresponding data readers
        and unit converter.

        Parameters
        ----------

        opmd_backend : str
            The backend to be used by the DataReader of the openPMD-viewer.
            Possible values are 'h5py' or 'openpmd-api'.

        """
        self.opmd_reader = OpenPMDDataReader(opmd_backend)
        self.field_reader = fr.OpenPMDFieldReader(self.opmd_reader)
        self.particle_reader = pr.OpenPMDParticleReader(self.opmd_reader)
        self.unit_converter = uc.OpenPMDUnitConverter()

    def get_list_of_fields(self, folder_path):
        """
        Get list of fields in the specified path.

        Parameters
        ----------

        folder_path : str
            Path to the folder containing the simulation data.

        Returns
        -------
        A list of FolderField objects
        """
        field_list = []
        iterations = self.opmd_reader.list_iterations(folder_path)

        # Create dictionary with the necessary data of each field.
        fields = {}
        for it in iterations:
            file = None  # Not needed for openPMD data.
            t, opmd_params = self.opmd_reader.read_openPMD_params(it)
            avail_fields = opmd_params['avail_fields']
            if avail_fields is not None:
                for field in avail_fields:
                    field_metadata = opmd_params['fields_metadata'][field]
                    if field_metadata['type'] == 'vector':
                        field_comps = field_metadata['avail_components']
                        if ((field_metadata['geometry'] == 'thetaMode') and
                                (set(['r', 't']).issubset(field_comps))):
                            field_comps += ['x', 'y']
                        for comp in field_comps:
                            field_path = field + '/' + comp
                            field_name = self._get_standard_visualpic_name(
                                field_path)

                            if field_name not in fields:
                                field_dict = {}
                                field_dict['path'] = field_path
                                field_dict['files'] = [file]
                                field_dict['iterations'] = [it]
                                field_dict['species_name'] = None
                                fields[field_name] = field_dict
                            else:
                                fields[field_name]['files'].append(file)
                                fields[field_name]['iterations'].append(it)

                    else:
                        # The code below tries to identify whether the field is
                        # associated with a particle species. The
                        # implementation was only valid for FBPIC and could
                        # lead to problems in other cases. A better way of
                        # doing this will be implemented once openPMD 2.0 is
                        # released, which adds this feature to the standard.
                        # if '_' in field:
                        #     name_parts = field.split('_')
                        #     field_name = name_parts[0]
                        #     if len(name_parts) > 2:
                        #         species_name = '_'.join(name_parts[1:])
                        #     else:
                        #         species_name = name_parts[1]
                        # else:
                        #     field_name = field
                        #     species_name = None
                        field_name = field
                        species_name = None
                        field_name = self._get_standard_visualpic_name(
                            field_name)
                        if field_name not in fields:
                            field_dict = {}
                            field_dict['path'] = field
                            field_dict['files'] = [file]
                            field_dict['iterations'] = [it]
                            field_dict['species_name'] = species_name
                            fields[field_name] = field_dict
                        else:
                            fields[field_name]['files'].append(file)
                            fields[field_name]['iterations'].append(it)

        # Create all fields.
        for field_name in fields.keys():
            field_list.append(
                FolderField(
                    field_name,
                    fields[field_name]['path'],
                    fields[field_name]['files'],
                    np.array(fields[field_name]['iterations']),
                    self.field_reader,
                    self.unit_converter,
                    species_name=fields[field_name]['species_name'])
            )
        return field_list

    def get_list_of_species(self, folder_path):
        """
        Get list of species in the specified path.

        Parameters
        ----------

        folder_path : str
            Path to the folder containing the simulation data.

        Returns
        -------
        A list of ParticleSpecies objects
        """
        species_list = []
        iterations = self.opmd_reader.list_iterations(folder_path)

        # Create dictionary with the necessary data of each species.
        found_species = {}
        for it in iterations:
            file = None  # Not needed for openPMD data.
            t, opmd_params = self.opmd_reader.read_openPMD_params(it)
            avail_species = opmd_params['avail_species']
            if avail_species is not None:
                for species in avail_species:
                    if species not in found_species:
                        species_dict = {}
                        comps = opmd_params['avail_record_components'][species]
                        for i, comp in enumerate(comps):
                            comps[i] = self._get_standard_visualpic_name(comp)
                        species_dict['comps'] = comps
                        species_dict['files'] = [file]
                        species_dict['iterations'] = [it]
                        found_species[species] = species_dict
                    else:
                        found_species[species]['files'].append(file)
                        found_species[species]['iterations'].append(it)

        # Create all species.
        for species_name in found_species.keys():
            species_list.append(
                ParticleSpecies(
                    species_name,
                    found_species[species_name]['comps'],
                    np.array(found_species[species_name]['iterations']),
                    found_species[species_name]['files'],
                    self.particle_reader,
                    self.unit_converter)
            )
        return species_list

    def _get_standard_visualpic_name(self, opmd_name):
        """
        Translate the name of a field, coordinate or other physical quantities
        from the openPMD standard to the VisualPIC convention.

        Parameters
        ----------

        opmd_name : str
            Name of the variable in openPMD.

        Returns
        -------
        A string with the VisualPIC name.
        """
        opmd_name = opmd_name.lower()
        name_relations = {'e/z': 'Ez',
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
                          'j/t': 'Jt',
                          'rho': 'rho',
                          'a_mod': 'a_mod',
                          'a_phase': 'a_phase',
                          'z': 'z',
                          'x': 'x',
                          'y': 'y',
                          'r': 'r',
                          'uz': 'pz',
                          'ux': 'px',
                          'uy': 'py',
                          'charge': 'q',
                          'mass': 'm',
                          'id': 'tag',
                          'w': 'w'}
        try:
            return name_relations[opmd_name]
        except KeyError:
            warn('Unknown data name {}.'.format(opmd_name))
            return opmd_name
