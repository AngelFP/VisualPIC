from typing import List, Optional, Union, Tuple
from copy import deepcopy

import numpy as np
from openpmd_viewer import OpenPMDTimeSeries

from visualpic import DataContainer
from visualpic.data_handling.field_data import FieldData
from visualpic.data_handling.fields import Field
from visualpic.utilities.caching import lru_cache
from visualpic.utilities.parallel import enable_parallelism
try:
    from lasy.utils.laser_utils import (
        field_to_envelope, field_to_vector_potential,
        vector_potential_to_field, compute_laser_energy, get_spectrum,
        get_duration, create_grid
    )
    from lasy.utils.openpmd_input import reorder_array

    lasy_installed = True
except ImportError:
    lasy_installed = False


class LaserEnvelope(Field):
    """Class containing a laser envelope field.

    Parameters
    ----------
    field : str
        The name of the field from which to read (if the field already
        represents a complex envelope) or extract (if the field represents the
        electric field of a laser) the envelope.
    polarization : str
        Polarization of the laser field from which to extract the envelope.
    timeseries : OpenPMDTimeSeries
        A timeseries from which to read the field data.
    as_potential : bool, optional
        Whether the envelope should be converted to a vector potential, by
        default False.
    normalized : Optional[bool], optional
        Whether the vector potential should be normalized. Only used if
        `as_potential=True`, by default True.
    """
    def __init__(
        self,
        field: str,
        polarization: str,
        timeseries: OpenPMDTimeSeries,
        as_potential: Optional[bool] = False,
        normalized: Optional[bool] = True
    ) -> None:
        super().__init__(field, polarization, timeseries)
        self._as_potential = as_potential
        self._normalized = normalized

    def get_data(
        self,
        iteration: int,
        slice_across: Optional[Union[str, List[str]]] = None,
        slice_relative_position: Optional[Union[float, List[float]]] = None,
        m: Optional[Union[int, str]] = 'all',
        theta: Optional[Union[float, None]] = 0.,
        max_resolution_3d: Optional[Union[List[int], None]] = None,
        laser_propagation_direction: Optional[str] = 'z',
        only_metadata: Optional[bool] = False
    ) -> FieldData:
        # We need to convert lists to tuples, because otherwise lru_cache
        # won't work.
        if isinstance(slice_across, list):
            slice_across = tuple(slice_across)
        if isinstance(slice_relative_position, list):
            slice_relative_position = tuple(slice_relative_position)
        if isinstance(max_resolution_3d, list):
            max_resolution_3d = tuple(max_resolution_3d)
        return self._get_data_cached(
            iteration=iteration,
            slice_across=slice_across,
            slice_relative_position=slice_relative_position,
            m=m,
            theta=theta,
            max_resolution_3d=max_resolution_3d,
            laser_propagation_direction=laser_propagation_direction,
            only_metadata=only_metadata
        )

    @lru_cache(maxsize=4)    
    def _get_data_cached(
        self,
        iteration: int,
        slice_across: Optional[Union[str, Tuple[str]]] = None,
        slice_relative_position: Optional[Union[float, Tuple[float]]] = None,
        m: Optional[Union[int, str]] = 'all',
        theta: Optional[Union[float, None]] = 0.,
        max_resolution_3d: Optional[Union[Tuple[int], None]] = None,
        laser_propagation_direction: Optional[str] = 'z',
        only_metadata: Optional[bool] = False
    ) -> FieldData:
        if isinstance(slice_across, tuple):
            slice_across = list(slice_across)
        if isinstance(slice_relative_position, tuple):
            slice_relative_position = list(slice_relative_position)
        if isinstance(max_resolution_3d, tuple):
            max_resolution_3d = list(max_resolution_3d)
        if slice_across is not None:
            assert laser_propagation_direction not in slice_across, (
                'Cannot slice along laser propagation direction.'
            )
        field = super().get_data(
            iteration, slice_across, slice_relative_position, m, theta,
            max_resolution_3d, only_metadata)

        array = field.array
        md = field._metadata

        is_envelope = np.iscomplexobj(array)

        if field.geometry == '3dcartesian' or theta is None:
            dim = 'xyt'
            assert slice_across is None, (
                'Slicing of 3d envelope not yet supported.'
            )

        elif field.geometry == 'thetaMode':
            dim = 'rt'
            if slice_across is not None:
                # Workaround to support slicing. Create 2D array and radial
                # axis to pass to lasy.
                array_lasy = np.zeros((4, array.size), dtype=array.dtype)
                array_lasy[:] = array
                array = array_lasy
                md = deepcopy(field._metadata)
                md.axes = {0: "r", 1: "z"}
                setattr(md, 'r', np.array([-1.5, -0.5, 0.5, 1.5]))

        array, axes = reorder_array(array, md, dim)
        grid = create_grid(array, axes, dim)

        if not is_envelope:
            grid, omega0 = field_to_envelope(grid, dim)

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
            # Workaround to support slicing. Get single slice of "artificial"
            # 2D array.
            if slice_across is not None:
                array = array[0]

        # Put array back in the original shape.
        if dim == "xyt":
            lasy_axes = ["x", "y", "t"]
            orig_axes = field.axis_labels
            if "z" in orig_axes:
                lasy_axes[-1] = "z"
            sorted_indices = [
                i
                for x in orig_axes
                for i, ax in enumerate(lasy_axes)
                if ax == x
            ]
            array = np.moveaxis(array, [0, 1, 2], sorted_indices)
        else:
            lasy_axes = ["r", "t"]
            orig_axes = field.axis_labels
            if "z" in orig_axes:
                lasy_axes[-1] = "z"
            sorted_indices = [
                i
                for x in orig_axes
                for i, ax in enumerate(lasy_axes)
                if ax == x
            ]
            array = np.moveaxis(array, [0, 1], sorted_indices)

        field = FieldData(
            name=field._name,
            component=field._component,
            array=array,
            metadata=field._metadata,
            geometry=field._geometry,
            units=field._units
        )
        field.omega0 = omega0
        return field


class LaserEnvelopeAmplitude(LaserEnvelope):
    """Class containing the amplitude of a laser envelope field.

    Parameters
    ----------
    field : str
        The name of the field from which to read (if the field already
        represents a complex envelope) or extract (if the field represents the
        electric field of a laser) the envelope.
    polarization : str
        Polarization of the laser field from which to extract the envelope.
    timeseries : OpenPMDTimeSeries
        A timeseries from which to read the field data.
    as_potential : bool, optional
        Whether the envelope should be converted to a vector potential, by
        default False.
    normalized : Optional[bool], optional
        Whether the vector potential should be normalized. Only used if
        `as_potential=True`, by default True.
    """
    def get_data(
        self,
        iteration: int,
        slice_across: Optional[Union[str, List[str]]] = None,
        slice_relative_position: Optional[Union[float, List[float]]] = None,
        m: Optional[Union[int, str]] = 'all',
        theta: Optional[Union[float, None]] = 0.,
        max_resolution_3d: Optional[Union[List[int], None]] = None,
        laser_propagation_direction: Optional[str] = 'z',
        only_metadata: Optional[bool] = False
    ) -> FieldData:
        envelope = super().get_data(
            iteration=iteration,
            slice_across=slice_across,
            slice_relative_position=slice_relative_position,
            m=m,
            theta=theta,
            max_resolution_3d=max_resolution_3d,
            laser_propagation_direction=laser_propagation_direction,
            only_metadata=only_metadata
        )
        return FieldData(
            name=envelope._name,
            component=envelope._component,
            array=np.absolute(envelope.array),
            metadata=envelope._metadata,
            geometry=envelope._geometry,
            units=envelope._units
        )


class LaserEnvelopeReal(LaserEnvelope):
    """Class containing the real part of a laser envelope field.

    Parameters
    ----------
    field : str
        The name of the field from which to read (if the field already
        represents a complex envelope) or extract (if the field represents the
        electric field of a laser) the envelope.
    polarization : str
        Polarization of the laser field from which to extract the envelope.
    timeseries : OpenPMDTimeSeries
        A timeseries from which to read the field data.
    as_potential : bool, optional
        Whether the envelope should be converted to a vector potential, by
        default False.
    normalized : Optional[bool], optional
        Whether the vector potential should be normalized. Only used if
        `as_potential=True`, by default True.
    """
    def get_data(
        self,
        iteration: int,
        slice_across: Optional[Union[str, List[str]]] = None,
        slice_relative_position: Optional[Union[float, List[float]]] = None,
        m: Optional[Union[int, str]] = 'all',
        theta: Optional[Union[float, None]] = 0.,
        max_resolution_3d: Optional[Union[List[int], None]] = None,
        laser_propagation_direction: Optional[str] = 'z',
        only_metadata: Optional[bool] = False
    ) -> FieldData:
        envelope = super().get_data(
            iteration=iteration,
            slice_across=slice_across,
            slice_relative_position=slice_relative_position,
            m=m,
            theta=theta,
            max_resolution_3d=max_resolution_3d,
            laser_propagation_direction=laser_propagation_direction,
            only_metadata=only_metadata
        )
        return FieldData(
            name=envelope._name,
            component=envelope._component,
            array=np.real(envelope.array),
            metadata=envelope._metadata,
            geometry=envelope._geometry,
            units=envelope._units
        )
    

class LaserEnvelopeImag(LaserEnvelope):
    """Class containing the imaginary part of a laser envelope field.

    Parameters
    ----------
    field : str
        The name of the field from which to read (if the field already
        represents a complex envelope) or extract (if the field represents the
        electric field of a laser) the envelope.
    polarization : str
        Polarization of the laser field from which to extract the envelope.
    timeseries : OpenPMDTimeSeries
        A timeseries from which to read the field data.
    as_potential : bool, optional
        Whether the envelope should be converted to a vector potential, by
        default False.
    normalized : Optional[bool], optional
        Whether the vector potential should be normalized. Only used if
        `as_potential=True`, by default True.
    """
    def get_data(
        self,
        iteration: int,
        slice_across: Optional[Union[str, List[str]]] = None,
        slice_relative_position: Optional[Union[float, List[float]]] = None,
        m: Optional[Union[int, str]] = 'all',
        theta: Optional[Union[float, None]] = 0.,
        max_resolution_3d: Optional[Union[List[int], None]] = None,
        laser_propagation_direction: Optional[str] = 'z',
        only_metadata: Optional[bool] = False
    ) -> FieldData:
        envelope = super().get_data(
            iteration=iteration,
            slice_across=slice_across,
            slice_relative_position=slice_relative_position,
            m=m,
            theta=theta,
            max_resolution_3d=max_resolution_3d,
            laser_propagation_direction=laser_propagation_direction,
            only_metadata=only_metadata
        )
        return FieldData(
            name=envelope._name,
            component=envelope._component,
            array=np.imag(envelope.array),
            metadata=envelope._metadata,
            geometry=envelope._geometry,
            units=envelope._units
        )


class LaserAnalysis():
    """Class with utilities for the analysis of laser pulses.

    Parameters
    ----------
    data_container : DataContainer
        A data container with the simulation data.

    """
    def __init__(
        self,
        data_container: DataContainer
    ) -> None:
        assert lasy_installed, (
            "`LaserAnalysis` requires `lasy` to be installed. "
            "You can install it with `pip install lasy`."
        )
        self._dc = data_container

    @lru_cache()
    def get_envelope(
        self,
        field: Optional[str] = 'E',
        polarization: Optional[str] = 'x',
        as_potential: Optional[bool] = False,
        normalized: Optional[bool] = True
    ) -> LaserEnvelope:
        """Get the laser envelope

        Parameters
        ----------
        field : str, optional
            The name of the field from which to read (if the field already
            represents a complex envelope) or extract (if the field represents
            the electric field of a laser) the envelope. By default 'E'.
        polarization : Optional[str], optional
            Polarization of the laser field from which to extract the envelope.
            Only required if the field is not an envelope and if the field
            is scalar (i.e., it has no components). By default 'x'.
        as_potential : bool, optional
            Whether the envelope should be converted to a vector potential, by
            default False.
        normalized : Optional[bool], optional
            Whether the vector potential should be normalized. Only used if
            `as_potential=True`, by default True.

        Returns
        -------
        LaserEnvelope
            A laser envelope field object.
        """
        return LaserEnvelope(
            field=field,
            polarization=polarization,
            timeseries=self._dc._ts,
            as_potential=as_potential,
            normalized=normalized
        )

    @lru_cache()
    def get_envelope_amplitude(
        self,
        field: Optional[str] = 'E',
        polarization: Optional[str] = 'x',
        as_potential: Optional[bool] = False,
        normalized: Optional[bool] = True
    ) -> LaserEnvelopeAmplitude:
        """Get the amplitudeof a laser envelope.

        Parameters
        ----------
        field : str, optional
            The name of the field from which to read (if the field already
            represents a complex envelope) or extract (if the field represents
            the electric field of a laser) the envelope. By default 'E'.
        polarization : Optional[str], optional
            Polarization of the laser field from which to extract the envelope.
            Only required if the field is not an envelope and if the field
            is scalar (i.e., it has no components). By default 'x'.
        as_potential : bool, optional
            Whether the envelope should be converted to a vector potential, by
            default False.
        normalized : Optional[bool], optional
            Whether the vector potential should be normalized. Only used if
            `as_potential=True`, by default True.

        Returns
        -------
        LaserEnvelopeAmplitude
        """
        return LaserEnvelopeAmplitude(
            field=field,
            polarization=polarization,
            timeseries=self._dc._ts,
            as_potential=as_potential,
            normalized=normalized
        )

    @lru_cache()
    def get_envelope_real(
        self,
        field: Optional[str] = 'E',
        polarization: Optional[str] = 'x',
        as_potential: Optional[bool] = False,
        normalized: Optional[bool] = True
    ) -> LaserEnvelopeReal:
        """Get the real part of a laser envelope.

        Parameters
        ----------
        field : str, optional
            The name of the field from which to read (if the field already
            represents a complex envelope) or extract (if the field represents
            the electric field of a laser) the envelope. By default 'E'.
        polarization : Optional[str], optional
            Polarization of the laser field from which to extract the envelope.
            Only required if the field is not an envelope and if the field
            is scalar (i.e., it has no components). By default 'x'.
        as_potential : bool, optional
            Whether the envelope should be converted to a vector potential, by
            default False.
        normalized : Optional[bool], optional
            Whether the vector potential should be normalized. Only used if
            `as_potential=True`, by default True.

        Returns
        -------
        LaserEnvelopeReal
        """
        return LaserEnvelopeReal(
            field=field,
            polarization=polarization,
            timeseries=self._dc._ts,
            as_potential=as_potential,
            normalized=normalized
        )

    @lru_cache()
    def get_envelope_imag(
        self,
        field: Optional[str] = 'E',
        polarization: Optional[str] = 'x',
        as_potential: Optional[bool] = False,
        normalized: Optional[bool] = True
    ) -> LaserEnvelopeImag:
        """Get the imaginary part of a laser envelope.

        Parameters
        ----------
        field : str, optional
            The name of the field from which to read (if the field already
            represents a complex envelope) or extract (if the field represents
            the electric field of a laser) the envelope. By default 'E'.
        polarization : Optional[str], optional
            Polarization of the laser field from which to extract the envelope.
            Only required if the field is not an envelope and if the field
            is scalar (i.e., it has no components). By default 'x'.
        as_potential : bool, optional
            Whether the envelope should be converted to a vector potential, by
            default False.
        normalized : Optional[bool], optional
            Whether the vector potential should be normalized. Only used if
            `as_potential=True`, by default True.

        Returns
        -------
        LaserEnvelopeImag
        """
        return LaserEnvelopeImag(
            field=field,
            polarization=polarization,
            timeseries=self._dc._ts,
            as_potential=as_potential,
            normalized=normalized
        )

    @enable_parallelism('width')
    def get_width(
        self,
        iteration: int,
        field: Optional[str] = 'E',
        polarization: Optional[str] = 'x'
    ) -> float:
        """Calculate the laser pulse width.
        
        The width is defined as the radial position where the electric field
        decays by 1/e.

        Parameters
        ----------
        iteration : int
            The simulation iteration at which to calculate the laser width.
        field : str, optional
            The name of the field from which to read (if the field already
            represents a complex envelope) or extract (if the field represents
            the electric field of a laser) the envelope. By default 'E'.
        polarization : Optional[str], optional
            Polarization of the laser field from which to extract the envelope.
            Only required if the field is not an envelope and if the field
            is scalar (i.e., it has no components). By default 'x'.

        Returns
        -------
        float
            The pulse width in meters.
        """
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
    
    @enable_parallelism('duration')
    def get_duration(
        self,
        iteration: int,
        field: Optional[str] = 'E',
        polarization: Optional[str] = 'x'
    ) -> float:
        """Calculate the laser pulse duration.

        The pulse duration is defined as the RMS duration of the laser
        intensity.

        Parameters
        ----------
        iteration : int
            The simulation iteration at which to calculate the pulse duration.
        field : str, optional
            The name of the field from which to read (if the field already
            represents a complex envelope) or extract (if the field represents
            the electric field of a laser) the envelope. By default 'E'.
        polarization : Optional[str], optional
            Polarization of the laser field from which to extract the envelope.
            Only required if the field is not an envelope and if the field
            is scalar (i.e., it has no components). By default 'x'.

        Returns
        -------
        float
            The pulse duration in seconds.
        """
        env = self.get_envelope(field, polarization).get_data(iteration)
        if len(env.axis_labels) == 3:
            dim = 'xyt'
        elif len(env.axis_labels) == 2:
            dim = 'rt'
        array, axes = reorder_array(env.array, env._metadata, dim)
        grid = create_grid(array, axes, dim)
        return get_duration(grid, dim)

    @enable_parallelism('a0')
    def get_a0(
        self,
        iteration: int,
        field: Optional[str] = 'E',
        polarization: Optional[str] = 'x'
    ) -> float:
        """Calculate maximum of the normalized vector potential.

        Parameters
        ----------
        iteration : int
            The simulation iteration at which to calculate a0.
        field : str, optional
            The name of the field from which to read (if the field already
            represents a complex envelope) or extract (if the field represents
            the electric field of a laser) the envelope. By default 'E'.
        polarization : Optional[str], optional
            Polarization of the laser field from which to extract the envelope.
            Only required if the field is not an envelope and if the field
            is scalar (i.e., it has no components). By default 'x'.

        Returns
        -------
        float
            The peak of the normalized vector potential.
        """
        env = self.get_envelope(field, polarization,
                                as_potential=True).get_data(iteration)
        return np.max(np.abs(env.array))

    @enable_parallelism('spectrum')
    def get_spectrum(
        self,
        iteration: int,
        field: Optional[str] = 'E',
        polarization: Optional[str] = 'x',
        is_envelope: Optional[bool] = True,
        range: Optional[list] = None,
        bins: Optional[int] = 20,
        on_axis: Optional[bool] = False
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate spectral density of a laser pulse.

        Parameters
        ----------
        iteration : int
            The simulation iteration at which to calculate a0.
        field : str, optional
            The name of the field from which to read (if the field already
            represents a complex envelope) or extract (if the field represents
            the electric field of a laser) the envelope. By default 'E'.
        polarization : Optional[str], optional
            Polarization of the laser field from which to extract the envelope.
            Only required if the field is not an envelope and if the field
            is scalar (i.e., it has no components). By default 'x'.
        is_envelope : bool (optional)
            Whether the field is a complex envelope. By default True.
        range : list of float (optional)
            List of two values indicating the minimum and maximum frequency of
            the spectrum. If provided, only the FFT spectrum within this range
            will be returned using interpolation. By default None.
        bins : int (optional)
            Number of bins of to which to interpolate the spectrum if a `range`
            is given. By default 20.
        on_axis : bool
            Whether to get the spectrum on axis or the transversely summed
            spectrum of the whole field. By default False.

        Returns
        -------
        spectral density : ndarray
            Array with the spectral density in J/(rad/s).
        omega : ndarray
            Array with the angular frequencies of the spectrum.
        """
        omega0 = None
        if is_envelope:
            env = self.get_envelope(field, polarization).get_data(iteration)
            omega0 = env.omega0
        else:
            env = self._dc.get_field(field, polarization).get_data(iteration)
        if len(env.axis_labels) == 3:
            dim = 'xyt'
        elif len(env.axis_labels) == 2:
            dim = 'rt'
        array, axes = reorder_array(env.array, env._metadata, dim)
        grid = create_grid(array, axes, dim)
        return get_spectrum(
            grid=grid,
            dim=dim,
            bins=bins,
            range=range,
            omega0=omega0,
            is_envelope=is_envelope,
            method='on_axis' if on_axis else 'sum'
        )

    @enable_parallelism('energy')
    def get_energy(
        self,
        iteration: int,
        field: Optional[str] = 'E',
        polarization: Optional[str] = 'x'
    ) -> float:
        """Calculate the laser energy.

        Parameters
        ----------
        iteration : int
            The simulation iteration at which to calculate a0.
        field : str, optional
            The name of the field from which to read (if the field already
            represents a complex envelope) or extract (if the field represents
            the electric field of a laser) the envelope. By default 'E'.
        polarization : Optional[str], optional
            Polarization of the laser field from which to extract the envelope.
            Only required if the field is not an envelope and if the field
            is scalar (i.e., it has no components). By default 'x'.

        Returns
        -------
        float
            The laser energy in Joule.
        """
        env = self.get_envelope(field, polarization).get_data(iteration)
        if len(env.axis_labels) == 3:
            dim = 'xyt'
        elif len(env.axis_labels) == 2:
            dim = 'rt'
        array, axes = reorder_array(env.array, env._metadata, dim)
        grid = create_grid(array, axes, dim)
        return compute_laser_energy(dim, grid)
