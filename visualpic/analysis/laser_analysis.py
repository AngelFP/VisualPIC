from typing import List, Optional, Union

import numpy as np
from openpmd_viewer import OpenPMDTimeSeries

from visualpic import DataContainer
from visualpic.data_handling.field_data import FieldData
from visualpic.data_handling.fields import Field
from visualpic.utilities.caching import lru_cache
from visualpic.utilities.parallel import enable_threading
from lasy.utils.laser_utils import (
    field_to_envelope, field_to_vector_potential, vector_potential_to_field,
    compute_laser_energy, get_spectrum, get_duration, create_grid)
from lasy.utils.openpmd_input import reorder_array


class LaserAnalysis():
    def __init__(
        self,
        data_container: DataContainer
    ) -> None:
        self._dc = data_container

    @lru_cache()
    def get_envelope(
        self,
        field='E',
        polarization='x',
        as_potential=False,
        normalized=True
    ):
        return LaserEnvelope(
            field=field,
            polarization=polarization,
            timeseries=self._dc._ts,
            as_potential=as_potential,
            normalized=normalized
        )

    @enable_threading('width')
    def get_width(
        self,
        iteration,
        field='E',
        polarization='x'
    ):
        env = self.get_envelope(field, polarization).get_data(iteration)
        assert env.array.ndim == 2

        # Project envelope to r
        env_proj = np.sum(np.abs(env.array), axis=1)

        # Remove lower half (field has radial symmetry)
        nr = len(env_proj)
        env_proj = env_proj[int(nr/2):]

        # Maximum is on axis
        env_max = env_proj[0]

        # Get first index of value below a_max / e
        i_first = np.where(env_proj <= env_max / np.e)[0][0]

        # Do linear interpolation to get more accurate value of w.
        # We build a line y = a + b*x, where:
        #     b = (y_2 - y_1) / (x_2 - x_1)
        #     a = y_1 - b*x_1
        #
        #     y_1 is the value of a_proj at i_first - 1
        #     y_2 is the value of a_proj at i_first
        #     x_1 and x_2 are the radial positions of y_1 and y_2
        #
        # We can then determine the spot size by interpolating between y_1
        # and y_2, that is, do x = (y - a) / b, where y = a_max/e
        y_1 = env_proj[i_first - 1]
        y_2 = env_proj[i_first]
        x_1 = (i_first-1) * env.dr + env.dr/2
        x_2 = i_first * env.dr + env.dr/2
        b = (y_2 - y_1) / (x_2 - x_1)
        a = y_1 - b*x_1
        w = (env_max/np.e - a) / b
        return w
    
    @enable_threading('duration')
    def get_duration(
        self,
        iteration,
        field='E',
        polarization='x'
    ):
        env = self.get_envelope(field, polarization).get_data(iteration)
        if len(env.axis_labels) == 3:
            dim = 'xyt'
        elif len(env.axis_labels) == 2:
            dim = 'rt'
        array, axes = reorder_array(env.array, env._metadata, dim)
        grid = create_grid(array, axes, dim)
        return get_duration(grid, dim)

    @enable_threading('a0')
    def get_a0(
        self,
        iteration,
        field='E',
        polarization='x'
    ):
        env = self.get_envelope(field, polarization,
                                as_potential=True).get_data(iteration)
        return np.max(np.abs(env.array))

    @enable_threading('spectrum')
    def get_spectrum(
        self,
        iteration,
        field='E',
        polarization='x',
        bins=20,
        range=None
    ):
        env = self.get_envelope(field, polarization).get_data(iteration)
        omega0 = env.omega0
        if len(env.axis_labels) == 3:
            dim = 'xyt'
            phase_unwrap_1d = True
        elif len(env.axis_labels) == 2:
            dim = 'rt'
            phase_unwrap_1d = False
        array, axes = reorder_array(env.array, env._metadata, dim)
        grid = create_grid(array, axes, dim)
        return get_spectrum(
            grid=grid,
            dim=dim,
            bins=bins,
            range=range,
            omega0=omega0,
            phase_unwrap_1d=phase_unwrap_1d,
        )

    @enable_threading('energy')
    def get_energy(
        self,
        iteration,
        field='E',
        polarization='x'
    ):
        env = self.get_envelope(field, polarization).get_data(iteration)
        if len(env.axis_labels) == 3:
            dim = 'xyt'
        elif len(env.axis_labels) == 2:
            dim = 'rt'
        array, axes = reorder_array(env.array, env._metadata, dim)
        grid = create_grid(array, axes, dim)
        return compute_laser_energy(dim, grid)


class LaserEnvelope(Field):
    def __init__(
        self,
        field,
        polarization: str,
        timeseries: OpenPMDTimeSeries,
        as_potential=False,
        normalized=True
    ) -> None:
        super().__init__(field, polarization, timeseries)
        self._as_potential = as_potential
        self._normalized = normalized

    @lru_cache(maxsize=4)
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
        field = super().get_data(
            iteration, slice_across, slice_relative_position, m, theta,
            max_resolution_3d, only_metadata)

        is_envelope = np.iscomplexobj(field.array)

        if len(field.axis_labels) == 3:
            dim = 'xyt'
            phase_unwrap_1d = True
        elif len(field.axis_labels) == 2:
            dim = 'rt'
            phase_unwrap_1d = False
        array, axes = reorder_array(field.array, field._metadata, dim)
        grid = create_grid(array, axes, dim)

        if not is_envelope:
            grid, omega0 = field_to_envelope(grid, dim, phase_unwrap_1d)

        else:
            # assume that it is a normalized vector potential.
            omega0 = field.field_attributes['angularFrequency']
            grid.field = vector_potential_to_field(grid, omega0)

        if self._as_potential:
            array = field_to_vector_potential(grid, omega0)
        else:
            array = grid.field

        if dim == 'rt':
            array = array[0]
            nr, nz = array.shape
            array_extended = np.zeros((nr*2, nz), dtype=np.complex128)
            array_extended[:nr] = array[::-1]
            array_extended[nr:] = array
            array = array_extended[:, ::-1]

        field.array = array
        field.omega0 = omega0
        return field
