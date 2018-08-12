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


class Species:
    def __init__(self, name):
        self.name = name
        self.available_fields = list()
        self.custom_fields = list()
        self.raw_datasets = list()
        self.tags = None # it will be a RawDataTags instance
        self.has_fields = False
        self.species_with_raw_data = False
        self.species_with_tags = False
        
    def add_available_field(self,field):
        self.has_fields = True
        if field not in self.available_fields:
            self.available_fields.append(field)
        
    def add_custom_field(self, field):
        self.custom_fields.append(field)
            
    def add_raw_dataset(self, dataset):
        self.species_with_raw_data = True
        self.raw_datasets.append(dataset)

    def add_raw_data_tags(self, tags):
        self.species_with_tags = True
        self.tags = tags

    def has_fields(self):
        return self.has_fields
        
    def has_raw_data(self):
        return self.species_with_raw_data

    def has_tags(self):
        return self.species_with_tags
            
    def get_field_plot_data(self, field_name, time_step):
        for field in self.available_fields:
            if field.get_name() == field_name:
                return field.get_plot_data(time_step)
        
        for field in self.custom_fields:
            if field.get_name() == field_name:
                return field.get_plot_data(time_step)
    
    def get_raw_dataset_plot_data(self, dataset_name, time_step):
        for dataset in self.raw_datasets:
            if dataset.get_name() == dataset_name:
                return dataset.get_plot_data(time_step)

    def get_tags(self, time_step):
        return self.tags.GetTags(time_step)

    def get_raw_data_time_steps(self):
        """ Assumes all RawDataSets have the same number of time steps)"""
        return self.raw_datasets[0].get_time_steps()
            
    def get_available_field_names_list(self):
        field_names = list()
        for field in self.available_fields:
            field_names.append(field.get_name())
        return field_names

    def get_available_fields(self):
        return self.available_fields
        
    def get_custom_field_names_list(self):
        field_names = list()
        for field in self.custom_fields:
            field_names.append(field.get_name())
        return field_names
        
    def get_raw_dataset_names_list(self):
        dataset_names = list()
        for dataset in self.raw_datasets:
            dataset_names.append(dataset.get_name())
        return dataset_names

    def get_all_raw_datasets(self):
        return self.raw_datasets
    
    def get_name(self):
        return self.name
    
    def get_field(self, field_name):
        for field in self.available_fields:
            if field.get_name() == field_name:
                return field
                
    def get_raw_dataset(self, dataset_name):
        for dataset in self.raw_datasets:
            if dataset.get_name() == dataset_name:
                return dataset
        
    def load_custom_fields(self):
        #to do
        #looks which fields are available and loads the custom fields that
        #can be computed from those
        raise Exception("notImplemented")
