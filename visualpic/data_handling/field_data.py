from typing import List
from numbers import Number

import numpy as np
from openpmd_viewer.openpmd_timeseries import FieldMetaInformation


class FieldData(np.lib.mixins.NDArrayOperatorsMixin):
    """Class containing the field data at a given iteration.

    Parameters
    ----------
    name : str
        Name of the field.
    component : str
        Component of the field.
    array : ndarray
        Array with the field data.
    metadata : FieldMetaInformation
        Field metadata from the openpmd-viewer.
    geometry : str
        Field geometry.
    iteration : int
        Current iteration.
    time : float
        Time at the current iteration.
    """
    def __init__(
        self,
        name: str,
        component: str,
        array: np.ndarray,
        metadata: FieldMetaInformation,
        geometry: str
    ) -> None:
        self._name = name
        self._component = component
        self._array = array
        self._metadata = metadata
        self._geometry = geometry
        self._legacy_metadata = self._create_legacy_metadata()
        self._legacy_api = (self.array, self._legacy_metadata)
        # Enable some array-like functionality (such as passing to matplotlib).
        self.__array_interface__ = array.__array_interface__

    def __iter__(self):
        """Enables the field data to be unpacked in two items.

        The first one is the field array and the second one is the legacy
        dictionary with field metadata. This enables compatibility with the
        old v0.5 API.
        """
        yield self._legacy_api[0]
        yield self._legacy_api[1]

    def __getitem__(self, index):
        """Enables the field data to be accessed as a tuple with two items.

        The first one is the field array and the second one is the legacy
        dictionary with field metadata. This enables compatibility with the
        old v0.5 API.
        """
        return self._legacy_api[index]

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        """Allow applying numpy ufuncs to this class.

        The ufuncs will be applied only to the field array. If two
        instances of this class are added, multiplied, etc., some field
        metadata is lost (as it is hard to define in general) in the
        instance created by the operation.
        """
        if method == '__call__':
            scalars = []
            for input in inputs:
                if isinstance(input, Number):
                    scalars.append(input)
                elif isinstance(input, self.__class__):
                    scalars.append(input._array)
                else:
                    return NotImplemented
            return self.__class__(
                name='',
                component='',
                array=ufunc(*scalars, **kwargs),
                metadata=self._metadata,
                geometry=self.geometry,
            )
        else:
            return NotImplemented

    @property
    def name(self) -> str:
        return self._name

    @property
    def component(self) -> str:
        return self._component

    @property
    def array(self) -> np.ndarray:
        return self._array

    @property
    def geometry(self) -> str:
        return self._geometry

    @property
    def iteration(self) -> int:
        return self._metadata.iteration

    @property
    def units(self) -> str:
        return self._get_units()

    @property
    def axis_labels(self) -> List[str]:
        return list(self._metadata.axes.values())

    @property
    def time(self) -> np.ndarray:
        return self._metadata.time

    @property
    def time_units(self) -> np.ndarray:
        return 's'

    @property
    def x(self) -> np.ndarray:
        return self._metadata.x

    @property
    def y(self) -> np.ndarray:
        return self._metadata.y

    @property
    def z(self) -> np.ndarray:
        return self._metadata.z

    @property
    def x_min(self) -> float:
        return self._metadata.xmin

    @property
    def y_min(self) -> float:
        return self._metadata.ymin

    @property
    def z_min(self) -> float:
        return self._metadata.zmin

    @property
    def x_max(self) -> float:
        return self._metadata.xmax

    @property
    def y_max(self) -> float:
        return self._metadata.ymax

    @property
    def z_max(self) -> float:
        return self._metadata.zmax

    @property
    def dx(self) -> float:
        return self._metadata.dx

    @property
    def dy(self) -> float:
        return self._metadata.dy

    @property
    def dz(self) -> float:
        return self._metadata.dz

    @property
    def x_units(self) -> str:
        return 'm'

    @property
    def y_units(self) -> str:
        return 'm'

    @property
    def z_units(self) -> str:
        return 'm'

    @property
    def imshow_extent(self) -> List[float]:
        assert len(self.axis_labels) == 2, (
            'Can only generate `imshow_extent` for 2D data.'
        )
        return self._metadata.imshow_extent

    def _get_units(self):
        known_units = {
            'E': 'V/m',
            'B': 'T',
            'rho': 'C/m^3',
            'J': 'A'
        }
        if self.name in known_units:
            return known_units[self.name]
        else:
            return ''

    def _create_legacy_metadata(self):
        """Creates a dictionary with field metadata to enable compatibility
        with the ond v0.5 API"""
        md = {}
        md['time'] = {}
        md['time']['value'] = self.time
        md['time']['units'] = self.time_units
        md['field'] = {}
        md['field']['geometry'] = self.geometry
        md['field']['axis_labels'] = self.axis_labels
        md['field']['units'] = self.units
        md['axis'] = {}
        for axis in self.axis_labels:
            md['axis'][axis] = {}
            md['axis'][axis]['units'] = 'm'
            md['axis'][axis]['array'] = getattr(self, axis)
            md['axis'][axis]['spacing'] = getattr(self, f'd{axis}')
            md['axis'][axis]['min'] = getattr(self, f'{axis}_min')
            md['axis'][axis]['max'] = getattr(self, f'{axis}_max')
        return md
