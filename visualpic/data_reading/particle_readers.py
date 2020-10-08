"""
This file is part of VisualPIC.

The module contains the definitions of the different particle data readers.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""

from h5py import File as H5F
import numpy as np
import scipy.constants as ct
from openpmd_viewer.openpmd_timeseries.data_reader.params_reader import (
    read_openPMD_params)
from openpmd_viewer.openpmd_timeseries.data_reader.field_reader import (
    get_grid_parameters)

from visualpic.helper_functions import join_infile_path


class ParticleReader():
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def read_particle_data(self, file_path, species_name,
                           component_list=[]):
        data_dict = {}
        for component in component_list:
            metadata = self._read_component_metadata(file_path, species_name,
                                                     component)
            data = self._read_component_data(file_path, species_name,
                                             component)
            data_dict[component] = (data, metadata)
        return data_dict

    def _read_component_metadata(self, file_path, species, component):
        raise NotImplementedError()

    def _read_component_data(self, file_path, species, component):
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

    def _read_component_data(self, file_path, species, component):
        with H5F(file_path, 'r') as file_handle:
            data = file_handle[self.name_relations[component]]
            if component == 'tag':
                # Apply Cantor pairing function
                print(data)
                a = data[:, 0]
                b = data[:, 1]
                data = 1/2*(a+b)*(a+b+1)+b
            return np.array(data)

    def _read_component_metadata(self, file_path, species, component):
        metadata = {}
        with H5F(file_path, 'r') as file_handle:
            # Read units.
            if component != 'tag':
                osiris_name = self.name_relations[component]
                # In new Osiris versions, the units are in a list in '/'.
                if 'QUANTS' in file_handle.attrs:
                    units_path = '/'
                    quantlist = [self._numpy_bytes_to_string(q)
                                 for q in file_handle.attrs['QUANTS']]
                    idx = quantlist.index(osiris_name)
                else:
                    units_path = osiris_name
                    idx = 0
                metadata['units'] = self._numpy_bytes_to_string(
                    file_handle[units_path].attrs['UNITS'][idx])
            # Read time data.
            metadata['time'] = {}
            metadata['time']['value'] = file_handle.attrs['TIME'][0]
            metadata['time']['units'] = self._numpy_bytes_to_string(
                file_handle.attrs['TIME UNITS'][0])
            # Read grid parameters.
            simdata_path = '/SIMULATION'
            # In older Osiris versions the simulation parameters are in '/'.
            if simdata_path not in file_handle.keys():
                simdata_path = '/'
            sim_data = file_handle[simdata_path]
            metadata['grid'] = {}
            metadata['grid']['resolution'] = sim_data.attrs['NX']
            max_range = sim_data.attrs['XMAX']
            min_range = sim_data.attrs['XMIN']
            metadata['grid']['size'] = max_range - min_range
            grid_range = []
            for x_min, x_max in zip(min_range, max_range):
                grid_range.append([x_min, x_max])
            metadata['grid']['range'] = grid_range
            metadata['grid']['size_units'] = '\\omega_p/c'
        return metadata

    def _numpy_bytes_to_string(self, npbytes):
        return str(npbytes)[2:-1].replace("\\\\", "\\").replace(' ', '')


class HiPACEParticleReader(ParticleReader):
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

    def _read_component_data(self, file_path, species, component):
        with H5F(file_path, 'r') as file_handle:
            if component in self.name_relations:
                hp_name = self.name_relations[component]
            else:
                hp_name = component
            data = file_handle[hp_name]
            if component == 'tag':
                # Apply Cantor pairing function
                print(data)
                a = data[:, 0]
                b = data[:, 1]
                data = 1/2*(a+b)*(a+b+1)+b
            return np.array(data)

    def _read_component_metadata(self, file_path, species, component):
        metadata = {}
        with H5F(file_path, 'r') as file_handle:
            if component in ['x', 'y', 'z']:
                units = 'c/\\omega_p'
            elif component in ['px', 'py', 'pz']:
                units = 'm_ec'
            elif component == 'q':
                units = 'qnorm'
            else:
                units = ''
            metadata['units'] = units
            metadata['time'] = {}
            metadata['time']['value'] = file_handle.attrs['TIME'][0]
            metadata['time']['units'] = '1/\\omega_p'
            metadata['grid'] = {}
            metadata['grid']['resolution'] = file_handle.attrs['NX']
            max_range = file_handle.attrs['XMAX']
            min_range = file_handle.attrs['XMIN']
            metadata['grid']['size'] = max_range - min_range
            grid_range = []
            for x_min, x_max in zip(min_range, max_range):
                grid_range.append([x_min, x_max])
            metadata['grid']['range'] = grid_range
            metadata['grid']['size_units'] = 'c/\\omega_p'
        return metadata


class OpenPMDParticleReader(ParticleReader):
    def __init__(self, *args, **kwargs):
        self.name_relations = {'z': 'position/z',
                               'x': 'position/x',
                               'y': 'position/y',
                               'pz': 'momentum/z',
                               'px': 'momentum/x',
                               'py': 'momentum/y',
                               'q': 'charge',
                               'm': 'mass',
                               'tag': 'id',
                               'w': 'weighting'}
        return super().__init__(*args, **kwargs)

    def _read_component_data(self, file_path, species, component):
        with H5F(file_path, 'r') as file_handle:
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
            elif component_to_read == 'mass':
                data = beam_species[component_to_read].attrs['value']
                w = beam_species['weighting'][:]
                data = data * w
            else:
                data = beam_species[component_to_read][:]
            return data

    def _read_component_metadata(self, file_path, species, component):
        t, params = read_openPMD_params(file_path, extract_parameters=True)
        fields_metadata = params['fields_metadata']
        avail_fields = params['avail_fields']
        component_to_read = self.name_relations[component]
        metadata = {}
        if 'position' in component_to_read:
            metadata['units'] = 'm'
        elif 'momentum' in component_to_read:
            metadata['units'] = 'm_e*c'
        elif component_to_read == 'charge':
            metadata['units'] = 'C'
        elif component_to_read == 'mass':
            metadata['units'] = 'kg'
        else:
            metadata['units'] = ''
        metadata['time'] = {}
        metadata['time']['value'] = t
        metadata['time']['units'] = 's'
        metadata['grid'] = {}
        if len(avail_fields) > 0:
            with H5F(file_path, 'r') as file_handle:
                grid_size_dict, grid_range_dict = get_grid_parameters(
                        file_handle, avail_fields, fields_metadata)
                resolution = []
                grid_size = []
                grid_range = []
                if 'z' in grid_size_dict:
                    resolution.append(grid_size_dict['z'])
                    grid_size.append(grid_range_dict['z'][1] -
                                     grid_range_dict['z'][0])
                    grid_range.append(grid_range_dict['z'])
                if 'r' in grid_size_dict:
                    resolution.append(grid_size_dict['r'])
                    grid_size.append(grid_range_dict['r'][1] -
                                     grid_range_dict['r'][0])
                    grid_range.append(grid_range_dict['r'])
                if 'x' in grid_size_dict:
                    resolution.append(grid_size_dict['x'])
                    grid_size.append(grid_range_dict['x'][1] -
                                     grid_range_dict['x'][0])
                    grid_range.append(grid_range_dict['x'])
                if 'y' in grid_size_dict:
                    resolution.append(grid_size_dict['y'])
                    grid_size.append(grid_range_dict['y'][1] -
                                     grid_range_dict['y'][0])
                    grid_range.append(grid_range_dict['y'])
            metadata['grid']['resolution'] = resolution
            metadata['grid']['size'] = grid_size
            metadata['grid']['range'] = grid_range
            metadata['grid']['size_units'] = 'm'
        else:
            metadata['grid']['resolution'] = None
            metadata['grid']['size'] = None
            metadata['grid']['size_units'] = None
        return metadata
