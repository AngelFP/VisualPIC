""" Colletion of command-line methods for data analysis """

import numpy as np
import aptools.data_analysis.beam_diagnostics as bd
from VisualPIC.DataReading.folder_scanners import (OsirisFolderScanner,
                                                   OpenPMDFolderScanner, 
                                                   HiPACEFolderScanner)
from VisualPIC.helper_functions import print_progress_bar


def analyze_beam_evolution(sim_path, sim_code, species_name,
                           t_step_range=None, slice_len=0.1e-6, save_to=None, 
                           saved_file_name='beam_params'):
    scanner_associations = {'osiris': OsirisFolderScanner,
                            'hipace': HiPACEFolderScanner,
                            'openpmd': OpenPMDFolderScanner}

    print('Scanning simulation folder... ', end = '')
    folder_scanner = scanner_associations[sim_code]()
    species_list = folder_scanner.get_list_of_species(sim_path)

    found_species = False
    for species in sp_list:
        if species.species_name == species_name:
            beam = species
            found_species = True
    if not found_species:
        print('Species {} not found in specified path.'.format(species_name))
        return
    if t_step_range is not None:
        time_steps = beam.timesteps[
            np.where((bunch.timesteps >= t_step_range[0])
                     and (bunch.timesteps <= t_step_range[1]))]
    else:
        time_steps = beam.timesteps
    print('Done.')

    str_0 = 'Analyzing beam evolution... '
    for i, time_step in enumerate(time_steps):
        print_progress_bar(str_0, i, len(time_steps)-1)
        # read time step data
        data = beam.get_data(time_step, ['x', 'y', 'z', 'px', 'py', 'pz', 'q'])
        x, *_ = data['x']
        y, *_ = data['y']
        z, *_ = data['z']
        px, *_ = data['px']
        py, *_ = data['py']
        pz, *_ = data['pz']
        q, *_ = data['q']
        
        # analyze beam
        beam_params = bd.general_analysis(x, y, z, px, py, pz, q,
                                            len_slice=slice_len)
        if i == 0:
            params_array = np.array(beam_params)
        else:
            params_array = np.vstack((params_array, np.array(beam_params)))
    params_array = params_array.T
    print('Done.')

    # save to file
    if save_to is not None:
        print('Saving to file... ', end = '')
        file_path = os.path.join(save_to, saved_file_name)
        np.save(file_path, params_array)
        print('Done.')

    return params_array
