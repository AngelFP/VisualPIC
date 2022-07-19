"""
This file is part of VisualPIC.

The module contains general helper methods needed in other modules.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""


import sys

import numpy as np


def print_progress_bar(pre_string, step, total_steps, total_dashes=20):
    """
    Prints an updatable progress bar to the terminal output.

    Parameters:
    -----------

    pre_string : str
        A string with a message to include before (in front) the progress bar.

    step : int
        Current step of the progress.

    total_steps : int
        Total number of steps that have to be completed.

    total_dashes : int
        Number of dashes that the progress bar should be made of.

    Returns:
    --------
    A string with the complete path using '/' as separator.
    """
    n_dash = int(round(step/total_steps*total_dashes))
    n_space = total_dashes - n_dash
    status = pre_string + '[' + '-'*n_dash + ' '*n_space + '] '
    if step < total_steps:
        status += '\r'
    sys.stdout.write(status)
    sys.stdout.flush()


def join_infile_path(*paths):
    """
    Join path components using '/' as separator.
    This method is defined as an alternative to os.path.join, which uses '\\'
    as separator in Windows environments and is therefore not valid to navigate
    within data files.

    Parameters:
    -----------
    *paths: all strings with path components to join

    Returns:
    --------
    A string with the complete path using '/' as separator.
    """
    # Join path components
    path = '/'.join(paths)
    # Correct double slashes, if any is present
    path = path.replace('//', '/')
    return path


def get_common_timesteps(data_list):
    """
    Determines the time steps which are common to several data elements (Fields
    or ParticleSpecies).

    Parameters:
    -----------
    data_list : list
        List of Fields and ParticleSpecies

    Returns:
    --------
    An array containing only the common time steps.
    """
    common_ts = np.array([])
    ts_list = []
    for data_element in data_list:
        ts_list.append(data_element.timesteps)
    if len(ts_list) > 0:
        common_ts = get_common_array_elements(ts_list)
    return common_ts


def get_common_array_elements(array_list):
    """
    Returns an array containing only the common elements between all the
    arrays in 'array_list'

    """
    for i, array in enumerate(array_list):
        if i == 0:
            common_els = array
        else:
            common_els = np.intersect1d(common_els, array)
    return common_els


def get_closest_timestep(time_step, time_steps):
    """
    Return the closest time step to the specified desired time step.

    Parameters:
    -----------
    time_step : int
        Desired time step.

    time_steps : ndarray
        Array containing all available time steps.

    Returns:
    --------
    An int with the desired time step if available in time_steps. Otherwise,
    the closest available time step is returned.
    """
    if time_step in time_steps:
        return time_step
    else:
        closest_higher = time_steps[np.where(time_steps > time_step)[0][0]]
        closest_lower = time_steps[np.where(time_steps < time_step)[0][-1]]
        if np.abs(time_step-closest_higher) < np.abs(time_step-closest_lower):
            return closest_higher
        else:
            return closest_lower


def get_next_timestep(current_time_step, time_steps):
    """
    Return the next time step to the specified one.

    Parameters:
    -----------
    current_time_step : int
        Current time step.

    time_steps : ndarray
        Array containing all available time steps.

    Returns:
    --------
    An int with the next available time step. If the current time step is
    already the last one in time_steps, current_time_step is returned.
    """
    if current_time_step not in time_steps:
        raise ValueError(
            'Time step {} is not in the provided timesteps.'.format(
                current_time_step))
    current_index = np.where(time_steps == current_time_step)[0][0]
    if current_index < len(time_steps)-1:
        return time_steps[current_index + 1]
    else:
        return current_time_step


def get_previous_timestep(current_time_step, time_steps):
    """
    Return the previous time step to the specified one.

    Parameters:
    -----------
    current_time_step : int
        Current time step.

    time_steps : ndarray
        Array containing all available time steps.

    Returns:
    --------
    An int with the previous available time step. If the current time step is
    already the first one in time_steps, current_time_step is returned.
    """
    if current_time_step not in time_steps:
        raise ValueError(
            'Time step {} is not in the provided timesteps.'.format(
                current_time_step))
    current_index = np.where(time_steps == current_time_step)[0][0]
    if current_index > 0:
        return time_steps[current_index - 1]
    else:
        return current_time_step
