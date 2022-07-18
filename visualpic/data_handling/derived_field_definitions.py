"""
This file is part of VisualPIC.

The module contains the definitions of derived fields.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""


import scipy.constants as ct
import numpy as np


derived_field_definitions = []


'''
-------------------------------------------------------------------------------
Template for adding new derived fields. Copy the code below, uncomment and
substitute 'Field name' and 'field_name' with the appropriate name.
-------------------------------------------------------------------------------

# Field name
def calculate_field_name(data_list, sim_geometry, sim_params):
    """
    Defines how the field is calculated for each possible simulation geometry.

    Parameters
    ----------

    data_list : list
        List containing all the FolderFields specified in
        field_name['requirements'][sim_geometry] and in the same order.

    sim_geometry : str
        Geometry of the simulation.

    sim_params : dict
        Provided if needed to calculate some fields. Dictionary containing the
        keys 'n_p' for the plasma density and 'lambda_0' for the laser
        wavelength in the simulation.

    Returns
    -------
    An numpy array containing the field data with the same dimensions as the
    fields in the data_list.
    """
    if sim_geometry == '1d':
        raise NotImplementedError
    elif sim_geometry == '2dcartesian':
        raise NotImplementedError
    elif sim_geometry == '3dcartesian':
        raise NotImplementedError
    elif sim_geometry == 'cylindrical':
        raise NotImplementedError
    elif sim_geometry == 'thetaMode':
        raise NotImplementedError


# Dictionary containing the necessary field information. The requirements for
# each geometry is simply a list of strings with the names of the fields (in
# VisualPIC convention) needed to compute the derived field.
field_name = {'name': 'F',
              'units': '',
              'requirements': {'1d': [],
                               '2dcartesian': [],
                               '3dcartesian': [],
                               'cylindrical': [],
                               'thetaMode': []},
              'recipe': calculate_field_name}


# Finally, add the dictionary to the list.
derived_field_definitions.append(field_name)
'''


# Intensity
def calculate_intensity(data_list, sim_geometry, sim_params):
    if sim_geometry == '1d':
        Ez = data_list[0]
        E2 = Ez**2
    elif sim_geometry == '2dcartesian':
        Ez, Ex = data_list
        E2 = Ez**2 + Ex**2
    elif sim_geometry == '3dcartesian':
        Ez, Ex, Ey = data_list
        E2 = Ez**2 + Ex**2 + Ey**2
    elif sim_geometry == 'cylindrical':
        raise NotImplementedError
    elif sim_geometry == 'thetaMode':
        Ez, Er, Et = data_list
        E2 = Ez**2 + Er**2 + Et**2
    return ct.c * ct.epsilon_0 / 2 * E2


intensity = {'name': 'I',
             'units': 'W/m^2',
             'requirements': {'1d': ['Ez'],
                              '2dcartesian': ['Ez', 'Ex'],
                              '3dcartesian': ['Ez', 'Ex', 'Ey'],
                              'cylindrical': ['Ez', 'Er'],
                              'thetaMode': ['Ez', 'Er', 'Et']},
             'recipe': calculate_intensity}


derived_field_definitions.append(intensity)


# Vector potential
def calculate_vector_pot(data_list, sim_geometry, sim_params):
    l_0 = sim_params['lambda_0']
    if sim_geometry == '1d':
        Ez = data_list[0]
        E2 = Ez**2
    elif sim_geometry == '2dcartesian':
        Ez, Ex = data_list
        E2 = Ez**2 + Ex**2
    elif sim_geometry == '3dcartesian':
        Ez, Ex, Ey = data_list
        E2 = Ez**2 + Ex**2 + Ey**2
    elif sim_geometry == 'cylindrical':
        raise NotImplementedError
    elif sim_geometry == 'thetaMode':
        Ez, Er, Et = data_list
        E2 = Ez**2 + Er**2 + Et**2
    k_0 = 2. * np.pi / l_0
    return np.sqrt(E2) / k_0


vector_pot = {'name': 'A',
              'units': 'V',
              'requirements': {'1d': ['Ez'],
                               '2dcartesian': ['Ez', 'Ex'],
                               '3dcartesian': ['Ez', 'Ex', 'Ey'],
                               'cylindrical': ['Ez', 'Er'],
                               'thetaMode': ['Ez', 'Er', 'Et']},
              'recipe': calculate_vector_pot}


derived_field_definitions.append(vector_pot)


# Normalized vector potential
def calculate_norm_vector_pot(data_list, sim_geometry, sim_params):
    A = calculate_vector_pot(data_list, sim_geometry, sim_params)
    return A / ((ct.m_e * ct.c**2) / ct.e)


norm_vector_pot = {'name': 'a',
                   'units': '',
                   'requirements': {'1d': ['Ez'],
                                    '2dcartesian': ['Ez', 'Ex'],
                                    '3dcartesian': ['Ez', 'Ex', 'Ey'],
                                    'cylindrical': ['Ez', 'Er'],
                                    'thetaMode': ['Ez', 'Er', 'Et']},
                   'recipe': calculate_norm_vector_pot}


derived_field_definitions.append(norm_vector_pot)
