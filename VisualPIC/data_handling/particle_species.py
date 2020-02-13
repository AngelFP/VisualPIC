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


class ParticleSpecies():
    def __init__(self, species_name, components_in_file, species_timesteps,
                 species_files, data_reader, unit_converter):
        self.species_name = species_name
        self.components_in_file = components_in_file
        self.custom_components = []
        self.timesteps = species_timesteps
        self.species_files = species_files
        self.data_reader = data_reader
        self.unit_converter = unit_converter

    def get_data(self, time_step, components_list, data_units=None,
                 time_units=None):
        comp_to_read = []
        comp_to_compute = []
        for component in components_list:
            if component in self.components_in_file:
                comp_to_read.append(component)
            elif component in self.custom_components:
                comp_to_compute.append(component)
            else:
                print('Unrecognized component {}'.format(component))
        file_path = self._get_file_path(time_step)
        folder_data = self.data_reader.read_particle_data(
            file_path, self.species_name, comp_to_read)
        # TODO: implement custom data
        custom_data = {}
        data = {**folder_data, **custom_data}
        if data_units is not None:
            if len(data_units) == len(components_list):
                units_dict = dict(zip(components_list, data_units))
                #Perform data unit conversion
                self.unit_converter.convert_particle_data_units(data, target_data_units=units_dict,
                                    target_time_units=time_units)
            else:
                print('Lenght of units and components lists does not match.')
        return data

    def _get_file_path(self, time_step):
        ts_i = self.timesteps.tolist().index(time_step)
        return self.species_files[ts_i]

