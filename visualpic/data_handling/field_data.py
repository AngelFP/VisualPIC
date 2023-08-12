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
        geometry: str,
        iteration: int,
        time: float
    ) -> None:
        self._name = name
        self._component = component
        self._array = array
        self._metadata = metadata
        self._geometry = geometry
        self._iteration = iteration,
        self._time = time
        self.__array_interface__ = array.__array_interface__

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        if method == '__call__':
            scalars = []
            for input in inputs:
                if isinstance(input, Number):
                    scalars.append(input)
                elif isinstance(input, self.__class__):
                    scalars.append(input._array)
                else:
                    return NotImplemented
            return self.__class__(ufunc(*scalars, **kwargs), self._metadata)
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
    def units(self) -> str:
        raise NotImplementedError

    @property
    def axis_labels(self) -> List[str]:
        return self._metadata.axes

    @property
    def time(self) -> np.ndarray:
        return self._time

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
