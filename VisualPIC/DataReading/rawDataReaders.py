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
from h5py import File as H5File
import numpy as np

from VisualPIC.DataReading.dataReader import DataReader
from VisualPIC.DataReading.openPMDTimeSeriesSingleton import (
    OpenPMDTimeSeriesSingleton, openpmd_installed)


class RawDataReaderBase(DataReader):
    """Parent class for all rawDataReaders"""
    __metaclass__  = abc.ABCMeta
    def __init__(self, location, species_name, data_name, internal_name,
                 first_time_step):
        DataReader.__init__(self, location, species_name, data_name,
                            internal_name)
        self.internal_name = data_name
        self.first_time_step = first_time_step
        self.read_basic_data()

    def get_data(self, time_step):
        if time_step != self.current_time_step:
            self.current_time_step = time_step
            self.data = self.read_data(time_step)
        return self.data

    def get_data_units(self):
        if self.data_units == "":
            self.read_units()
        return self.data_units

    def get_time(self, time_step):
        if time_step != self.current_time_step:
            self.current_time_step = time_step
            self.read_time(time_step)
        return self.current_time

    def get_time_units(self):
        if self.time_units == "":
            self.read_units()
        return self.time_units

    @abc.abstractmethod
    def read_basic_data(self):
        raise NotImplementedError


class OsirisRawDataReader(RawDataReaderBase):
    def __init__(self, location, species_name, data_name, internal_name,
                 first_time_step):
        RawDataReaderBase.__init__(self, location, species_name, data_name,
                                   internal_name, first_time_step)

    def read_data(self, time_step):
        file_content = self.open_file(time_step)
        if self.internal_name == "tag":
            tags = np.array(file_content.get(self.internal_name))
            a = tags[:,0]
            b = tags[:,1]
            data = 1/2*(a+b)*(a+b+1)+b # Cantor pairing function
        else:
            data = np.array(file_content.get(self.internal_name))
        self.current_time = file_content.attrs["TIME"][0]
        file_content.close()
        return data

    def read_time(self, time_step):
        file_content = self.open_file(time_step)
        self.current_time = file_content.attrs["TIME"][0]
        file_content.close()

    def read_units(self):
        file_content = self.open_file(self.first_time_step)
        self.data_units = str(list(file_content[self.internal_name].attrs[
            "UNITS"])[0])[2:-1].replace("\\\\","\\")
        self.time_units = str(file_content.attrs[
            "TIME UNITS"][0])[2:-1].replace("\\\\","\\")
        file_content.close()

    def read_simulation_properties(self, file_content):
        self.grid_resolution = np.array(file_content.attrs['NX'])
        self.grid_size = (np.array(file_content.attrs['XMAX'])
                          - np.array(file_content.attrs['XMIN']))
        self.grid_units = 'c/ \omega_p'

    def open_file(self, time_step):
        fileName = "RAW-" + self.species_name + "-" + str(time_step).zfill(6)
        ending = ".h5"
        file_path = self.location + "/" + fileName + ending
        file_content = H5File(file_path, 'r')
        return file_content

    def read_basic_data(self):
        file_content = self.open_file(self.first_time_step)
        self.read_simulation_properties(file_content)
        file_content.close()


class HiPACERawDataReader(RawDataReaderBase):
    def __init__(self, location, species_name, data_name, internal_name,
                 first_time_step):
        RawDataReaderBase.__init__(self, location, species_name, data_name,
                                   internal_name, first_time_step)

    def read_data(self, time_step):
        file_content = self.open_file(time_step)
        if self.internal_name == "tag":
            tags = np.array(file_content.get(self.internal_name))
            a = tags[:,0]
            b = tags[:,1]
            data = 1/2*(a+b)*(a+b+1)+b # Cantor pairing function
        else:
            data = np.array(file_content.get(self.internal_name))
        self.current_time = file_content.attrs["TIME"][0]
        if self.internal_name == "x1":
            data += self.current_time
        file_content.close()
        return data

    def read_time(self, time_step):
        file_content = self.open_file(time_step)
        self.current_time = file_content.attrs["TIME"][0]
        file_content.close()

    def read_units(self):
        # No units information is currently stored by HiPACE
        if self.data_name in ["x1" , "x2", "x3"]:
            self.data_units = 'c/ \omega_p'
        elif self.data_name in ["p1", "p2", "p3"]:
            self.data_units = 'm_e c'
        elif self.data_name == "q":
            self.data_units = 'e'
        else:
            self.data_units = 'unknown'
        self.time_units = '1/ \omega_p'

    def open_file(self, time_step):
        fileName = "raw_" + self.species_name + "_" + str(time_step).zfill(6)
        ending = ".h5"
        file_path = self.location + "/" + fileName + ending
        file_content = H5File(file_path, 'r')
        return file_content

    def read_simulation_properties(self, file_content):
        self.grid_resolution = np.array(file_content.attrs['NX'])
        self.grid_size = (np.array(file_content.attrs['XMAX'])
                          - np.array(file_content.attrs['XMIN']))
        self.grid_units = 'c/ \omega_p'

    def read_basic_data(self):
        file_content = self.open_file(self.first_time_step)
        self.read_simulation_properties(file_content)
        file_content.close()

class OpenPMDRawDataReader(RawDataReaderBase):
    def __init__(self, location, species_name, data_name, internal_name,
                 first_time_step):
        # First check whether openPMD is installed
        if not openpmd_installed:
            raise RunTimeError(
                "You need to install openPMD-viewer, e.g. with:\n"
                "pip install openPMD-viewer")
        # Store an openPMD timeseries object
        # (Its API is used in order to conveniently extract data from the file)
        self.openpmd_ts = OpenPMDTimeSeriesSingleton(location,
                                                     check_all_files=False)
        # Initialize the instance
        RawDataReaderBase.__init__(self, location, species_name, data_name,
                                   internal_name, first_time_step)

    def read_data(self, time_step):
        data, = self.openpmd_ts.get_particle( [self.internal_name],
                    species=self.species_name, iteration=time_step )
        # VisualPIC needs the total charge and mass per particle, therefore,
        #in openPMD this quantities have to be multiplied by the particle
        #weight
        if self.internal_name == 'charge' or self.internal_name == 'mass':
            w, = self.openpmd_ts.get_particle( ['w'],
                    species=self.species_name, iteration=time_step )
            data = data*w
        self.current_time = self.read_time(time_step)
        return data

    def read_time(self, time_step):
        # The line below sets the attribute `_current_i` of openpmd_ts
        self.openpmd_ts._find_output( None, time_step )
        # This sets the corresponding time
        self.current_time = self.openpmd_ts.t[ self.openpmd_ts._current_i ]

    def read_units(self):
        # OpenPMD data always provide conversion to SI units
        # TODO: Get the units from file
        if self.internal_name in ["x", "y", "z"]:
            self.data_units = "μm" 
        elif self.internal_name in ["ux", "uy", "uz"]:
            self.data_units = "m_e c" 
        elif self.internal_name == 'charge':
            self.data_units = "C"
        elif self.internal_name == 'mass':
            self.data_units = "kg"
        else:
            self.data_units = "arb.u." 
        self.time_units = "s"

    def open_file(self, time_step):
        # The line below sets the attribute `_current_i` of openpmd_ts
        self.openpmd_ts._find_output( None, time_step )
        # This finds the full path to the corresponding file
        fileName = self.openpmd_ts.h5_files[ self.openpmd_ts._current_i ]
        file_content = H5File(fileName, 'r')
        return file_content

    def read_simulation_properties(self, file_content):
        # TODO: Add the proper resolution
        self.grid_resolution = None
        self.grid_size = None
        self.grid_units = 'm'

    def read_basic_data(self):
        file_content = self.open_file(self.first_time_step)
        self.read_simulation_properties(file_content)
        file_content.close()
