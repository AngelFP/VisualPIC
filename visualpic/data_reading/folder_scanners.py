# -*- coding: utf-8 -*-

#Copyright 2016-2020 Angel Ferran Pousa, DESY
#
#This file is part of VisualPIC.
#
#VisualPIC is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#VisualPIC is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with VisualPIC.  If not, see <http://www.gnu.org/licenses/>.


import os

import numpy as np
from h5py import File as H5F
from openpmd_viewer.openpmd_timeseries.utilities import list_h5_files
from openpmd_viewer.openpmd_timeseries.data_reader.params_reader import (
    read_openPMD_params)

import VisualPIC.data_reading.field_readers as fr
import VisualPIC.data_reading.particle_readers as pr
import VisualPIC.data_handling.unit_converters as uc
from VisualPIC.data_handling.fields import FolderField
from VisualPIC.data_handling.particle_species import ParticleSpecies


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

    def __init__(self):
        """
        Initialize the folder scanner and assign corresponding data readers
        and unit converter.
        """
        self.field_reader = fr.OpenPMDFieldReader()
        self.particle_reader = pr.OpenPMDParticleReader()
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
        h5_files, iterations = list_h5_files(folder_path)
        t, opmd_params = read_openPMD_params(h5_files[0])
        avail_fields = opmd_params['avail_fields']
        if avail_fields is not None:
            for field in avail_fields:
                field_metadata = opmd_params['fields_metadata'][field]
                if field_metadata['type'] == 'vector':
                    field_comps = field_metadata['axis_labels']
                    if field_metadata['geometry'] == 'thetaMode':
                        field_comps += ['x', 'y', 't']
                    for comp in field_comps:
                        field_path = field + '/' + comp
                        field_name = self._get_standard_visualpic_name(
                            field_path)
                        field_list.append(
                            FolderField(field_name, field_path, h5_files,
                                        iterations, self.field_reader,
                                        self.unit_converter))
                else:
                    field_list.append(
                            FolderField(field, field, h5_files, iterations,
                                        self.field_reader,
                                        self.unit_converter))
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
        h5_files, iterations = list_h5_files(folder_path)
        t, opmd_params = read_openPMD_params(h5_files[0])
        avail_species = opmd_params['avail_species']
        if avail_species is not None:
            for species in avail_species:
                species_comps = opmd_params['avail_record_components'][species]
                for i, comp in enumerate(species_comps):
                    species_comps[i] = self._get_standard_visualpic_name(comp)
                species_list.append(
                    ParticleSpecies(species, species_comps, iterations,
                                    h5_files, self.particle_reader,
                                    self.unit_converter))
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
        name_relations = {'E/z': 'Ez',
                          'E/x': 'Ex',
                          'E/y': 'Ey',
                          'E/r': 'Er',
                          'E/t': 'Et',
                          'B/z': 'Bz',
                          'B/x': 'Bx',
                          'B/y': 'By',
                          'B/r': 'Br',
                          'B/t': 'Bt',
                          'J/z': 'Jz',
                          'J/x': 'Jx',
                          'J/y': 'Jy',
                          'J/r': 'Jr',
                          'J/t': 'Jt',
                          'rho': 'rho',
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
            print('Unknown data name {}.'.format(opmd_name))
            return opmd_name


class OsirisFolderScanner(FolderScanner):
    def __init__(self, plasma_density=None):
        """
        Initialize the folder scanner and assign corresponding data readers
        and unit converter.

        Parameters
        ----------

        plasma_density : float
            (Optional) Value of the plasma density in m^{-3}. Needed only to
            convert data to non-normalized units.
        """
        self.field_reader = fr.OsirisFieldReader()
        self.particle_reader = pr.OsirisParticleReader()
        self.unit_converter = uc.OsirisUnitConverter(plasma_density)

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
        folders_in_path = os.listdir(folder_path)
        for folder in folders_in_path:
            if folder == "DENSITY":
                subdir = os.path.join(folder_path, folder)
                available_species = os.listdir(subdir)
                for species in available_species:
                    species_folder = os.path.join(subdir, species)
                    if os.path.isdir(species_folder):
                        species_fields = os.listdir(species_folder)
                        for field in species_fields:
                            field_folder = os.path.join(species_folder, field)
                            if os.path.isdir(field_folder):
                                field_list.append(self._create_field(
                                    field, field_folder, species))
            if folder == "FLD":
                subdir = os.path.join(folder_path, folder)
                domain_fields = os.listdir(subdir)
                for field in domain_fields:
                    field_folder = os.path.join(subdir, field)
                    if os.path.isdir(field_folder):
                        field_list.append(
                            self._create_field(field, field_folder))
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
        folders_in_path = os.listdir(folder_path)
        for folder in folders_in_path:
            if folder == "RAW":
                subdir = os.path.join(folder_path, folder)
                available_species = os.listdir(subdir)
                for species in available_species:
                    species_folder = os.path.join(subdir, species)
                    if os.path.isdir(species_folder):
                        species_fields = os.listdir(species_folder)
                        species_list.append(self._create_species(
                                    species, species_folder))
        return species_list

    def _create_field(self, field_name, field_folder, species_name=None):
        """
        Create a FolderField object with the specified information.

        Parameters
        ----------

        field_name : str
            Name of the field according to the VisualPIC convention.

        field_folder : str
            Path to the folder containing the field data files.

        species_name : str
            (Optional) Name of the particle species to which the field belongs.
            Only needed if the field actually belongs to a species.
            For example, for the charge density.

        Returns
        -------
        A FolderField object
        """
        field_path = self._get_field_path(field_name)
        osiris_field_name = self._get_osiris_field_name(
            field_name)
        field_name = self._get_standard_visualpic_name(
            osiris_field_name)
        fld_files, time_steps = self._get_files_and_timesteps(
            field_folder)
        return FolderField(field_name, field_path, fld_files,
                           time_steps, self.field_reader,
                           self.unit_converter, species_name)

    def _create_species(self, species_name, species_folder):
        """
        Create a ParticleSpecies object with the specified information.

        Parameters
        ----------

        species_name : str
            Name of the particle species.

        species_folder : str
            Path to the folder containing the species data files.

        Returns
        -------
        A ParticleSpecies object
        """
        species_files, time_steps = self._get_files_and_timesteps(
            species_folder)
        species_components = []
        file_path = species_files[0]
        file_content = H5F(file_path, 'r')
        for dataset_name in list(file_content):
            species_components.append(
                self._get_standard_visualpic_name(dataset_name))
        return ParticleSpecies(species_name, species_components, time_steps,
                               species_files, self.particle_reader,
                               self.unit_converter)

    def _get_field_path(self, field_folder_name):
        return '/' + self._get_osiris_field_name(field_folder_name)

    def _get_standard_visualpic_name(self, osiris_name):
        """
        Translate the name of a field, coordinate or other physical quantities
        from the OSIRIS naming to the VisualPIC convention.

        Parameters
        ----------

        osiris_name : str
            Name of the variable in OSIRIS.

        Returns
        -------
        A string with the VisualPIC name.
        """
        name_relations = {'e1': 'Ez',
                          'e2': 'Ex',
                          'e3': 'Ey',
                          'b1': 'Bz',
                          'b2': 'Bx',
                          'b3': 'By',
                          'charge': 'rho',
                          'x1': 'z',
                          'x2': 'x',
                          'x3': 'y',
                          'p1': 'pz',
                          'p2': 'px',
                          'p3': 'py',
                          'q': 'q',
                          'ene': 'ekin',
                          'tag': 'tag'}

        try:
            return name_relations[osiris_name]
        except KeyError:
            print('Unknown data name {}.'.format(osiris_name))
            return osiris_name

    def _get_osiris_field_name(self, field_folder_name):
        """
        Returns the OSIRIS field name, removing the '-savg' suffix if
        neccesary
        """
        return field_folder_name.replace('-savg', '')

    def _get_files_and_timesteps(self, field_folder_path):
        """
        Get a list of all field files and timesteps.

        Parameters
        ----------

        field_folder_path : str
            Path to the folder containing the field files.

        Returns
        -------
        A tuple with a an array of file paths and and array of timesteps.
        """
        all_files = os.listdir(field_folder_path)
        h5_files = list()
        for file in all_files:
            if file.endswith(".h5"):
                h5_files.append(os.path.join(field_folder_path, file))
        time_steps = np.zeros(len(h5_files))
        for i, file in enumerate(h5_files):
            time_step = int(file[-9:-3])
            time_steps[i] = time_step
        sort_i = np.argsort(time_steps)
        time_steps = time_steps[sort_i]
        h5_files = np.array(h5_files)[sort_i]
        return h5_files, time_steps


class HiPACEFolderScanner(FolderScanner):
    def __init__(self, plasma_density=None):
        """
        Initialize the folder scanner and assign corresponding data readers
        and unit converter.

        Parameters
        ----------

        plasma_density : float
            (Optional) Value of the plasma density in m^{-3}. Needed only to
            convert data to non-normalized units.
        """
        self.field_reader = fr.HiPACEFieldReader()
        self.particle_reader = pr.HiPACEParticleReader()
        self.unit_converter = uc.HiPACEUnitConverter(plasma_density)

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
        files_in_folder = sorted(os.listdir(folder_path))
        # scan for names of fields and species
        species_names = []
        field_names = []
        for file in files_in_folder:
            if file.endswith('.h5'):
                if 'density' in file:
                    species_name = file.split('_')[1]
                    if species_name not in species_names:
                        species_names.append(species_name)
                elif 'field' in file:
                    field_name = file.split('_')[1]
                    if field_name not in field_names:
                        field_names.append(field_name)
        # get available fields
        available_fields = []
        for species in species_names:
            available_fields.append(
                self._create_field(folder_path, files_in_folder, 'density',
                                   species, species_name=species))
        for field in field_names:
            available_fields.append(
                self._create_field(folder_path, files_in_folder, 'field',
                                   field))
        return available_fields

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
        files_in_folder = sorted(os.listdir(folder_path))
        species_names = []
        for file in files_in_folder:
            if file.endswith('.h5'):
                if 'raw' in file:
                    species_name = file.split('_')[1]
                    if species_name not in species_names:
                        species_names.append(species_name)
        available_species = []
        for species in species_names:
            available_species.append(
                self._create_species(folder_path, files_in_folder, species))
        return available_species

    def _create_field(self, folder_path, files_in_folder, prefix, name,
                      species_name=None):
        """
        Create a FolderField object with the specified information.

        Parameters
        ----------

        folder_path : str
            Path to the folder containing the data files.

        files_in_folder : list
            List of all data files in the HiPACE simulation folder (not only
            those of the current field).

        prefix : str
            HiPACE files have a prefix 'field', 'density' or 'raw' depending
            on the data type. Possible values here are 'field' or 'density'.

        name : str
            For 'field' data this is the name of the field. For 'density' data
            it corresponds to the species name.

        species_name : str
            (Optional) Name of the particle species to which the field belongs.
            Only needed if the field actually belongs to a species.
            For example, for the charge density.

        Returns
        -------
        A FolderField object.
        """
        field_files, time_steps = self._get_files_and_timesteps(
                folder_path, files_in_folder, prefix, name)
        if prefix == 'density':
            vpic_name = self._get_standard_visualpic_name('density')
        else:
            vpic_name = self._get_standard_visualpic_name(name)
        return FolderField(vpic_name, name, field_files, time_steps,
                           self.field_reader, self.unit_converter,
                           species_name)

    def _create_species(self, folder_path, files_in_folder, species_name):
        """
        Create a ParticleSpecies object with the specified information.

        Parameters
        ----------

        folder_path : str
            Path to the folder containing the data files.

        files_in_folder : list
            List of all data files in the HiPACE simulation folder (not only
            those of the current field).

        species_name : str
            Name of the particle species.

        Returns
        -------
        A ParticleSpecies object.
        """
        species_files, time_steps = self._get_files_and_timesteps(
            folder_path, files_in_folder, 'raw', species_name)
        species_components = []
        file_path = species_files[0]
        file_content = H5F(file_path, 'r')
        for dataset_name in list(file_content):
            species_components.append(
                self._get_standard_visualpic_name(dataset_name))
        return ParticleSpecies(species_name, species_components, time_steps,
                               species_files, self.particle_reader,
                               self.unit_converter)

    def _get_standard_visualpic_name(self, hipace_name):
        """
        Translate the name of a field, coordinate or other physical quantities
        from the HiPACE naming to the VisualPIC convention.

        Parameters
        ----------

        hipace_name : str
            Name of the variable in HiPACE.

        Returns
        -------
        A string with the VisualPIC name.
        """
        name_relations = {'Ez': 'Ez',
                          'ExmBy': 'Wx',
                          'EypBx': 'Wy',
                          'Bz': 'Bz',
                          'Bx': 'Bx',
                          'By': 'By',
                          'density': 'rho',
                          'x1': 'z',
                          'x2': 'x',
                          'x3': 'y',
                          'p1': 'pz',
                          'p2': 'px',
                          'p3': 'py',
                          'q': 'q',
                          'ene': 'ekin',
                          'tag': 'tag'}

        try:
            return name_relations[hipace_name]
        except KeyError:
            print('Unknown data name {}.'.format(hipace_name))
            return hipace_name

    def _get_files_and_timesteps(self, folder_path, files_in_folder, prefix,
                                 name):
        """
        Get a list of all field files and timesteps.

        Parameters
        ----------

        folder_path : str
            Path to the folder containing the data files.

        files_in_folder : list
            List of all data files in the HiPACE simulation folder (not only
            those of the current field).

        prefix : str
            HiPACE files have a prefix 'field', 'density' or 'raw' depending
            on the data type. Possible values here are 'field' or 'density'.

        Returns
        -------
        A tuple with a an array of file paths and and array of timesteps.
        """
        field_files = [os.path.join(folder_path, file) for file in \
            files_in_folder if (prefix in file) and (name in file)]
        time_steps = np.zeros(len(field_files))
        for i, file in enumerate(field_files):
            time_step = int(file.split('_')[-1].split('.')[0])
            time_steps[i] = time_step
        sort_i = np.argsort(time_steps)
        time_steps = time_steps[sort_i]
        field_files = np.array(field_files)[sort_i]
        return field_files, time_steps