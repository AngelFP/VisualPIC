from h5py import File as H5F
import numpy as np

class FieldReader():
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def read_field(self, file_path, field_path, slice_i=None, slice_j=None,
                   slice_dir_i='z', slice_dir_j='x', m=0, theta=0):
        fld_metadata = self.read_field_metadata(file_path, field_path)
        geom = fld_metadata['field']['geometry']
        if geom == "1D":
            fld = self.read_field_1d(file_path, field_path)
        elif geom == "2D-cart":
            fld = self.read_field_2d_cart(file_path, field_path, slice_i,
                                          slice_dir_i)
        elif geom == "3D-cart":
            fld = self.read_field_3d_cart(file_path, field_path, slice_i,
                                          slice_j, slice_dir_i, slice_dir_j)
        elif geom == "2D-cyl":
            fld = self.read_field_2d_cyl(file_path, field_path, slice_i,
                                         slice_dir_i)
        elif geom == "thetaMode":
            fld = self.read_field_theta(file_path, field_path, m, theta)
        return fld, fld_metadata

    def read_field_1d(self, file_path, field_path):
        raise NotImplementedError

    def read_field_2d_cart(self, file_path, field_path, slice_i=None,
                           slice_dir_i='z'):
        raise NotImplementedError

    def read_field_3d_cart(self, file_path, field_path, slice_i=None,
                           slice_j=None, slice_dir_i='z', slice_dir_j='x'):
        raise NotImplementedError

    def read_field_2d_cyl(self, file_path, field_path, slice_i=None,
                          slice_dir_i='z'):
        raise NotImplementedError

    def read_field_theta(self, file_path, field_path, m=0, theta=0):
        raise NotImplementedError

    def read_field_metadata(self, file_path, field_path):
        raise NotImplementedError


class OsirisFieldReader(FieldReader):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def read_field_1d(self, file_path, field_path):
        file = H5F(file_path, 'r')
        return file[field_path]
    
    def read_field_2d_cart(self, file_path, field_path, slice_i=None,
                           slice_dir_i='z'):
        file = H5F(file_path, 'r')
        fld = file[field_path]
        if slice_i is not None:
            fld_shape = fld.shape
            axis_order = ['x', 'z']
            slice_list = [slice(None)] * fld.ndim
            axis_idx_i = axis_order.index(slice_dir_i)
            axis_elements_i = fld_shape[axis_idx_i] 
            slice_idx_i = int(round(axis_elements_i * slice_i))
            slice_list[axis_idx_i] = slice_idx_i
            fld = fld[tuple(slice_list)]
        return fld

    def read_field_3d_cart(self, file_path, field_path, slice_i=None,
                           slice_j=None, slice_dir_i='z', slice_dir_j='x'):
        file = H5F(file_path, 'r')
        fld = file[field_path]
        if slice_i is not None:
            fld_shape = fld.shape
            axis_order = ['x', 'y', 'z']
            slice_list = [slice(None)] * fld.ndim
            axis_idx_i = axis_order.index(slice_dir_i)
            axis_elements_i = fld_shape[axis_idx_i] 
            slice_idx_i = int(round(axis_elements_i * slice_i))
            slice_list[axis_idx_i] = slice_idx_i
            if slice_j is not None:
                axis_idx_j = axis_order.index(slice_dir_j)
                axis_elements_j = fld_shape[axis_idx_j] 
                slice_idx_j = int(round(axis_elements_j * slice_j))
                slice_list[axis_idx_j] = slice_idx_j
            fld = fld[tuple(slice_list)]
        return fld

    def read_field_metadata(self, file_path, field_path):
        file = H5F(file_path, 'r')
        md = {}
        field_units = self.get_field_units(file, field_path)
        field_shape = self.get_field_shape(file, field_path)
        field_geometry = self.determine_geometry(file)
        md['field'] = {}
        md['field']['units'] = field_units
        md['field']['geometry'] = field_geometry
        md['axis'] = self.get_axis_data(file, field_path, field_geometry,
                                       field_shape)
        md['time'] = self.get_time_data(file)
        file.close()
        return md
        
    def get_field_units(self, file, field_path):
        """ Returns the field units"""
        return str(list(file[field_path].attrs["UNITS"])[0])[2:-1].replace(
            "\\\\","\\")

    def get_field_shape(self, file, field_path):
        """ Returns shape of field array"""
        return file[field_path].shape

    def determine_geometry(self, file):
        """ Determines the field geometry """
        if '/AXIS/AXIS3' in file:
            return "3D-cart"
        elif '/AXIS/AXIS2' in file:
            return "2D-cart"
        else:
            return "1D"

    def get_axis_data(self, file, field_path, field_geometry, field_shape):
        """ Returns dictionary with the array and units of each field axis """
        axis_data = {}
        axis_data['z'] = {}
        axis_data["z"]["units"] = str(list(file['/AXIS/AXIS1'].attrs[
            "UNITS"])[0])[2:-1].replace("\\\\","\\")
        axis_data["z"]["array"] = np.linspace(file.attrs['XMIN'][0],
                                              file.attrs['XMAX'][0],
                                              field_shape[0])
        if field_geometry in ["2D-cart", "3D-cart"]:
            axis_data['x'] = {}
            axis_data["x"]["units"] = str(list(file['/AXIS/AXIS2'].attrs[
                "UNITS"])[0])[2:-1].replace("\\\\","\\")
            axis_data["x"]["array"] = np.linspace(file.attrs['XMIN'][1],
                                                  file.attrs['XMAX'][1],
                                                  field_shape[1])
        if field_geometry == "3D-cart":
            axis_data['y'] = {}
            axis_data["y"]["units"] = str(list(file['/AXIS/AXIS3'].attrs[
                "UNITS"])[0])[2:-1].replace("\\\\","\\")
            axis_data["y"]["array"] = np.linspace(file.attrs['XMIN'][2],
                                                  file.attrs['XMAX'][2],
                                                  field_shape[2])
        return axis_data

    def get_time_data(self, file):
        """ Returns dictionary with value and units of the simulation time """
        time_data = {}
        time_data["value"] = file.attrs["TIME"][0]
        time_data["units"] = str(file.attrs["TIME UNITS"][0])[2:-1].replace(
            "\\\\","\\")
        return time_data
