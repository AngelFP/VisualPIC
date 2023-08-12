"""
This file is part of VisualPIC.

The module contains the definitions of the ParticleSpecies class.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""

from openpmd_viewer import OpenPMDTimeSeries


class ParticleSpecies():

    """Class providing access to the data of a particle species"""

    def __init__(
        self,
        species_name: str,
        timeseries: OpenPMDTimeSeries
    ):
        """
        Initialize the particle species.

        Parameters
        ----------

        species_name : str
            Name of the particle species.

        components_in_file : list
            List of string containing the names (in VisualPIC convention) of
            the particle components available in the data files for this
            species.

        species_timesteps : array
            A sorted numpy array numbering all the timesteps containing data
            of this particle species.

        timestep_to_files : dict or list
            A dictionary relating each time step to a data file. Alternatively,
            a list with the same length and order as species_timesteps
            containing the path to each data file can also be provided.

        data_reader : ParticleReader
            An instance of a ParticleReader of the corresponding simulation
            code.
        """
        self.species_name = species_name
        self.timeseries = timeseries
        self.associated_fields = []

    @property
    def available_components(self):
        return self.timeseries.avail_record_components[self.species_name]

    @property
    def iterations(self):
        return self.timeseries.species_iterations[self.species_name]

    def get_data(self, iteration, components_list=[]):
        """
        Get the species data of the requested components and time step.

        Parameters
        ----------

        iteration : int
            Time step at which to read the data. This is the time step number
            as generated by the simulation code, not the index of the time
            step list.

        components_list : list
            List of strings containing the names of the components to be read.

        Returns
        -------
        A dictionary containing the particle data. The keys correspond to the
        names of each of the requested components. Each key stores a tuple
        where the first element is the data array and the second is the
        metadata dictionary.
        """
        # By default, if no list is specified, get all components.
        if not components_list:
            components_list = self.available_components
        
        data = self.timeseries.get_particle(
            var_list=components_list,
            species=self.species_name,
            iteration=iteration            
        )
        
        return data

    def contains(self, data):
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
