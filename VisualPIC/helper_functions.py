"""This module contains methods needed by other modules"""

import sys


def print_progress_bar(pre_string, step, total_steps):
    n_dash = int(round(step/total_steps*20))
    n_space = 20 - n_dash
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
