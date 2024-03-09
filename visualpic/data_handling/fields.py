"""
This file is part of VisualPIC.

The module contains the definitions of different field classes.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""
from typing import Optional, Union, List, Dict
from warnings import warn

import numpy as np
from openpmd_viewer import OpenPMDTimeSeries

from visualpic.helper_functions import get_common_timesteps
from .field_data import FieldData


class Field():
    """Class representing a field.

    It exposes methods to get the field data at any iteration, as well as
    basic metadata.

    Parameters
    ----------
    name : str
        Name of the field.
    component : str or None
        The component of the field. `None` for scalar fields.
    timeseries : OpenPMDTimeSeries
        Reference to the OpenPMDTimeSeries from which to read the data.
    """
    def __init__(
        self,
        name: str,
        component: str,
        timeseries: OpenPMDTimeSeries,
    ) -> None:
        self._name = name
        self._component = component
        self._ts = timeseries

    @property
    def name(self) -> str:
        return self._name

    @property
    def iterations(self) -> np.ndarray:
        return self._ts.fields_iterations[self._name]

    @property
    def timesteps(self) -> np.ndarray:
        return self.iterations

    @property
    def geometry(self) -> str:
        return self._ts.fields_metadata[self._name]['geometry']

    @property
    def field_name(self) -> str:
        # TODO: deprecate
        return self.name

    @property
    def species_name(self) -> str:
        # TODO: deprecate
        return None

    def get_name(self) -> str:
        """Get field name.

        This method is kept for backward compatibility.
        """
        return self.name

    def get_data(
        self,
        iteration: Optional[int] = None,
        slice_across: Optional[Union[str, List[str]]] = None,
        slice_relative_position: Optional[Union[float, List[float]]] = None,
        m: Optional[Union[int, str]] = 'all',
        theta: Optional[Union[float, None]] = 0.,
        max_resolution_3d: Optional[Union[List[int], None]] = None,
        only_metadata: Optional[bool] = False,
        **kwargs
    ) -> FieldData:
        """Get the field data at a given iteration.

        Parameters
        ----------
        iteration : int
            The iteration from which to read the data.
        slice_across : str or list of str, optional
            Direction(s) across which the data should be sliced
            + In cartesian geometry, elements can be:
                - 1d: 'z'
                - 2d: 'x' and/or 'z'
                - 3d: 'x' and/or 'y' and/or 'z'
            + In cylindrical geometry, elements can be 'r' and/or 'z'
            Returned array is reduced by 1 dimension per slicing.
            If slicing is None, the full grid is returned.
        slice_relative_position : float or list of float, optional
            Number(s) between -1 and 1 that indicate where to slice the data,
            along the directions in `slice_across`
            -1 : lower edge of the simulation box
            0 : middle of the simulation box
            1 : upper edge of the simulation box
            Default: None, which results in slicing at 0 in all direction
            of `slice_across`.
        m : int or str, optional
            Only used for thetaMode geometry
            Either 'all' (for the sum of all the modes)
            or an integer (for the selection of a particular mode)
        theta : float or None, optional
            Only used for thetaMode geometry
            The angle of the plane of observation, with respect to the x axis
            If `theta` is not None, then this function returns a 2D array
            corresponding to the plane of observation given by `theta` ;
            otherwise it returns a full 3D Cartesian array
        max_resolution_3d : list of int or None
            Maximum resolution that the 3D reconstruction of the field (when
            `theta` is None) can have. The list should contain two values,
            e.g. `[200, 100]`, indicating the maximum longitudinal and
            transverse resolution, respectively. This is useful for
            performance reasons, particularly for 3D visualization.
        only_metadata : Optional[bool], optional
            Whether to read only the field metadata, by default False

        Returns
        -------
        FieldData
        """
        iteration, slice_across, slice_relative_position = self._check_old_api(
            iteration, slice_across, slice_relative_position, kwargs
        )
        if iteration is None:
            raise ValueError("Please indicate which `iteration` to read.")
        fld, fld_md = self._ts.get_field(
            field=self._name,
            coord=self._component,
            iteration=iteration,
            m=m,
            theta=theta,
            slice_across=slice_across,
            slice_relative_position=slice_relative_position,
            max_resolution_3d=max_resolution_3d
        )
        return FieldData(
            name=self._name,
            component=self._component,
            array=fld,
            metadata=fld_md,
            geometry=self.geometry,
        )

    def get_geometry(self):
        """Get field geometry.

        This method is only kept for backward compatibility.
        """
        return self.geometry

    def _check_old_api(self, iteration, slice_across, slice_relative_position, kwargs):
        """Check if arguments from the old v0.5 API have been provided.

        If so, raise a warning or try to convert them to the new API.
        """
        if 'field_units' in kwargs:
            warn(
                '`data_units` argument is deprecated since version 0.6. '
                'The data is now always returned in SI units.'
            )
        if 'axes_units' in kwargs:
            warn(
                '`axes_units` argument is deprecated since version 0.6. '
                'The data is now always returned in SI units.'
            )
        if 'axes_to_convert' in kwargs:
            warn(
                '`axes_to_convert` argument is deprecated since version 0.6. '
                'The data is now always returned in SI units.'
            )
        if 'time_units' in kwargs:
            warn(
                '`time_units` argument is deprecated since version 0.6. '
                'The data is now always returned in SI units.'
            )
        if 'time_step' in kwargs:
            warn(
                '`time_step` argument is deprecated since version 0.6. '
                'please use `iteration` instead.'
            )
            iteration = kwargs['time_step']
        if 'slice_dir_i' in kwargs:
            if kwargs['slice_dir_i'] is not None:
                slice_across = [kwargs['slice_dir_i']]
                slice_relative_position = [2 * (kwargs['slice_i'] - 0.5)]
        if 'slice_dir_j' in kwargs:
            if kwargs['slice_dir_j'] is not None:
                slice_across += [kwargs['slice_dir_j']]
                slice_relative_position += [2 * (kwargs['slice_j'] - 0.5)]
        return iteration, slice_across, slice_relative_position


class DerivedField(Field):
    def __init__(self, field_dict: Dict, sim_geometry: str, base_fields: List[Field]):
        self._field_dict = field_dict
        self._sim_geometry = sim_geometry
        self._base_fields = base_fields
        self._common_iterations = get_common_timesteps(base_fields)
        super().__init__(field_dict['name'], None, base_fields[0]._ts)

    @property
    def iterations(self):
        return self._common_iterations

    @property
    def geometry(self):
        return self._sim_geometry

    def get_data(
        self,
        iteration: Optional[int] = None,
        slice_across: Optional[Union[str, List[str]]] = None,
        slice_relative_position: Optional[Union[float, List[float]]] = None,
        m: Optional[Union[int, str]] = 'all',
        theta: Optional[Union[float, None]] = 0.,
        max_resolution_3d: Optional[Union[List[int], None]] = None,
        only_metadata: Optional[bool] = False,
        **kwargs,
    ) -> FieldData:
        field_data = []
        for field in self._base_fields:
            fld_data = field.get_data(
                iteration=iteration,
                slice_across=slice_across,
                slice_relative_position=slice_relative_position,
                m=m,
                theta=theta,
                max_resolution_3d=max_resolution_3d,
                only_metadata=only_metadata,
                **kwargs,
            )
            field_data.append(fld_data.array)
        if not only_metadata:
            fld = self._field_dict['recipe'](field_data, self._sim_geometry,
                                            None)

        return FieldData(
            name=self.name,
            component=self._component,
            array=fld,
            metadata=fld_data._metadata,
            geometry=self.geometry,
            units=self._field_dict['units'],
        )
