# -*- coding: utf-8 -*-

#Copyright 2016-2018 Angel Ferran Pousa, DESY
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
from h5py import File as H5File
import numpy as np

from VisualPIC.DataHandling.species import Species
from VisualPIC.DataHandling.folderDataElements import (FolderField, 
                                                       FolderRawDataSet)
from VisualPIC.DataHandling.rawDataTags import RawDataTags
from VisualPIC.DataReading.openPMDTimeSeriesSingleton import (
    OpenPMDTimeSeriesSingleton, openpmd_installed)

class FolderDataReader:
    """Scans the simulation folder and creates all the necessary species,
    fields and rawDataSet objects"""
    def __init__(self, parent_data_container):
        self.data_container = parent_data_container
        self.data_location = ""
        self.load_data_from = {"Osiris": self.load_osiris_data,
                               "HiPACE": self.load_hipace_data,
                               "openPMD": self.load_openpmd_data}

    def set_data_location(self, data_location):
        self.data_location = data_location

    def get_data_location(self):
        return self.data_location

    """
    Data managing. Methods for adding the detected species, fields...
    """
    def add_species(self, species):
        add_species = True
        # the species will not be added if it already exists
        for av_species in self.data_container.available_species:
            if av_species.get_name() == species.get_name():
                add_species =  False
        if add_species:
            self.data_container.available_species.append(species)

    def add_field_to_species(self, species_name, field):
        for species in self.data_container.available_species:
            if species.get_name() == species_name:
                species.add_available_field(field)

    def add_raw_data_to_species(self, species_name, dataset):
        for species in self.data_container.available_species:
            if species.get_name() == species_name:
                species.add_raw_dataset(dataset)

    def add_raw_data_tags_to_species(self, species_name, tags):
        for species in self.data_container.available_species:
            if species.get_name() == species_name:
                species.add_raw_data_tags(tags)

    def add_domain_field(self,field):
        self.data_container.available_domain_fields.append(field)

    def load_data(self, simulation_code):
        """Main data loader. It will automatically call the specific loader
        for a particular simulation code"""
        self.load_data_from[simulation_code]()

    """
    Specific data loaders
    """
    # OSIRIS
    def load_osiris_data(self):
        """Osiris Loader"""
        key_folder_names = ["DENSITY", "FLD", "PHA", "RAW" ]
        main_folders = os.listdir(self.data_location)
        for folder in main_folders:
            subdir = self.data_location + "/" + folder
            if folder == key_folder_names[0]:
                species_names = os.listdir(subdir)
                for species in species_names:
                    if os.path.isdir(os.path.join(subdir, species)):
                        self.add_species(Species(species))
                        species_fields = os.listdir(subdir + "/" + species)
                        for field in species_fields:
                            if os.path.isdir(os.path.join(
                                subdir + "/" + species, field)):
                                field_location = (subdir + "/" + species + "/"
                                                  + field)
                                field_name = field
                                time_steps = (
                                    self.get_time_steps_in_simulation_osiris(
                                        field_location))
                                if time_steps.size != 0:
                                    field = FolderField(
                                        "Osiris", field_name, 
                                        self.give_standard_name_osiris(
                                            field_name), 
                                        field_location, time_steps, species)
                                    self.add_field_to_species(species, field)
            elif folder == key_folder_names[1]:
                domain_fields = os.listdir(subdir)
                for field in domain_fields:
                    if os.path.isdir(os.path.join(subdir, field)):
                        field_location = subdir + "/" + field
                        field_name = field
                        time_steps = self.get_time_steps_in_simulation_osiris(
                            field_location)
                        if time_steps.size != 0:
                            field = FolderField(
                                "Osiris", field_name,
                                self.give_standard_name_osiris(field_name),
                                field_location, time_steps)
                            self.add_domain_field(field)

            elif folder ==  key_folder_names[3]:
                subdir = self.data_location + "/" + folder
                species_names = os.listdir(subdir)
                for species in species_names:
                    if os.path.isdir(os.path.join(subdir, species)):
                        self.add_species(Species(species))
                        dataset_location = subdir + "/" + species
                        time_steps = self.get_time_steps_in_simulation_osiris(
                            dataset_location)
                        if time_steps.size != 0:
                            file_path = (dataset_location + "/" + "RAW-"
                                         + species + "-"
                                         + str(time_steps[0]).zfill(6) + ".h5")
                            file_content = H5File(file_path, 'r')
                            for dataset_name in list(file_content):
                                if dataset_name == "tag":
                                    tags = RawDataTags(
                                        "Osiris", dataset_name,
                                        dataset_location, time_steps, species,
                                        dataset_name)
                                    self.add_raw_data_tags_to_species(species,
                                                                      tags)
                                else:
                                    raw_dataset = FolderRawDataSet(
                                        "Osiris", dataset_name, 
                                        self.give_standard_name_osiris(
                                            dataset_name), dataset_location, 
                                        time_steps, species, dataset_name)
                                    self.add_raw_data_to_species(species,
                                                                 raw_dataset)
                            file_content.close()

    def get_time_steps_in_simulation_osiris(self, location):
        filenames_list = os.listdir(location)
        # filter only .h5 files
        h5_files = list()
        for file in filenames_list:
            if file.endswith(".h5"):
                h5_files.append(file)
        time_steps = np.zeros(len(h5_files))
        i = 0
        for file in h5_files:
            time_step = int(file[-9:-3])
            time_steps[i] = time_step
            i+=1
        time_steps = time_steps.astype(np.int64)
        time_steps.sort()
        return time_steps

    def give_standard_name_osiris(self, osiris_name):
        if "e1" in osiris_name:
            return "Ez"
        elif "e2" in osiris_name:
            return "Ex"
        elif "e3" in osiris_name:
            return "Ey"
        elif "b1" in osiris_name:
            return "Bz"
        elif "b2" in osiris_name:
            return "Bx"
        elif "b3" in osiris_name:
            return "By"
        elif "charge" in osiris_name:
            return "Charge density"
        elif osiris_name == "x1":
            return "z"
        elif osiris_name == "x2":
            return "x"
        elif osiris_name == "x3":
            return "y"
        elif osiris_name == "p1":
            return "Pz"
        elif osiris_name == "p2":
            return "Px"
        elif osiris_name == "p3":
            return "Py"
        elif osiris_name == "q":
            return "Charge"
        elif osiris_name == "ene":
            return "Energy"
        else:
            return osiris_name

    # HiPACE
    def load_hipace_data(self):
        """HiPACE loader"""
        data_folder = self.data_location
        data_types = ['density', 'field', 'raw']

        files_in_folder = os.listdir(data_folder)

        for data_type in data_types:
            # Fields
            if data_type == 'field':
                data_files = list()
                data_names = list()
                for file in files_in_folder:
                    if file.endswith(".h5") and data_type in file:
                        data_files.append(file)
                        data_name = file.replace(data_type + '_', '')[0:-10]
                        if data_name not in data_names:
                            data_names.append(data_name)
                for data_name in data_names:
                    data_time_steps = list()
                    for file in data_files:
                        if data_name in file:
                            time_step = int(file[-9, -3])
                            data_time_steps.append(time_step)
                    data_time_steps = np.array(data_time_steps)
                    field = FolderField(
                        "HiPACE", data_name, 
                        self.give_standard_name_hipace(data_name),
                        data_folder, data_time_steps)
                    self.add_domain_field(field)
            # Density
            if data_type == 'density':
                data_name = 'charge'
                data_files = list()
                species_names = list()
                for file in files_in_folder:
                    if file.endswith(".h5") and data_type in file:
                        data_files.append(file)
                        species_name = file.replace(
                            data_type + '_', '').replace(
                                '_' + data_name + '_', '')[0:-9]
                        if species_name not in species_names:
                            species_names.append(species_name)
                for species_name in species_names:
                    self.add_species(Species(species_name))
                    data_time_steps = list()
                    for file in data_files:
                        if species_name in file:
                            time_step = int(file[-9:-3])
                            data_time_steps.append(time_step)
                    data_time_steps = np.array(data_time_steps)
                    field = FolderField(
                        "HiPACE", data_name,
                        self.give_standard_name_osiris(data_name), data_folder,
                        data_time_steps, species_name)
                    self.add_field_to_species(species_name, field)
            # Raw data
            if data_type == 'raw':
                data_files = list()
                species_names = list()
                for file in files_in_folder:
                    if file.endswith(".h5") and data_type in file:
                        data_files.append(file)
                        species_name = file.replace(data_type + '_', '')[0:-10]
                        if species_name not in species_names:
                            species_names.append(species_name)
                for species_name in species_names:
                    self.add_species(Species(species_name))
                    data_time_steps = list()
                    for file in data_files:
                        if species_name in file:
                            time_step = int(file[-9:-3])
                            data_time_steps.append(time_step)
                    data_time_steps = np.array(data_time_steps)
                    if data_time_steps.size != 0:
                        file_path = (data_folder + '/' + data_type + '_'
                                     + species_name + '_'
                                     + str(data_time_steps[0]).zfill(6)
                                     + '.h5')
                        file_content = H5File(file_path, 'r')
                        for data_set_name in list(file_content):
                            if data_set_name == "tag":
                                tags = RawDataTags(
                                    "HiPACE", data_set_name, data_folder,
                                    data_time_steps, species_name,
                                    data_set_name)
                                self.add_raw_data_tags_to_species(species_name,
                                                                  tags)
                            else:
                                raw_dataset = FolderRawDataSet(
                                    "HiPACE", data_set_name,
                                    self.give_standard_name_hipace(
                                        data_set_name), data_folder,
                                    data_time_steps, species_name,
                                    data_set_name)
                                self.add_raw_data_to_species(species_name,
                                                             raw_dataset)
                        file_content.close()

    def give_standard_name_hipace(self, original_name):
        if "Ez" in original_name:
            return "Ez"
        elif "charge" in original_name:
            return "Charge density"
        elif original_name == "x1":
            return "z"
        elif original_name == "x2":
            return "x"
        elif original_name == "x3":
            return "y"
        elif original_name == "p1":
            return "Pz"
        elif original_name == "p2":
            return "Px"
        elif original_name == "p3":
            return "Py"
        elif original_name == "q":
            return "Charge"
        elif original_name == "ene":
            return "Energy"
        else:
            return original_name

    # openPMD
    def load_openpmd_data(self):
        """OpenPMD Loader"""
        # First check whether openPMD is installed
        if not openpmd_installed:
            raise RunTimeError(
                "You need to install openPMD-viewer, e.g. with:\n"
                "pip install openPMD-viewer")
        # Scan the folder using openPMD-viewer
        ts = OpenPMDTimeSeriesSingleton(
            self.data_location, check_all_files=False, reset=True)

        # TODO: Change has_non_si_units to False once unit reading is
        # implemented

        # Register the available fields
        if ts.avail_fields is not None:
            for field in ts.avail_fields:
                # Vector field
                if ts.fields_metadata[field]['type'] == 'vector':
                    available_coord = ts.fields_metadata[field]['axis_labels']
                    if ts.fields_metadata[field]['geometry'] == 'thetaMode':
                        available_coord += ['x', 'y']
                    # Register each coordinate of the vector
                    for coord in available_coord:
                        field_name = field + '/' + coord
                        standard_name = self.give_standard_name_openpmd(
                            field_name)
                        self.add_domain_field(
                            FolderField( "openPMD", field_name, standard_name,
                                        self.data_location, ts.iterations,
                                        has_non_si_units = True ) )
                # Scalar field
                if ts.fields_metadata[field]['type'] == 'scalar':
                    field_name = field
                    standard_name = self.give_standard_name_openpmd(field)
                    self.add_domain_field(
                        FolderField( "openPMD", field_name, standard_name,
                                    self.data_location, ts.iterations,
                                    has_non_si_units = True ) )

        # Register the available species
        if ts.avail_species is not None:
            for species in ts.avail_species:
                self.add_species(Species(species))
                for species_quantity in ts.avail_record_components[species]:
                    if species_quantity == "id":
                        tags = RawDataTags("openPMD", species_quantity,
                                self.data_location, ts.iterations,
                                species, species_quantity)
                        self.add_raw_data_tags_to_species(species, tags)
                    else:
                        raw_dataset = FolderRawDataSet(
                            "openPMD", species_quantity,
                            self.give_standard_name_openpmd(species_quantity),
                            self.data_location, ts.iterations, species,
                            species_quantity, has_non_si_units = True) 
                        self.add_raw_data_to_species(species, raw_dataset)

    def give_standard_name_openpmd(self, openpmd_name):
        if "E/z" in openpmd_name:
            return "Ez"
        elif "E/y" in openpmd_name:
            return "Ey"
        elif "E/x" in openpmd_name:
            return "Ex"
        elif "E/r" in openpmd_name:
            return "Er"
        elif "B/z" in openpmd_name:
            return "Bz"
        elif "B/y" in openpmd_name:
            return "By"
        elif "B/x" in openpmd_name:
            return "Bx"
        elif "B/r" in openpmd_name:
            return "Br"
        elif "rho" in openpmd_name:
            return "Charge density"
        elif openpmd_name == "uz":
            return "Pz"
        elif openpmd_name == "uy":
            return "Py"
        elif openpmd_name == "ux":
            return "Px"
        elif openpmd_name == "charge":
            return "Charge"
        else:
            return openpmd_name
