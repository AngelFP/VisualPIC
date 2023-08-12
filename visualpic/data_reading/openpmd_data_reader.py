"""
This module contains the `OpenPMDDataReader`, a class derived from the
openPMD-viewer `DataReader` which has been expanded with a method for returning
only the field metadata.

Some of the methods below include code from openPMD-viewer (see at
https://github.com/openPMD/openPMD-viewer).
"""

import h5py
from openpmd_viewer.openpmd_timeseries.data_reader import DataReader
from openpmd_viewer.openpmd_timeseries.data_reader.h5py_reader import (
    field_reader as fr)
from openpmd_viewer.openpmd_timeseries import FieldMetaInformation
from openpmd_viewer import __version__
viewer_version = __version__.split('.')
viewer_version = [int(v) for v in viewer_version]
new_metainformation = (viewer_version[0] > 1) or (viewer_version[1] >= 8)


class OpenPMDDataReader(DataReader):
    """
    Class perfroming the access to openPMD data files.

    This class is derived from the original openPMD `DataReader` to extend its
    functionality and provide a method which returns only the field metadata.
    """

    def __init__(self, backend):
        """ Initialize class. """
        super().__init__(backend)

    def read_field_metadata(self, iteration, field_name, component_name):
        """
        Read the field metadata.

        Parameters:
        -----------
        iteration : int
            The iteration at which the parameters should be extracted.
        field_name : str
            Name of the field (e.g., `'E'`, `'B'`, `'rho'`, etc.).
        component_name : str
            Name of the field component (e.g., `'r'`, `'x'`, `'t'`, etc.)

        Returns:
        --------
        A dictionary with the time, field and axis metadata.
        """
        # Initialize metadata dictionary.
        md = {}

        # Read basic openPMD parameters.
        t, params = self.read_openPMD_params(iteration)

        # Time metadata.
        md['time'] = {}
        md['time']['value'] = t
        md['time']['units'] = 's'

        # Field metadata.
        md['field'] = {}
        field_geometry = params['fields_metadata'][field_name]['geometry']
        axis_labels = params['fields_metadata'][field_name]['axis_labels']
        field_units = determine_field_units(field_name)
        md['field']['geometry'] = field_geometry
        md['field']['axis_labels'] = axis_labels
        md['field']['units'] = field_units

        # Axis metadata.
        md['axis'] = {}
        info = self.get_field_meta_info(
            iteration, field_name, component_name, axis_labels, field_geometry,
            t)
        for axis in axis_labels:
            md['axis'][axis] = {}
            md['axis'][axis]['units'] = 'm'
            md['axis'][axis]['array'] = getattr(info, axis)
            md['axis'][axis]['spacing'] = getattr(info, 'd'+axis)
            md['axis'][axis]['min'] = getattr(info, axis+'min')
            md['axis'][axis]['max'] = getattr(info, axis+'max')

        return md

    def get_field_meta_info(self, iteration, field, comp, axis_labels,
                            geometry, t):
        """ Get the `FieldMetaInformation` of the field. """
        if self.backend == 'h5py':
            filename = self.iteration_to_file[iteration]
            if geometry in ['thetaMode']:
                return read_circ_field_metadata_h5py(
                    filename, iteration, field, comp, t)
            elif geometry in ["1dcartesian", "2dcartesian", "3dcartesian"]:
                return read_cartesian_field_metadata_h5py(
                    filename, iteration, field, comp, axis_labels, t)
        elif self.backend == 'openpmd-api':
            if geometry in ['thetaMode']:
                return read_circ_field_metadata_io(
                    self.series, iteration, field, comp, t)
            elif geometry in ["1dcartesian", "2dcartesian", "3dcartesian"]:
                return read_cartesian_field_metadata_io(
                    self.series, iteration, field, comp, axis_labels, t)


def read_cartesian_field_metadata_h5py(filename, iteration, field_name,
                                       component_name, axis_labels, t):
    """
    Get `FieldMetaInformation` of cartesian field using `h5py` backend.

    Parameters:
    -----------
    filename : str
        The absolute path to the HDF5 file.
    iteration : int
        The iteration at which to obtain the data.
    field_name : string
       Which field to extract.
    component_name : string, optional
       Which component of the field to extract.
    axis_labels: list of strings
       The name of the dimensions of the array (e.g. ['x', 'y', 'z']).
    """
    # Open the HDF5 file
    dfile = h5py.File(filename, 'r')
    # Extract the dataset and and corresponding group
    if component_name is None:
        field_path = field_name
    else:
        field_path = fr.join_infile_path(field_name, component_name)
    group, dset = fr.find_dataset(dfile, iteration, field_path)

    # Extract the metainformation
    shape = list(fr.get_shape(dset))
    axes = {i: axis_labels[i] for i in range(len(axis_labels))}

    if new_metainformation:
        info = FieldMetaInformation(
            axes, shape, group.attrs['gridSpacing'],
            group.attrs['gridGlobalOffset'], group.attrs['gridUnitSI'],
            dset.attrs['position'], t, iteration)
    else:
        info = FieldMetaInformation(
            axes, shape, group.attrs['gridSpacing'],
            group.attrs['gridGlobalOffset'], group.attrs['gridUnitSI'],
            dset.attrs['position'])
    return info


def read_cartesian_field_metadata_io(series, iteration, field_name,
                                     component_name, axis_labels, t):
    """
    Get `FieldMetaInformation` of cartesian field using `io` backend.

    Parameters:
    -----------
    series : openpmd_api.Series
        An open, readable openPMD-api series object.
    iteration : int
        The iteration at which to obtain the data.
    field_name : string
       Which field to extract.
    component_name : string, optional
       Which component of the field to extract.
    axis_labels: list of strings
       The name of the dimensions of the array (e.g. ['x', 'y', 'z']).
    """
    it = series.iterations[iteration]

    # Extract the dataset and and corresponding group
    field = it.meshes[field_name]
    if field.scalar:
        component = next(field.items())[1]
    else:
        component = field[component_name]

    # Extract the metainformation
    shape = component.shape
    axes = {i: axis_labels[i] for i in range(len(axis_labels))}
    if new_metainformation:
        info = FieldMetaInformation(
            axes, shape,
            field.grid_spacing, field.grid_global_offset,
            field.grid_unit_SI, component.position,
            t, iteration)
    else:
        info = FieldMetaInformation(
            axes, shape,
            field.grid_spacing, field.grid_global_offset,
            field.grid_unit_SI, component.position)
    return info


def read_circ_field_metadata_h5py(filename, iteration, field_name,
                                  component_name, t):
    """
    Get `FieldMetaInformation` of thetaMode field using `h5py` backend.

    Parameters:
    -----------
    filename : str
        The absolute path to the HDF5 file.
    iteration : int
        The iteration at which to obtain the data.
    field_name : string
       Which field to extract.
    component_name : string, optional
       Which component of the field to extract.
    """
    # Open the HDF5 file
    dfile = h5py.File(filename, 'r')
    # Extract the dataset and and corresponding group
    if component_name is None:
        field_path = field_name
    else:
        field_path = fr.join_infile_path(field_name, component_name)
    group, dset = fr.find_dataset(dfile, iteration, field_path)

    # Extract the metainformation
    Nm, Nr, Nz = fr.get_shape(dset)
    if new_metainformation:
        info = FieldMetaInformation(
            {0: 'r', 1: 'z'}, (Nr, Nz),
            group.attrs['gridSpacing'], group.attrs['gridGlobalOffset'],
            group.attrs['gridUnitSI'], dset.attrs['position'], t, iteration,
            thetaMode=True)
    else:
        info = FieldMetaInformation(
            {0: 'r', 1: 'z'}, (Nr, Nz),
            group.attrs['gridSpacing'], group.attrs['gridGlobalOffset'],
            group.attrs['gridUnitSI'], dset.attrs['position'], thetaMode=True)

    return info


def read_circ_field_metadata_io(series, iteration, field_name, component_name,
                                t):
    """
    Get `FieldMetaInformation` of thetaMode field using `io` backend.

    Parameters:
    -----------
    series : openpmd_api.Series
        An open, readable openPMD-api series object.
    iteration : int
        The iteration at which to obtain the data.
    field_name : string
       Which field to extract.
    component_name : string, optional
       Which component of the field to extract.
    """
    it = series.iterations[iteration]

    # Extract the dataset and and corresponding group
    field = it.meshes[field_name]
    if field.scalar:
        component = next(field.items())[1]
    else:
        component = field[component_name]

    # Extract the metainformation
    Nm, Nr, Nz = component.shape
    if new_metainformation:
        info = FieldMetaInformation(
            {0: 'r', 1: 'z'}, (Nr, Nz),
            field.grid_spacing, field.grid_global_offset,
            field.grid_unit_SI, component.position, t, iteration,
            thetaMode=True)
        return info
    else:
        info = FieldMetaInformation(
            {0: 'r', 1: 'z'}, (Nr, Nz),
            field.grid_spacing, field.grid_global_offset,
            field.grid_unit_SI, component.position, thetaMode=True)
        return info


def determine_field_units(field_name):
    """ Return the corresponding units of the field. """
    # TODO: Make more robust implementation using unit_dimension attributes.
    if field_name == 'E':
        return 'V/m'
    elif field_name == 'B':
        return 'T'
    elif field_name == 'rho':
        return 'C/m^3'
    elif field_name == 'J':
        return 'A'
    else:
        return ''
