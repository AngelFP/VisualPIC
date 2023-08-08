"""
This file is part of VisualPIC.

The module contains the classes related to the visual appearance of volumetric
fields.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""


import os
from pkg_resources import resource_filename

import numpy as np
from h5py import File as H5File
import matplotlib.colors as mcolors


class VolumeStyleHandler():

    """Defines a style handler as singleton."""

    vsh = None

    def __init__(self):
        if VolumeStyleHandler.vsh is None:
            VolumeStyleHandler.vsh = VolumeStyleHandler.__VolumeStyleHandler()

    def __getattr__(self, name):
        return getattr(self.vsh, name)

    class __VolumeStyleHandler():
        def __init__(self):
            self.max_len = 50
            self.opacity_folder_path = resource_filename(
                'visualpic.visualization.assets.vtk_visualizer.opacities', '')
            self.cmaps_folder_path = resource_filename(
                'visualpic.visualization.assets.vtk_visualizer.colormaps', '')
            self.initialize_available_opacities()
            self.initialize_available_cmaps()

        """Opacities"""

        def initialize_available_opacities(self):
            self.default_opacities = list()
            self.other_opacities = list()
            folder_opacities = self.get_opacities_in_default_folder()
            if len(folder_opacities) > 0:
                self.default_opacities += (
                    self.get_opacities_in_default_folder())
            else:
                self.default_opacities.append(self.create_fallback_opacity())

        def get_opacities_in_default_folder(self):
            files_in_folder = os.listdir(self.opacity_folder_path)
            folder_opacities = list()
            for file in files_in_folder:
                if file.endswith('.h5'):
                    file_path = self.create_file_path(file,
                                                      self.opacity_folder_path)
                    folder_opacities.append(Opacity(file_path))
            return folder_opacities

        def create_fallback_opacity(self):
            n_points = 11
            name = "linear positive"
            fld_vals = np.linspace(0, 255, n_points)
            op_vals = np.linspace(0, 0.999, n_points)
            op = Opacity(name=name, fld_values=fld_vals, op_values=op_vals)
            return op

        def get_available_opacities(self):
            ops = list()
            for op in self.default_opacities + self.other_opacities:
                ops.append(op.get_name())
            return ops

        def opacity_exists(self, op_name):
            for op in self.default_opacities + self.other_opacities:
                if op.get_name() == op_name:
                    return True
            return False

        def get_opacity(self, op_name):
            for op in self.default_opacities + self.other_opacities:
                if op.get_name() == op_name:
                    return op

        def get_opacity_values(self, op_name):
            for op in self.default_opacities + self.other_opacities:
                if op.get_name() == op_name:
                    return op.get_opacity_values()

        def save_opacity(self, name, field_values, opacity_values,
                         folder_path):
            # Make sure opacity is within bounds.
            opacity_values[opacity_values < 0.] = 0.
            opacity_values[opacity_values > 1] = 1.
            if (field_values.min() >= 0 and field_values.max() <= 255
                and len(field_values) == len(opacity_values)
                    and len(opacity_values) <= self.max_len):
                file_path = self.create_file_path(name, folder_path)
                # Create H5 file
                file = H5File(file_path,  "w")
                file.create_dataset("opacity", data=opacity_values)
                file.create_dataset("field", data=field_values)
                file.attrs["opacity_name"] = name
                file.close()
                # Add to available opacities
                opacity = Opacity(file_path)
                if (os.path.normpath(folder_path)
                        == self.opacity_folder_path):
                    self.default_opacities.append(opacity)
                else:
                    self.other_opacities.append(opacity)
                return True
            else:
                return False

        def add_opacity_from_file(self, file_path):
            self.other_opacities.append(Opacity(file_path))

        """Colormaps"""

        def initialize_available_cmaps(self):
            self.default_cmaps = list()
            self.other_cmaps = list()
            folder_cmaps = self.get_cmaps_in_default_folder()
            if len(folder_cmaps) > 0:
                self.default_cmaps += (
                    self.get_cmaps_in_default_folder())
            else:
                self.default_cmaps.append(self.create_fallback_cmap())
            self.mpl_colors = self.get_mpl_colors()

        def get_mpl_colors(self, only_basic=False):
            if only_basic:
                return list(mcolors.BASE_COLORS) + list(mcolors.TABLEAU_COLORS)
            else:
                return list(mcolors.get_named_colors_mapping())

        def get_cmaps_in_default_folder(self):
            files_in_folder = os.listdir(self.cmaps_folder_path)
            folder_cmaps = list()
            for file in files_in_folder:
                if file.endswith('.h5'):
                    file_path = self.create_file_path(file,
                                                      self.cmaps_folder_path)
                    folder_cmaps.append(Colormap(file_path))
            return folder_cmaps

        def create_fallback_cmap(self):
            n_points = 11
            cmap = Colormap("")
            cmap.name = "default"
            cmap.fld_data = np.linspace(0, 255, n_points)
            r_1 = np.linspace(0, 1, (n_points+1) / 2)
            r_2 = np.linspace(1, 0, (n_points+1) / 2)
            cmap.r_data = np.append(np.delete(r_1, -1), r_2)
            cmap.g_data = np.linspace(0, 1, n_points)
            cmap.b_data = np.linspace(1, 0, n_points)
            return cmap

        def get_available_cmaps(self):
            cmaps = list()
            for cmap in self.default_cmaps + self.other_cmaps:
                cmaps.append(cmap.get_name())
            return cmaps

        def cmap_exists(self, cmap_name):
            for cmap in self.default_cmaps + self.other_cmaps:
                if cmap.get_name() == cmap_name:
                    return True
                if cmap_name in self.mpl_colors:
                    return True
            return False

        def get_cmap(self, cmap_name):
            for cmap in self.default_cmaps + self.other_cmaps:
                if cmap.get_name() == cmap_name:
                    return cmap
            if cmap_name in self.mpl_colors:
                return self._create_cmap_from_mpl_color(cmap_name)

        def get_cmap_values(self, cmap_name):
            for cmap in self.default_cmaps + self.other_cmaps:
                if cmap.get_name() == cmap_name:
                    return cmap.get_cmap_values()

        def save_cmap(self, name, fld_val, r_val, g_val, b_val, folder_path):
            if (fld_val.min() >= 0 and fld_val.max() <= 255
                and r_val.min() >= 0 and r_val.max() <= 255
                and g_val.min() >= 0 and g_val.max() <= 255
                and b_val.min() >= 0 and b_val.max() <= 255
                and len(fld_val) == len(r_val) == len(g_val) == len(b_val)
                    and len(fld_val) <= self.max_len):
                file_path = self.create_file_path(name, folder_path)
                # Create H5 file
                file = H5File(file_path,  "w")
                file.create_dataset("r", data=r_val)
                file.create_dataset("g", data=g_val)
                file.create_dataset("b", data=b_val)
                file.create_dataset("field", data=fld_val)
                file.attrs["cmap_name"] = name
                file.close()
                # Add to available colormaps
                cmap = Colormap(file_path)
                if (os.path.normpath(folder_path) == self.cmaps_folder_path):
                    self.default_cmaps.append(cmap)
                else:
                    self.other_cmaps.append(cmap)
                return True
            else:
                return False

        def add_cmap_from_file(self, file_path):
            self.other_cmaps.append(Colormap(file_path))

        def get_mpl_color_rgb(self, mpl_color):
            r, g, b = mcolors.to_rgb(mpl_color)
            return r, g, b

        def _create_cmap_from_mpl_color(self, mpl_color):
            r, g, b = self.get_mpl_color_rgb(mpl_color)
            base_arr = np.ones(11)
            r_vals = r * base_arr
            g_vals = g * base_arr
            b_vals = b * base_arr
            fld_vals = np.linspace(0, 255, 11)
            return Colormap(name=mpl_color, r_values=r_vals, g_values=g_vals,
                            b_values=b_vals, fld_values=fld_vals)

        """Common"""

        def create_file_path(self, file_name, folder_path):
            if not file_name.endswith('.h5'):
                file_name += ".h5"
                file_name = file_name.replace(' ', '_').lower()
            file_path = os.path.join(folder_path, file_name)
            return file_path


class Opacity():

    """Class defining an opacity map fr 3D fields."""

    def __init__(self, file_path=None, name=None, op_values=None,
                 fld_values=None):
        if file_path is not None:
            file = H5File(file_path, "r")
            self.name = file.attrs["opacity_name"]
            self.op_values = np.array(file["/opacity"])
            self.fld_values = np.array(file["/field"])
        else:
            self.name = name
            self.op_values = op_values
            self.fld_values = fld_values

    def get_name(self):
        return self.name

    def get_opacity_values(self):
        return self.fld_values, self.op_values


class Colormap():

    """Class defining a colormap for 3D fields."""

    def __init__(self, file_path=None, name=None, r_values=None, g_values=None,
                 b_values=None, fld_values=None):
        if file_path is not None:
            file = H5File(file_path, "r")
            self.name = file.attrs["cmap_name"]
            self.r_values = np.array(file["/r"])
            self.g_values = np.array(file["/g"])
            self.b_values = np.array(file["/b"])
            self.fld_values = np.array(file["/field"])
        else:
            self.name = name
            self.r_values = r_values
            self.g_values = g_values
            self.b_values = b_values
            self.fld_values = fld_values

    def get_name(self):
        return self.name

    def get_cmap_values(self):
        return self.fld_values, self.r_values, self.g_values, self.b_values
