"""
This file is part of VisualPIC.

The module contains the definitions of the ParticleSpecies class.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""
from typing import Optional, Union, List
from copy import deepcopy
from warnings import warn

import numpy as np
from openpmd_viewer import OpenPMDTimeSeries

from .particle_data import ParticleData


class ParticleSpecies():
    """Class providing access to the data of a particle species.

    Parameters
    ----------
    name : str
        Name of the particle species.
    timeseries : OpenPMDTimeSeries
        Reference to the OpenPMDTimeSeries from which to read the data.
    """
    def __init__(
        self,
        name: str,
        timeseries: OpenPMDTimeSeries
    ) -> None:
        self._name = name
        self._ts = timeseries

    @property
    def name(self) -> str:
        return self._name

    @property
    def species_name(self) -> str:
        # kept of backward compatibility.
        return self._name

    @property
    def available_components(self) -> List[str]:
        return self._ts.avail_record_components[self._name]

    @property
    def iterations(self) -> np.ndarray:
        return self._ts.species_iterations[self._name]

    @property
    def timesteps(self) -> np.ndarray:
        # kept of backward compatibility.
        return self.iterations

    def get_data(
        self,
        iteration: int,
        components_list: Optional[List[str]] = None,
        data_units: Optional[List[str]] = None
    ) -> ParticleData:
        """
        Get the species data of the requested components and time step.

        Parameters
        ----------
        iteration : int
            Iteration from which to read the data.
        components_list : list, optional
            List of strings containing the names of the components to be read.
            If `None` all components will be read. By defaulf, None.
        data_units : list, optional
            Do not use, it does not have any effect. The data is always
            returned in SI units.

            .. deprecated:: 0.6.0

        Returns
        -------
        ParticleData
        """
        # Check given names for backward compatibility with old v0.5 API.
        has_old_names = False
        if components_list:
            old_names = components_list
            components_list = deepcopy(components_list)
            for i, c in enumerate(components_list):
                if c not in self.available_components:
                    new_name = self._check_name_for_backward_compatibility(c)
                    if new_name:
                        components_list[i] = new_name
                        has_old_names = True
            # In the old API, 'q' stands for the macroparticle charge, so we
            # need the weight to compute it.
            if 'q' in old_names:
                components_list.append('w')
        if data_units is not None:
            warn(
                '`data_units` argument has been deprecated since version 0.6. '
                'The data is now always returned in SI units.'
            )

        # By default, if no list is specified, get all components.
        else:
            components_list = self.available_components

        # Get particle data.
        data = self._ts.get_particle(
            var_list=components_list,
            species=self._name,
            iteration=iteration
        )

        # Get the macroparticle charge, if using the old API.
        if has_old_names:
            if 'q' in old_names:
                i_q = old_names.index('q')
                w = data.pop(-1)
                data[i_q] *= w

        return ParticleData(
            components=components_list if not has_old_names else old_names,
            arrays=data,
            iteration=iteration,
            time=self._get_time(iteration),
            grid_params=self._ts.data_reader.get_grid_parameters(
                iteration=iteration,
                avail_fields=self._ts.avail_fields,
                metadata=self._ts.fields_metadata
            )
        )

    def contains(
        self,
        data: Union[str, List[str]]
    ) -> bool:
        """
        Check whether the species contains the specified data.

        Parameters
        ----------
        data : str or list
            A string or a list of strings with the names of the data elements
            that should be checked (can be both particle components and
            associated fields).

        Returns
        -------
        True if the species contains all data elements specified in 'data'.
        False otherwise.

        """
        if not isinstance(data, list):
            data = [data]
        comps = self.available_components()
        return set(data) <= set(comps)

    def get_list_of_available_components(self) -> List[str]:
        """Get list of the components available in this species.

        This method is kept for backward compatibility.
        """
        return self.available_components

    def _get_time(self, iteration) -> float:
        """Get time of current iteration."""
        species_its = self._ts.species_iterations[self._name]
        species_t = self._ts.species_t[self._name]
        return species_t[np.where(species_its == iteration)[0][0]]

    def _check_name_for_backward_compatibility(
        self,
        component_name: str
    ) -> Union[str, None]:
        """If the component has a name from the old API, return new name."""
        old_name_relations = {
            'pz': 'uz',
            'px': 'ux',
            'py': 'uy',
            'q': 'charge',
            'm': 'mass',
            'tag': 'id',
        }
        if component_name in old_name_relations:
            return old_name_relations[component_name]
