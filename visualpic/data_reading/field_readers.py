"""
This file is part of VisualPIC.

The module contains the definitions of the different field readers.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""

import os

from h5py import File as H5F
import numpy as np


class FieldReader():
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def read_field(
            self, file_path, iteration, field_path, slice_i=0.5, slice_j=0.5,
            slice_dir_i=None, slice_dir_j=None, m='all', theta=0,
            max_resolution_3d=None, only_metadata=False):
        fld_metadata = self._read_field_metadata(
            file_path, iteration, field_path)
        if not only_metadata:
            geom = fld_metadata['field']['geometry']
            if geom == "1d":
                fld = self._read_field_1d(file_path, iteration, field_path,
                                          fld_metadata)
            elif geom == "2dcartesian":
                fld = self._read_field_2d_cart(
                    file_path, iteration, field_path, fld_metadata, slice_i,
                    slice_dir_i)
            elif geom == "3dcartesian":
                fld = self._read_field_3d_cart(
                    file_path, iteration, field_path, fld_metadata, slice_i,
                    slice_j, slice_dir_i, slice_dir_j)
            elif geom == "cylindrical":
                fld = self._read_field_2d_cyl(
                    file_path, iteration, field_path, fld_metadata, theta,
                    slice_i, slice_dir_i, max_resolution_3d)
            elif geom == "thetaMode":
                fld = self._read_field_theta(
                    file_path, iteration, field_path, fld_metadata, m, theta,
                    slice_i, slice_dir_i, max_resolution_3d)
        else:
            fld = np.array([])
        self._readjust_metadata(fld_metadata, slice_dir_i, slice_dir_j, theta,
                                max_resolution_3d)
        return fld, fld_metadata

    def _readjust_metadata(self, field_metadata, slice_dir_i, slice_dir_j,
                           theta, max_resolution_3d):
        geom = field_metadata['field']['geometry']
        if geom in ['cylindrical', 'thetaMode'] and theta is None:
            r_md = field_metadata['axis']['r']
            z_md = field_metadata['axis']['z']
            # Check if resolution should be reduced
            if max_resolution_3d is not None:
                z = z_md['array']
                r = r_md['array']
                nr = len(r) - 1
                nz = len(z) - 1
                max_res_lon, max_res_transv = max_resolution_3d
                if nz > max_res_lon:
                    excess_z = int(np.round(nz/max_res_lon))
                    z_md['array'] = z[::excess_z]
                    z_md['min'] = z_md['array'][0]
                    z_md['max'] = z_md['array'][-1]
                if nr > max_res_transv:
                    excess_r = int(np.round(nr/max_res_transv))
                    r_md['array'] = r[::excess_r]
                    r_md['min'] = z_md['array'][0]
                    r_md['max'] = z_md['array'][-1]
                # if nr > max_res_transv:
                #    r = zoom(r, max_res_transv/nr, order=1)
                #    r_md['array'] = r
                # if nz > max_res_lon:
                #    z = zoom(z, max_res_lon/nz, order=1)
                #    field_metadata['axis']['z']['array'] = z
            # Create x and y axes and remove r
            field_metadata['axis']['x'] = r_md
            field_metadata['axis']['y'] = r_md
            del field_metadata['axis']['r']
            field_metadata['field']['axis_labels'] = ['x', 'y', 'z']
        elif geom == '3dcartesian':
            # Make sure that the axis order is always ['x', 'y', 'z'].
            # The fields might not originally have the axes ordered like this,
            # but the different field readers already take care of reordering
            # the 3d arrays.
            field_metadata['field']['axis_labels'] = ['x', 'y', 'z']
        if slice_dir_i is not None:
            del field_metadata['axis'][slice_dir_i]
            field_metadata['field']['axis_labels'].remove(slice_dir_i)
        if slice_dir_j is not None:
            del field_metadata['axis'][slice_dir_j]
            field_metadata['field']['axis_labels'].remove(slice_dir_j)

    def _read_field_1d(self, file_path, iteration, field_path, field_md):
        raise NotImplementedError

    def _read_field_2d_cart(
            self, file_path, iteration, field_path, field_md, slice_i=0.5,
            slice_dir_i='z'):
        raise NotImplementedError

    def _read_field_3d_cart(
            self, file_path, iteration, field_path, field_md, slice_i=0.5,
            slice_j=0.5, slice_dir_i=None, slice_dir_j=None):
        raise NotImplementedError

    def _read_field_2d_cyl(
            self, file_path, iteration, field_path, field_md, theta=0,
            slice_i=0.5, slice_dir_i=None, max_resolution_3d=None):
        raise NotImplementedError

    def _read_field_theta(
            self, file_path, iteration, field_path, field_md, m='all', theta=0,
            slice_i=0.5, slice_dir_i=None, max_resolution_3d=None):
        raise NotImplementedError

    def _read_field_metadata(self, file_path, iteration, field_path):
        raise NotImplementedError


class OsirisFieldReader(FieldReader):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def _read_field_1d(self, file_path, iteration, field_path, field_md):
        file = H5F(file_path, 'r')
        return file[field_path]

    def _read_field_2d_cart(
            self, file_path, iteration, field_path, field_md, slice_i=0.5,
            slice_dir_i=None):
        file = H5F(file_path, 'r')
        fld = file[field_path]
        if slice_dir_i is not None:
            fld_shape = fld.shape
            axis_order = ['z', 'x']
            slice_list = [slice(None)] * fld.ndim
            axis_idx_i = axis_order.index(slice_dir_i)
            axis_elements_i = fld_shape[axis_idx_i]
            slice_idx_i = int(round(axis_elements_i * slice_i))
            slice_list[axis_idx_i] = slice_idx_i
            fld = fld[tuple(slice_list)]
        return fld

    def _read_field_3d_cart(
            self, file_path, iteration, field_path, field_md, slice_i=0.5,
            slice_j=0.5, slice_dir_i=None, slice_dir_j=None):
        file = H5F(file_path, 'r')
        fld = file[field_path]
        if slice_dir_i is not None:
            fld_shape = fld.shape
            axis_order = ['x', 'y', 'z']
            slice_list = [slice(None)] * fld.ndim
            axis_idx_i = axis_order.index(slice_dir_i)
            axis_elements_i = fld_shape[axis_idx_i]
            slice_idx_i = int(round(axis_elements_i * slice_i))
            slice_list[axis_idx_i] = slice_idx_i
            if slice_dir_j is not None:
                axis_idx_j = axis_order.index(slice_dir_j)
                axis_elements_j = fld_shape[axis_idx_j]
                slice_idx_j = int(round(axis_elements_j * slice_j))
                slice_list[axis_idx_j] = slice_idx_j
            fld = fld[tuple(slice_list)]
        else:
            fld = fld[:]
        return fld

    def _read_field_metadata(self, file_path, iteration, field_path):
        file = H5F(file_path, 'r')
        md = {}
        field_units = self._get_field_units(file, field_path)
        field_shape = self._get_field_shape(file, field_path)
        field_geometry = self._determine_geometry(file)
        md['field'] = {}
        md['field']['units'] = field_units
        md['field']['geometry'] = field_geometry
        # TODO: check correct order of labels
        if field_geometry == "3dcartesian":
            axis_labels = ['x', 'y', 'z']
        elif field_geometry == "2dcartesian":
            axis_labels = ['x', 'z']
        elif field_geometry == "1d":
            axis_labels = ['z']
        else:
            raise NotImplementedError('Geometry {} '.format(field_geometry) +
                                      'not yet supported.')
        md['field']['axis_labels'] = axis_labels
        md['axis'] = self._get_axis_data(file, field_path, field_geometry,
                                         field_shape)
        md['time'] = self._get_time_data(file)
        file.close()
        return md

    def _get_field_units(self, file, field_path):
        """ Returns the field units"""
        attr_path = '/'
        # In older Osiris versions the units are in field_path.
        if "UNITS" in file[field_path].attrs:
            attr_path = field_path
        return self._numpy_bytes_to_string(file[attr_path].attrs["UNITS"][0])

    def _get_field_shape(self, file, field_path):
        """ Returns shape of field array"""
        return file[field_path].shape

    def _determine_geometry(self, file):
        """ Determines the field geometry """
        if '/AXIS/AXIS3' in file:
            return "3dcartesian"
        elif '/AXIS/AXIS2' in file:
            return "2dcartesian"
        else:
            return "1d"

    def _get_axis_data(self, file, field_path, field_geometry, field_shape):
        """ Returns dictionary with the array and units of each field axis """
        simdata_path = '/SIMULATION'
        # In older Osiris versions the simulation parameters are in '/'.
        if simdata_path not in file.keys():
            simdata_path = '/'
        sim_data = file[simdata_path]
        axis_data = {}
        axis_data['z'] = {}
        axis_data["z"]["units"] = self._numpy_bytes_to_string(
            file['/AXIS/AXIS1'].attrs["UNITS"][0])
        axis_data["z"]["array"] = np.linspace(sim_data.attrs['XMIN'][0],
                                              sim_data.attrs['XMAX'][0],
                                              field_shape[-1])
        if field_geometry in ["2dcartesian", "3dcartesian"]:
            axis_data['x'] = {}
            axis_data["x"]["units"] = self._numpy_bytes_to_string(
                file['/AXIS/AXIS2'].attrs["UNITS"][0])
            axis_data["x"]["array"] = np.linspace(sim_data.attrs['XMIN'][1],
                                                  sim_data.attrs['XMAX'][1],
                                                  field_shape[0])
        if field_geometry == "3dcartesian":
            axis_data['y'] = {}
            axis_data["y"]["units"] = self._numpy_bytes_to_string(
                file['/AXIS/AXIS3'].attrs["UNITS"][0])
            axis_data["y"]["array"] = np.linspace(sim_data.attrs['XMIN'][2],
                                                  sim_data.attrs['XMAX'][2],
                                                  field_shape[1])
        return axis_data

    def _get_time_data(self, file):
        """ Returns dictionary with value and units of the simulation time """
        time_data = {}
        time_data["value"] = file.attrs["TIME"][0]
        time_data["units"] = self._numpy_bytes_to_string(
            file.attrs["TIME UNITS"][0])
        return time_data

    def _numpy_bytes_to_string(self, npbytes):
        return str(npbytes)[2:-1].replace("\\\\", "\\").replace(' ', '')


class HiPACEFieldReader(FieldReader):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def _read_field_3d_cart(
            self, file_path, iteration, field_path, field_md, slice_i=0.5,
            slice_j=0.5, slice_dir_i=None, slice_dir_j=None):
        file = H5F(file_path, 'r')
        fld = file[field_path]
        fld = np.moveaxis(fld, 0, 2)
        if slice_dir_i is not None:
            fld_shape = fld.shape
            axis_order = ['x', 'y', 'z']
            slice_list = [slice(None)] * fld.ndim
            axis_idx_i = axis_order.index(slice_dir_i)
            axis_elements_i = fld_shape[axis_idx_i]
            slice_idx_i = int(round(axis_elements_i * slice_i))
            slice_list[axis_idx_i] = slice_idx_i
            if slice_dir_j is not None:
                axis_idx_j = axis_order.index(slice_dir_j)
                axis_elements_j = fld_shape[axis_idx_j]
                slice_idx_j = int(round(axis_elements_j * slice_j))
                slice_list[axis_idx_j] = slice_idx_j
            fld = fld[tuple(slice_list)]
        return fld

    def _read_field_metadata(self, file_path, iteration, field_path):
        file = H5F(file_path, 'r')
        md = {}
        field_units = self._get_field_units(file_path)
        field_shape = self._get_field_shape(file, field_path)
        md['field'] = {}
        md['field']['units'] = field_units
        md['field']['geometry'] = '3dcartesian'
        # TODO: check correct order of labels
        md['field']['axis_labels'] = ['x', 'y', 'z']
        md['axis'] = self._get_axis_data(file, field_shape)
        md['time'] = self._get_time_data(file)
        file.close()
        return md

    def _get_field_units(self, file_path):
        """ Returns the field units"""
        # HiPACE does not store unit information in data files
        file = os.path.split(file_path)[-1]
        if 'field' in file:
            return 'E_0'
        elif 'density' in file:
            return 'n_0'
        else:
            return ''

    def _get_field_shape(self, file, field_path):
        """ Returns shape of field array"""
        return file[field_path].shape

    def _get_axis_data(self, file, field_shape):
        """ Returns dictionary with the array and units of each field axis """
        axis_data = {}
        axis_data['z'] = {}
        axis_data["z"]["units"] = 'c/\\omega_p'
        axis_data["z"]["array"] = np.linspace(file.attrs['XMIN'][0],
                                              file.attrs['XMAX'][0],
                                              field_shape[0])
        axis_data['x'] = {}
        axis_data["x"]["units"] = 'c/\\omega_p'
        axis_data["x"]["array"] = np.linspace(file.attrs['XMIN'][1],
                                              file.attrs['XMAX'][1],
                                              field_shape[1])
        axis_data['y'] = {}
        axis_data["y"]["units"] = 'c/\\omega_p'
        axis_data["y"]["array"] = np.linspace(file.attrs['XMIN'][2],
                                              file.attrs['XMAX'][2],
                                              field_shape[2])
        return axis_data

    def _get_time_data(self, file):
        """ Returns dictionary with value and units of the simulation time """
        time_data = {}
        time_data["value"] = file.attrs["TIME"][0]
        time_data["units"] = '1/\\omega_p'
        return time_data


class OpenPMDFieldReader(FieldReader):
    def __init__(self, opmd_reader,  *args, **kwargs):
        self._opmd_reader = opmd_reader
        return super().__init__(*args, **kwargs)

    def _read_field_1d(self, file_path, iteration, field_path, field_md):
        field, *comp = field_path.split('/')
        if len(comp) > 0:
            comp = comp[0]
        else:
            comp = None
        axis_labels = field_md['field']['axis_labels']
        fld, _ = self._opmd_reader.read_field_cartesian(
            iteration, field, comp, axis_labels, None, None)
        return fld

    def _read_field_2d_cart(
            self, file_path, iteration, field_path, field_md, slice_i=0.5,
            slice_dir_i=None):
        field, *comp = field_path.split('/')
        if len(comp) > 0:
            comp = comp[0]
        else:
            comp = None
        axis_labels = field_md['field']['axis_labels']
        fld, _ = self._opmd_reader.read_field_cartesian(
            iteration, field, comp, axis_labels, None, None)

        # Make sure the array indices are ordered as ['x' (or 'y'), 'z']
        axes_sort = np.argsort(np.array(axis_labels))
        fld = np.moveaxis(fld, axes_sort, [0, 1])

        if slice_dir_i is not None:
            fld_shape = fld.shape
            axis_order = axis_labels
            slice_list = [slice(None)] * fld.ndim
            axis_idx_i = axis_order.index(slice_dir_i)
            axis_elements_i = fld_shape[axis_idx_i]
            slice_idx_i = int(round(axis_elements_i * slice_i))
            slice_list[axis_idx_i] = slice_idx_i
            fld = fld[tuple(slice_list)]
        return fld

    def _read_field_3d_cart(
            self, file_path, iteration, field_path, field_md, slice_i=0.5,
            slice_j=0.5, slice_dir_i=None, slice_dir_j=None):
        field, *comp = field_path.split('/')
        if len(comp) > 0:
            comp = comp[0]
        else:
            comp = None
        if slice_dir_i is not None:
            slicing = -1. + 2*slice_i
        else:
            slicing = None
        axis_labels = field_md['field']['axis_labels']
        fld, _ = self._opmd_reader.read_field_cartesian(
            iteration, field, comp, axis_labels, slicing, slice_dir_i)

        # Make sure the array indices are ordered as ['x', 'y', 'z']
        axes_sort = np.argsort(np.array(axis_labels))
        fld = np.moveaxis(fld, axes_sort, [0, 1, 2])

        if slice_dir_i is not None and slice_dir_j is not None:
            fld_shape = fld.shape
            axis_order = axis_labels
            axis_order.remove(slice_dir_i)
            slice_list = [slice(None)] * fld.ndim
            axis_idx_j = axis_order.index(slice_dir_j)
            axis_elements_j = fld_shape[axis_idx_j]
            slice_idx_j = int(round(axis_elements_j * slice_j))
            slice_list[axis_idx_j] = slice_idx_j
            fld = fld[tuple(slice_list)]
        return fld

    def _read_field_2d_cyl(
            self, file_path, iteration, field_path, field_md, theta, slice_i,
            slice_dir_i, max_resolution_3d):
        field, *comp = field_path.split('/')
        if len(comp) > 0:
            comp = comp[0]
        else:
            comp = None
        fld, _ = self._opmd_reader.read_field_circ(
            iteration, field, comp, None, None, theta=theta,
            max_resolution_3d=max_resolution_3d)
        return fld

    def _read_field_theta(
            self, file_path, iteration, field_path, field_md, m='all', theta=0,
            slice_i=0.5, slice_dir_i=None, max_resolution_3d=None):
        field, *comp = field_path.split('/')
        if len(comp) > 0:
            comp = comp[0]
        else:
            comp = None
        if comp in ['x', 'y']:
            fld_r, info = self._opmd_reader.read_field_circ(
                iteration, field, '/r', None, None, m, theta,
                max_resolution_3d)
            fld_t, *_ = self._opmd_reader.read_field_circ(
                iteration, field, '/t', None, None, m, theta,
                max_resolution_3d)
            if theta is None:
                # This reconstruction leads to problems on axis
                nx, ny, nz = len(info.x), len(info.y), len(info.z)
                X, Y = np.meshgrid(info.x, info.y)
                theta_2d = np.arctan2(X, Y)
                theta_3d = np.zeros([nx, ny, nz])
                for i in np.arange(nz):
                    theta_3d[:, :, i] = theta_2d
                if comp == 'x':
                    fld = np.cos(theta_3d) * fld_r - np.sin(theta_3d) * fld_t
                elif comp == 'y':
                    fld = np.sin(theta_3d) * fld_r + np.cos(theta_3d) * fld_t
            else:
                if comp == 'x':
                    fld = np.cos(theta) * fld_r - np.sin(theta) * fld_t
                elif comp == 'y':
                    fld = np.sin(theta) * fld_r + np.cos(theta) * fld_t
                # Revert the sign below the axis
                fld[: int(fld.shape[0] / 2)] *= -1
        else:
            fld, _ = self._opmd_reader.read_field_circ(
                iteration, field, comp, None, None, m, theta,
                max_resolution_3d)
        if slice_dir_i is not None:
            fld_shape = fld.shape
            if theta is None:
                axis_order = ['x', 'y', 'z']
            else:
                axis_order = ['r', 'z']
            slice_list = [slice(None)] * fld.ndim
            axis_idx_i = axis_order.index(slice_dir_i)
            axis_elements_i = fld_shape[axis_idx_i]
            slice_idx_i = int(round(axis_elements_i * slice_i))
            slice_list[axis_idx_i] = slice_idx_i
            fld = fld[tuple(slice_list)]
        return fld

    def _read_field_metadata(self, file_path, iteration, field_path):
        # Get name of field and component.
        field, *comp = field_path.split('/')
        if len(comp) > 0:
            comp = comp[0]
        else:
            comp = None
        # Read metadata.
        return self._opmd_reader.read_field_metadata(iteration, field, comp)
