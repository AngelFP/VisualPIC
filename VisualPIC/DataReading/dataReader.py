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


import abc


class DataReader(object):
    """Parent class for all data readers (FieldReaders and RawDataReaders)"""
    __metaclass__  = abc.ABCMeta
    def __init__(self, location, species_name, data_name, internal_name = ""):
        self.location = location
        self.species_name = species_name
        self.data_name = data_name
        self.internal_name = internal_name
        self.current_time_step = None # time step number
        self.current_time = None # simulation time in the current time step
        self.time_units = ""
        self.data_units = ""
        self.data = None

    @abc.abstractmethod
    def read_units(self):
        raise NotImplementedError


