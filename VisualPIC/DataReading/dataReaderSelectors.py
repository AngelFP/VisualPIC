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

from VisualPIC.DataReading.rawDataReaders import *
from VisualPIC.DataReading.fieldReaders import *


class RawDataReaderSelector:
    """Class in charge of returning the corresponding raw data reader"""
    data_readers = {"Osiris": OsirisRawDataReader,
                    "HiPACE": HiPACERawDataReader,
                    "openPMD": OpenPMDRawDataReader}
    @classmethod
    def get_reader(cls, simulation_code, location, species_name, data_name,
                  internal_name, first_time_step):
        return cls.data_readers[simulation_code](
            location, species_name, data_name, internal_name, first_time_step)


class FieldReaderSelector:
    """Class in charge of returning the corresponding field data reader"""
    data_readers = {"Osiris": OsirisFieldReader,
                    "HiPACE": HiPACEFieldReader,
                    "openPMD": OpenPMDFieldReader}
    @classmethod
    def get_reader(cls, simulation_code, location, species_name, data_name,
                  first_time_step):
        return cls.data_readers[simulation_code](
            location, species_name, data_name, first_time_step)
