
import os

import numpy as np

import VisualPIC.DataReading.field_readers as fr
from VisualPIC.DataHandling.fields import FolderField
import VisualPIC.DataHandling.unitConverters as uc

class FolderScanner():
    def get_list_of_fields(self, folder_path):
        pass


class OsirisFolderScanner(FolderScanner):
    def __init__(self):
        self.field_reader = fr.OsirisFieldReader()
        #self.unit_converter = uc.OsirisUnitConverter()

    def get_list_of_fields(self, folder_path):
        field_list = []
        folders_in_path = os.listdir(folder_path)
        for folder in folders_in_path:
            if folder == "DENSITY":
                pass
            if folder == "FLD":
                subdir = os.path.join(folder_path, folder)
                domain_fields = os.listdir(subdir)
                for field in domain_fields:
                    field_folder = os.path.join(subdir, field)
                    if os.path.isdir(field_folder):
                        field_path = self._get_field_path(field)
                        osiris_field_name = self._get_osiris_field_name(
                            field)
                        field_name = self._get_standard_visualpic_name(
                            osiris_field_name)
                        fld_files, time_steps = self._get_files_and_timesteps(
                            field_folder)
                        field_list.append(
                            FolderField(field_name, field_path, fld_files,
                                        time_steps, self.field_reader,
                                        'uc'))
        return field_list

    def _get_field_path(self, field_folder_name):
        return '/' + self._get_osiris_field_name(field_folder_name)

    def _get_standard_visualpic_name(self, osiris_name):
        name_relations = {'e1': 'Ez',
                          'e2': 'Ex',
                          'e3': 'Ey',
                          'b1': 'Bz',
                          'b2': 'Bx',
                          'b3': 'By',
                          'charge': 'rho'}
        if osiris_name in name_relations:
            return name_relations[osiris_name]
        else:
            raise ValueError('Unknown data name {}.'.format(osiris_name))

    def _get_osiris_field_name(self, field_folder_name):
        return field_folder_name.replace('-savg', '')

    def _get_files_and_timesteps(self, field_folder_path):
        all_files = os.listdir(field_folder_path)
        h5_files = list()
        for file in all_files:
            if file.endswith(".h5"):
                h5_files.append(os.path.join(field_folder_path, file))
        time_steps = np.zeros(len(h5_files))
        for i, file in enumerate(h5_files):
            time_step = int(file[-9:-3])
            time_steps[i] = time_step
        sort_i = np.argsort(time_steps)
        time_steps = time_steps[sort_i]
        h5_files = np.array(h5_files)[sort_i]
        return h5_files, time_steps