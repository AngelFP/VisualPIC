import os
from pkg_resources import resource_filename

import numpy as np
from h5py import File as H5File


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
                'VisualPIC.visualization.assets.vtk_visualizer.opacities', '')
            self.cmaps_folder_path = resource_filename(
                'VisualPIC.visualization.assets.vtk_visualizer.colormaps', '')
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
            if (field_values.min() >= 0 and field_values.max() <= 255
                and opacity_values.min() >= 0 and opacity_values.max() <= 1
                and len(field_values) == len(opacity_values)
                and len(opacity_values) <= self.max_len):
                file_path = self.create_file_path(name, folder_path)
                # Create H5 file
                file = H5File(file_path,  "w")
                opacity_dataset = file.create_dataset(
                    "opacity", data = opacity_values)
                field_dataset = file.create_dataset("field",
                                                    data = field_values)
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
            return False

        def get_cmap(self, cmap_name):
            for cmap in self.default_cmaps + self.other_cmaps:
                if cmap.get_name() == cmap_name:
                    return cmap

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
                r_dataset = file.create_dataset("r", data=r_val)
                g_dataset = file.create_dataset("g", data=g_val)
                b_dataset = file.create_dataset("b", data=b_val)
                fld_dataset = file.create_dataset("field", data=fld_val)
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

