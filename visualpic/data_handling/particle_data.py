from typing import List, Dict
from numbers import Number

import numpy as np


class GridMetadata():
    """Class for storing metadata about the simulation grid.

    This metadata is stored in the particle data and can be useful for
    data visualization.
    """
    def __init__(
        self,
        resolution: List,
        size: List,
        range: List
    ) -> None:
        self.resolution = resolution
        self.size = size
        self.range = range


class ComponentData(np.lib.mixins.NDArrayOperatorsMixin):
    """Class storing the data of each particle component.

    Parameters
    ----------
    name : str
        Name of the component.
    array : ndarray
        Array with the component data.
    time : float
        Time at the iteration from which the data was read.
    grid_metadata : GridMetadata
        Metadata about the simulation grid.
    """
    def __init__(
        self,
        name: str,
        array: np.ndarray,
        time: float,
        grid_metadata: GridMetadata
    ) -> None:
        self._name = name
        self._array = array
        self._time = time
        self._grid_metadata = grid_metadata
        self._legacy_metadata = self._create_legacy_metadata()
        self.__array_interface__ = array.__array_interface__

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        """Allow applying numpy ufuncs to this class.

        The ufuncs will be applied only to the component array. If two
        instances of this class are added, multiplied, etc., the name is
        lost in the instance created by the operation.
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
                array=ufunc(*scalars, **kwargs),
                time=self._time,
                grid_metadata=self._grid_metadata
            )
        else:
            return NotImplemented

    @property
    def name(self) -> str:
        return self._name

    @property
    def array(self) -> np.ndarray:
        return self._array

    @property
    def units(self) -> str:
        return self._get_units()

    def _get_units(self) -> str:
        known_units = {
            'x': 'm',
            'y': 'm',
            'z': 'm',
            'r': 'm',
            'ux': 'm_e*c',
            'uy': 'm_e*c',
            'uz': 'm_e*c',
            'ur': 'm_e*c',
            'charge': 'C',
            'mass': 'kg',
        }
        if self.name in known_units:
            return known_units[self.name]
        else:
            return ''

    def _create_legacy_metadata(self) -> Dict:
        md = {}
        md['units'] = self.units
        md['time'] = {}
        md['time']['value'] = self._time
        md['time']['units'] = 's'
        md['grid'] = {}
        md['grid']['resolution'] = self._grid_metadata.resolution
        md['grid']['size'] = self._grid_metadata.size
        md['grid']['range'] = self._grid_metadata.range
        md['grid']['size_units'] = 'm'
        return md


class ParticleData():
    """Class containing the particle data at a given iteration.

    Parameters
    ----------
    components : list of str
        List of particle components that have been read.
    arrays : list of ndarray
        List of arrays with the data of each component.
    iteration : int
        Iteration at which the data was read.
    time : float
        Time at the iteration from which the data was read.
    grid_params : list
        Grid parameter given by the openpmd-viewer data reader.
    """
    def __init__(
        self,
        components: List[str],
        arrays: List[np.ndarray],
        iteration: int,
        time: float,
        grid_params: List
    ) -> None:
        self._components = components
        self._arrays = arrays
        self._iteration = iteration
        self._time = time
        self._grid_params = grid_params
        self._components_data = {c: ComponentData(c, a, time, self.grid)
                                 for c, a in zip(components, arrays)}
        self._legacy_data = {}
        for c, cd in self._components_data.items():
            if c in ["x", "y", "z"]:
                self._legacy_data[c] = (cd.array, cd._legacy_metadata)
            elif c in ["ux", "uy", "uz"]:
                c = c.replace("u", "p")
                self._legacy_data[c] = (cd.array, cd._legacy_metadata)
            elif c == "w":
                self._legacy_data[c] = (cd.array, cd._legacy_metadata)
                self._legacy_data["q"] = (
                    cd.array * self._components_data["charge"].array,
                    cd._legacy_metadata
                )
                self._legacy_data["m"] = (
                    cd.array * self._components_data["mass"].array,
                    cd._legacy_metadata
                )
        for c in components:
            if not hasattr(self, c):
                setattr(self, c, self._components_data[c])

    def __iter__(self):
        """Enables the particle data to be unpacked as a dictionary.

        Each key of the dictionary contains a tuple with the array of the
        corresponding component and a dictionary with metadata.
        This enables compatibility with the old v0.5 API.
        """
        return iter(self._legacy_data)

    def __getitem__(self, key):
        """Enables the particle data to be accessed as a dictionary.

        Each key of the dictionary contains a tuple with the array of the
        corresponding component and a dictionary with metadata.
        This enables compatibility with the old v0.5 API.
        """
        return self._legacy_data[key]

    def __setitem__(self, key, value):
        self._legacy_data[key] = value

    @property
    def x(self) -> ComponentData:
        return self._components_data['x']

    @property
    def y(self) -> ComponentData:
        return self._components_data['y']

    @property
    def z(self) -> ComponentData:
        return self._components_data['z']

    @property
    def r(self) -> ComponentData:
        return self._components_data['r']

    @property
    def ux(self) -> ComponentData:
        return self._components_data['ux']

    @property
    def uy(self) -> ComponentData:
        return self._components_data['uy']

    @property
    def uz(self) -> ComponentData:
        return self._components_data['uz']

    @property
    def ur(self) -> ComponentData:
        return self._components_data['ur']

    @property
    def w(self) -> ComponentData:
        return self._components_data['w']

    @property
    def q(self) -> ComponentData:
        return self._components_data['w'] * self._components_data['charge']

    @property
    def components(self) -> List[str]:
        return self._components

    @property
    def time(self) -> float:
        return self._time

    @property
    def iteration(self) -> int:
        return self._iteration

    @property
    def grid(self) -> GridMetadata:
        grid_size_dict, grid_range_dict = self._grid_params
        grid_resolution = []
        grid_size = []
        grid_range = []
        if 'z' in grid_size_dict:
            grid_resolution.append(grid_size_dict['z'])
            grid_size.append(grid_range_dict['z'][1] - grid_range_dict['z'][0])
            grid_range.append(grid_range_dict['z'])
        if 'r' in grid_size_dict:
            grid_resolution.append(grid_size_dict['r'])
            grid_size.append(grid_range_dict['r'][1] - grid_range_dict['r'][0])
            grid_range.append(grid_range_dict['r'])
        if 'x' in grid_size_dict:
            grid_resolution.append(grid_size_dict['x'])
            grid_size.append(grid_range_dict['x'][1] - grid_range_dict['x'][0])
            grid_range.append(grid_range_dict['x'])
        if 'y' in grid_size_dict:
            grid_resolution.append(grid_size_dict['y'])
            grid_size.append(grid_range_dict['y'][1] - grid_range_dict['y'][0])
            grid_range.append(grid_range_dict['y'])
        return GridMetadata(
            resolution=grid_resolution,
            size=grid_size,
            range=grid_range
        )
