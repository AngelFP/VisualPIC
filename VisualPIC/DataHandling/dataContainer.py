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


from VisualPIC.DataReading.folderDataReader import FolderDataReader
from VisualPIC.DataHandling.customDataElements import CustomFieldCreator, CustomRawDataSetCreator
from VisualPIC.DataHandling.dataElement import DataElement
import VisualPIC.DataHandling.unitConverters as uc


class DataContainer:
    """Contains all the fields and rawDataSets available on the simulation
    folder, as well as the custom ones"""
    def __init__(self):
        self.folder_data_reader = FolderDataReader(self)
        self.simulation_parameters = dict()
        # unit_converter will be set in "set_simulation_parameters" where the
        # user manually selects the code
        self.unit_converter = None
        # species (may contain fields and raw data)
        self.available_species = list()
        self.selected_species = list()
        self.selected_species_field_name = None
        self.selected_species_fields = list()
        # domain fields
        self.available_domain_fields = list()
        self.selected_domain_field = None
    
    def load_data(self):
        self.folder_data_reader.load_data(
            self.simulation_parameters["SimulationCode"])
        self.available_domain_fields = (
            self.available_domain_fields
            + CustomFieldCreator.get_custom_fields(self))
        for species in self.available_species:
            species_name = species.get_name()
            species_custom_flds = CustomRawDataSetCreator.get_custom_datasets(
                self, species_name)
            for data_set in species_custom_flds:
                species.add_raw_dataset(data_set)

    def set_data_folder_location(self, folder_location):
        self.folder_data_reader.set_data_location(str(folder_location))

    def get_data_folder_location(self):
        return self.folder_data_reader.get_data_location()

    def get_simulation_code_name(self):
        return self.simulation_parameters["SimulationCode"]

    def set_simulation_parameters(self, parameters):
        # If there is no unit_converter or the simulation code has changed,
        # create a new unit_converter.
        if ((self.unit_converter is None)
            or (self.simulation_parameters["SimulationCode"]
                != parameters["SimulationCode"])):
            self.unit_converter = uc.UnitConverterSelector.get_unit_converter(
                parameters)
            DataElement.set_unit_converter(self.unit_converter)
        # otherwise, update the current one.
        else:
            self.unit_converter.set_simulation_parameters(parameters)
        self.simulation_parameters = parameters

    def get_simulation_parameters(self):
        return self.simulation_parameters

    def get_names_of_available_parameters(self):
        param_names = list()
        for name in self.simulation_parameters:
            param_names.append(name)
        return param_names

    def get_simulation_parameter(self, param_name):
        return self.simulation_parameters[param_name]
                
    def add_selected_species(self, species_name):
        for species in self.available_species:
            if species.get_name() == species_name:
                self.selected_species.append(species)

    def get_simulation_geometry(self):
        for field in self.available_domain_fields:
            return field.get_field_geometry()
        for species in self.available_species:
            for field in species.get_available_fields():
                return field.get_field_geometry()

    def get_simulation_cell_size(self):
        for field in self.available_domain_fields:
            return field.get_simulation_cell_size()
        for species in self.available_species:
            for field in species.get_available_fields():
                return field.get_simulation_cell_size()
            for dataset in species.get_available_raw_data_sets():
                return dataset.get_simulation_cell_size()
        return "2D"
         
    def remove_selected_species(self, species_name):
        for species in self.selected_species:
            if species.get_name() == species_name:
                self.selected_species.remove(species)

    def set_selected_species(self, species_list):
        if species_list is list:
            self.selected_species = species_list;
    
    def set_selected_species_fields(self):
        self.selected_species_fields[:] = []
        for species in self.selected_species:
            self.selected_species_fields.append(
                species.get_field(self.selected_species_field_name))
            
    def set_selected_species_field(self, field_name):
        self.selected_species_field_name = field_name
    
    def get_available_species(self):
        return self.available_species

    def get_species(self, species_name):
        for species in self.available_species:
            if species.get_name() == species_name:
                return species
        
    def get_species_with_raw_data(self):
        species_list = list()
        for species in self.available_species:
            if species.has_raw_data():
                species_list.append(species)
        return species_list

    def get_species_with_tracking_data(self):
        species_list = list()
        for species in self.available_species:
            if species.has_tags():
                species_list.append(species)
        return species_list

    def get_name_of_species_with_tracking_data(self):
        species_list = list()
        for species in self.available_species:
            if species.has_tags():
                species_list.append(species.get_name())
        return species_list
        
    def get_available_species_names(self):
        names_list = list()
        for species in self.available_species:
            names_list.append(species.get_name())
        return names_list

    def get_selected_species(self):
        return self.selected_species  
        
    def get_available_domain_fields(self):
        return self.available_domain_fields
        
    def get_available_domain_fields_names(self):
        names_list = list()
        for field in self.available_domain_fields:
            names_list.append(field.get_name())
        return names_list
        
    def get_available_fields_in_species(self, species_name):
        for species in self.available_species:
            if species.get_name() == species_name:
                return species.get_available_field_names_list()
                
    def get_domain_field(self, field_name):
        for field in self.available_domain_fields:
            if field.get_name() == field_name:
                return field
                
    def get_species_field(self, species_name, field_name):
        for species in self.available_species:
            if species.get_name() == species_name:
                return species.get_field(field_name)
    
    def get_species_raw_dataset(self, species_name, dataset_name):
        for species in self.available_species:
            if species.get_name() == species_name:
                return species.get_raw_dataset(dataset_name)

    def get_species_tracking_tags(self, species_name, time_step):
        for species in self.available_species:
            if species.get_name() == species_name:
                return species.get_tags(time_step)
                
    def get_folder_path(self):
        return self.folder_data_reader.get_data_location()
        
    def set_selected_domain_field(self, field_name):
        for field in self.available_domain_fields:
            if field.get_name() == field_name:
                self.selected_domain_field = field
    
    def get_selected_domain_field(self):
        # return a list to keep consistency with get_selected_species_fields()
        fldList = list()
        fldList.append(self.selected_domain_field)
        return fldList;
            
    def get_selected_domain_field_name(self):
        return self.selected_domain_field.get_name();

    def get_selected_species_fields(self):
        return self.selected_species_fields
        
    def get_commonly_available_fields(self):
        common_fields = list()
        fields_to_remove = list()
        i = 0
        for species in self.selected_species:
            if i == 0:
                common_fields = species.get_available_field_names_list()
            else:
                speciesFields =  species.get_available_field_names_list()
                for field in common_fields:
                    if field not in speciesFields:
                        fields_to_remove.append(field)
            i+=1
        for field in fields_to_remove:
            common_fields.remove(field)
        return common_fields

    def clear_data(self):
        self.available_species = list()
        self.available_domain_fields = list()
        self.selected_species = list()
        self.selected_domain_field = None
        self.selected_species_field_name = None