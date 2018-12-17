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

from h5py import File as H5F
import numpy as np
import scipy.constants as ct

from VisualPIC.helper_functions import join_infile_path


class ParticleReader():
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def read_particle_data(self, file_path, species_name,
                           component_list=[]):
        file = self._get_file_handle(file_path)
        data_dict = {}
        for component in component_list:
            metadata = self._read_component_metadata(file, species_name,
                                                        component)
            data = self._read_component_data(file, species_name, component)
            data_dict[component] = (data, metadata)
        #self._release_file_handle(file)
        return data_dict

    def _get_file_handle(self, file_path):
        raise NotImplementedError()

    def _release_file_handle(self, file_handle):
        raise NotImplementedError()

    def _read_component_metadata(self, file_handle, species, component):
        raise NotImplementedError()

    def _read_component_data(self, file_handle, species, component):
        raise NotImplementedError()


class OsirisParticleReader(ParticleReader):
    def __init__(self, *args, **kwargs):
        self.name_relations = {'z': 'x1',
                               'x': 'x2',
                               'y': 'x3',
                               'pz': 'p1',
                               'px': 'p2',
                               'py': 'p3',
                               'q': 'q',
                               'ekin': 'ene',
                               'tag': 'tag'}
        return super().__init__(*args, **kwargs)

    def _get_file_handle(self, file_path):
        return H5F(file_path, 'r')

    def _release_file_handle(self, file_handle):
        file_handle.close()

    def _read_component_data(self, file_handle, species, component):
        data = file_handle[self.name_relations[component]]
        if component == 'tag':
            # Apply Cantor pairing function
            print(data)
            a = data[:,0]
            b = data[:,1]
            data = 1/2*(a+b)*(a+b+1)+b 
        return data

    def _read_component_metadata(self, file_handle, species, component):
        metadata = {}
        if component != 'tag': 
            metadata['units'] = self._numpy_bytes_to_string(
                file_handle[self.name_relations[component]].attrs['UNITS'][0])
        metadata['time'] = {}
        metadata['time']['value'] = file_handle.attrs['TIME'][0]
        metadata['time']['units'] = self._numpy_bytes_to_string(
            file_handle.attrs['TIME UNITS'][0])
        metadata['grid'] = {}
        metadata['grid']['resolution'] = file_handle.attrs['NX']
        metadata['grid']['size'] = (file_handle.attrs['XMAX']
                                    - file_handle.attrs['XMIN'])
        metadata['grid']['size_units'] = '\\omega_p/c'
        return metadata

    def _numpy_bytes_to_string(self, npbytes):
        return str(npbytes)[2:-1].replace("\\\\","\\")


class OpenPMDParticleReader(ParticleReader):
    def __init__(self, *args, **kwargs):
        self.name_relations = {'z': 'position/z',
                               'x': 'position/x',
                               'y': 'position/y',
                               'pz': 'momentum/z',
                               'px': 'momentum/x',
                               'py': 'momentum/y',
                               'q': 'charge'}
        return super().__init__(*args, **kwargs)

    def _get_file_handle(self, file_path):
        return H5F(file_path, 'r')

    def _release_file_handle(self, file_handle):
        file_handle.close()

    def _read_component_data(self, file_handle, species, component):
        # get base path in file
        iteration = list(file_handle['/data'].keys())[0]
        base_path = '/data/{}'.format(iteration)
        # get path under which particle data is stored
        particles_path = file_handle.attrs['particlesPath'].decode()
        # get species
        beam_species = file_handle[
            join_infile_path(base_path, particles_path, species)]
        component_to_read = self.name_relations[component]
        if 'position' in component_to_read:
            data = beam_species[component_to_read]
            coord = component_to_read[-1]
            data += beam_species['positionOffset/'+coord].attrs['value']
        elif 'momentum' in component_to_read:
            data = beam_species[component_to_read]
            m = beam_species['mass'].attrs['value']
            data = data / (m*ct.c)
        elif component_to_read == 'charge':
            data = beam_species[component_to_read].attrs['value']
            w = beam_species['weighting'][:]
            data = data * w
        return data

    def _read_component_metadata(self, file_handle, species, component):
        # get base path in file
        iteration = list(file_handle['/data'].keys())[0]
        base_path = '/data/{}'.format(iteration)
        component_to_read = self.name_relations[component]
        metadata = {}
        if 'position' in component_to_read:
            metadata['units'] = 'm'
        elif 'momentum' in component_to_read:
            metadata['units'] = 'm_e*c'
        elif component_to_read == 'charge':
            metadata['units'] = 'C'
        metadata['time'] = {}
        metadata['time']['value'] = file_handle[base_path].attrs['time']
        metadata['time']['units'] = 's'
        metadata['grid'] = {}
        metadata['grid']['resolution'] = None
        metadata['grid']['size'] = None
        metadata['grid']['size_units'] = None
        return metadata
