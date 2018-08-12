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

from VisualPIC.DataReading.dataReaderSelectors import RawDataReaderSelector

class RawDataTags(object):
    def __init__(self, simulation_code, name, location, time_steps,
                 species_name="", internal_name=""):
        self.data_name = name
        self.data_location = location
        self.species_name = species_name
        self.time_steps = time_steps
        self.data_reader = RawDataReaderSelector.get_reader(
            simulation_code, location, species_name, name, internal_name,
            time_steps[0])

    def get_time_steps(self):
        return self.time_steps

    def get_tags(self, time_step):
        return self.data_reader.get_data(time_step)
