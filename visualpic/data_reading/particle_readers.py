"""
This file is part of VisualPIC.

The module contains the definitions of the different particle data readers.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""

from h5py import File as H5F
import numpy as np


class ParticleReader():
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def read_particle_data(
            self, file_path, iteration, species_name, component_list=[]):
        data_dict = {}
        for component in component_list:
            metadata = self._read_component_metadata(
                file_path, iteration, species_name, component)
            data = self._read_component_data(
                file_path, iteration, species_name, component)
            data_dict[component] = (data, metadata)
        return data_dict

    def _read_component_metadata(
            self, file_path, iteration, species, component):
        raise NotImplementedError()

    def _read_component_data(self, file_path, iteration, species, component):
        raise NotImplementedError()


class OpenPMDParticleReader(ParticleReader):
    def __init__(self, opmd_reader, *args, **kwargs):
        self._opmd_reader = opmd_reader
        self.name_relations = {'z': 'z',
                               'x': 'x',
                               'y': 'y',
                               'pz': 'uz',
                               'px': 'ux',
                               'py': 'uy',
                               'q': 'charge',
                               'm': 'mass',
                               'tag': 'id',
                               'w': 'w'}
        return super().__init__(*args, **kwargs)

    def _read_component_data(self, file_path, iteration, species, component):
        record_comp = self.name_relations[component]
        t, params = self._opmd_reader.read_openPMD_params(iteration)
        extensions = params['extensions']
        data = self._opmd_reader.read_species_data(
            iteration, species, record_comp, extensions)
        if record_comp in ['charge', 'mass']:
            w = self._opmd_reader.read_species_data(
                iteration, species, 'w', extensions)
            data = data * w
        return data

    def _read_component_metadata(
            self, file_path, iteration, species, component):
        t, params = self._opmd_reader.read_openPMD_params(iteration)
        component_to_read = self.name_relations[component]
        metadata = {}
        if component_to_read in ['x', 'y', 'z']:
            metadata['units'] = 'm'
        elif component_to_read in ['ux', 'uy', 'uz']:
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
        avail_fields = params['avail_fields']
        if avail_fields is not None and len(avail_fields) > 0:
            fields_metadata = params['fields_metadata']
            grid_params = self._opmd_reader.get_grid_parameters(
                iteration, avail_fields, fields_metadata)
            grid_size_dict, grid_range_dict = grid_params
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
