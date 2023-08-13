"""
This file is part of VisualPIC.

The module contains the definitions of different field classes.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""
from typing import Optional, Union, List

import numpy as np
from openpmd_viewer import OpenPMDTimeSeries

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
        self._iterations = timeseries.fields_iterations[name]
        self._component = component
        self._ts = timeseries

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def iterations(self) -> np.ndarray:
        return self._iterations
    
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
        iteration: int,
        slice_across: Optional[Union[str, List[str]]] = None,
        slice_relative_position: Optional[Union[float, List[float]]] = None,
        m: Optional[Union[int, str]] = 'all',
        theta: Optional[Union[float, None]] = 0.,
        max_resolution_3d: Optional[Union[List[int], None]] = None,
        only_metadata: Optional[bool] = False
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
            iteration=iteration,
            time=self._get_time(iteration)
        )
    
    def get_geometry(self):
        """Get field geometry.
        
        This method is only kept for backward compatibility.
        """
        return self.geometry
    
    def _get_time(self, iteration) -> float:
        """Get time at given iteration."""
        field_its = self._ts.fields_iterations[self._name]
        field_t = self._ts.fields_t[self._name]
        return field_t[np.where(field_its == iteration)[0][0]]
