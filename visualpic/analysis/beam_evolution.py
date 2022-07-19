"""
This file is part of VisualPIC.

The module contains methods for analyzing the beam evolution within the
simulation.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""

import os
from functools import partial
from multiprocessing import cpu_count

import numpy as np
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import h5py
import aptools.data_analysis.beam_diagnostics as bd
import aptools.data_processing.beam_filtering as bf

from visualpic.data_handling.data_container import DataContainer


def analyze_beam_evolution(
        sim_path, sim_code, species_name, plasma_density=None,
        t_step_range=None, n_slices=10, slice_len=None,
        filter_min=[None, None, None, None, None, None, None],
        filter_max=[None, None, None, None, None, None, None],
        filter_sigma=[None, None, None, None, None, None, None], save_to=None,
        saved_file_name='beam_params.h5', parallel=False, n_proc=None):
    # Load data.
    print('Scanning simulation folder... ', end='', flush=True)
    dc = DataContainer(sim_code, sim_path, plasma_density)
    dc.load_data()
    print('Done.')
    beam = dc.get_species(species_name)
    time_steps = beam.timesteps
    if t_step_range is not None:
        time_steps = time_steps[np.where((time_steps >= t_step_range[0]) &
                                         (time_steps <= t_step_range[1]))]

    # Analyze beam.
    tqdm_params = {'ascii': True, 'desc': 'Analyzing beam evolution... '}
    if parallel:
        if n_proc is None:
            n_proc = cpu_count()
        part = partial(
            _analyze_beam_timestep, beam=beam, n_slices=n_slices,
            slice_len=slice_len, filter_min=filter_min, filter_max=filter_max,
            filter_sigma=filter_sigma)
        ts_params = process_map(part, time_steps, max_workers=n_proc,
                                **tqdm_params)
    else:
        ts_params = []
        for i, time_step in enumerate(tqdm(time_steps, **tqdm_params)):
            ts_params.append(
                _analyze_beam_timestep(time_step, beam, n_slices, slice_len,
                                       filter_min, filter_max, filter_sigma))

    # Group time steps parameters into arrays.
    var_arrays_dict = {}
    for var in _first_true(ts_params).keys():
        var_array = np.zeros(len(ts_params))
        for i, ts in enumerate(ts_params):
            if ts is not None:
                var_array[i] = ts[var]
            else:
                var_array[i] = np.nan
        var_arrays_dict[var] = var_array

    print('Done.')

    # Save to file.
    if save_to is not None:
        print('Saving to file... ', end='')
        if not saved_file_name.endswith('.h5'):
            saved_file_name += '.h5'
        file_path = os.path.join(save_to, saved_file_name)
        with h5py.File(file_path, 'w') as f:
            for var, arr in var_arrays_dict.items():
                dset = f.create_dataset(var, data=arr)
                dset.attrs['units'] = _get_data_units(var)
        print('Done.')

    return var_arrays_dict


def _analyze_beam_timestep(time_step, beam, n_slices, slice_len, filter_min,
                           filter_max, filter_sigma):
    data = beam.get_data(time_step, ['x', 'y', 'z', 'px', 'py', 'pz', 'q'],
                         data_units='SI')
    x, *_ = data['x']
    y, *_ = data['y']
    z, *_ = data['z']
    px, *_ = data['px']
    py, *_ = data['py']
    pz, *_ = data['pz']
    q, *_ = data['q']

    if len(x) <= 1:
        return None

    # Apply filters
    if any(el is not None for el in filter_min + filter_max):
        x, y, z, px, py, pz, q = bf.filter_beam(
            np.array([x, y, z, px, py, pz, q]), filter_min, filter_max)
        if len(x) <= 1:
            return None

    if any(el is not None for el in filter_sigma):
        x, y, z, px, py, pz, q = bf.filter_beam_sigma(
            np.array([x, y, z, px, py, pz, q]), filter_sigma, w=q)
        if len(x) <= 1:
            return None

    # Analyze beam
    return bd.general_analysis(x, y, z, px, py, pz, q, n_slices=n_slices,
                               len_slice=slice_len)


def _get_data_units(var):
    units_dict = {
        'x_avg': 'm',
        'y_avg': 'm',
        'z_avg': 'm',
        'theta_x': 'rad',
        'theta_y': 'rad',
        'sigma_x': 'm',
        'sigma_y': 'm',
        'sigma_z': 'm',
        'z_fwhm': 'm',
        'sigma_px': 'm*c',
        'sigma_py': 'm*c',
        'alpha_x': '',
        'alpha_y': '',
        'beta_x': 'm',
        'beta_y': 'm',
        'gamma_x': '1/m',
        'gamma_y': '1/m',
        'emitt_nx': 'm',
        'emitt_ny': 'm',
        'emitt_nx_sl': 'm',
        'emitt_ny_sl': 'm',
        'ene_avg': 'm*c^2',
        'rel_ene_sp': '',
        'rel_ene_sp_sl': '',
        'i_peak': 'A',
        'q': 'C'
    }
    if var in units_dict:
        return units_dict[var]
    else:
        return ''


def _first_true(iterable, default=False, pred=None):
    """Returns the first true value in the iterable.

    If no true value is found, returns *default*

    If *pred* is not None, returns the first item
    for which pred(item) is true.

    From https://docs.python.org/3/library/itertools.html#itertools-recipes.

    """
    return next(filter(pred, iterable), default)
