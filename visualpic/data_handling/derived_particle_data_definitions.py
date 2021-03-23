"""
This file is part of VisualPIC.

The module contains the definitions of derived particle data.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""


derived_particle_data_definitions = []


def get_definition(data_name):
    """
    Return the dictionary with the definition of the specified derived
    component.
    """
    for data_def in derived_particle_data_definitions:
        if data_def['name'] == data_name:
            return data_def


'''
-------------------------------------------------------------------------------
Template for adding new derived particle components. Copy the code below,
and substitute 'Component name' and 'component_name' with the appropriate name.
-------------------------------------------------------------------------------

# Component name
def calculate_component_name(data_dict):
    """
    Defines how the component is calculated.

    Parameters
    ----------

    data_dict : dict
        Dictionary containing the data of all components specified in
        component_name['requirements'].

    Returns
    -------
    An numpy array containing the component data.
    """
    raise NotImplementedError


# Dictionary containing the necessary component information. The requirements
# are specified as a list of the names (in VisualPIC convention) of the
# components needed to compute the derived component.
component_name = {'name': 'c',
                  'units': '',
                  'requirements': [],
                  'recipe': calculate_component_name}


# Finally, add the dictionary to the list.
derived_particle_data_definitions.append(component_name)
'''


# x_prime
def calculate_x_prime(data_dict):
    px = data_dict['px'][0]
    pz = data_dict['pz'][0]
    return px / pz


x_prime = {'name': 'x_prime',
           'units': 'rad',
           'requirements': ['px', 'pz'],
           'recipe': calculate_x_prime}


derived_particle_data_definitions.append(x_prime)
