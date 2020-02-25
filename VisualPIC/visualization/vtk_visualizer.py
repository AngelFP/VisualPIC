"""This module contains the classes for 3D visualization with VTK"""

import os
import sys
from pkg_resources import resource_filename

import vtk
import numpy as np
from scipy.ndimage import zoom
from h5py import File as H5File
try:
    from PyQt5 import QtWidgets
    qt_installed = True
except:
    qt_installed = False

if qt_installed:
    from VisualPIC.visualization.basic_render_window import BasicRenderWindow


class VTKVisualizer():

    """Main class controlling the visualization"""

    def __init__(self, show_axes=True, show_logo=True, background='black',
                 use_qt=True):
        """
        Initialize the 3D visualizer.

        Parameters
        ----------

        show_axes : bool
            Determines whether to show a 3D axis in the render.

        show_axes : bool
            Determines whether to show the VisualPIC logo in the render.

        background : str or list
            Background color of the render. Possible values are 'black',
            'white' or a list of 3 floats with the RGB values.

        use_qt : bool
            Whether to use Qt for the windows opened by the visualizer.
        """
        if use_qt and not qt_installed:
            print('Qt is not installed. Default VTK windows will be used.')
            use_qt = False
        self.vis_config = {'render_quality': 'auto',
                           'background_color': background,
                           'show_logo': show_logo,
                           'show_axes': show_axes,
                           'use_qt': use_qt}
        self.volume_field_list = []
        self._initialize_base_vtk_elements()
        self._add_axes_widget()
        self._add_visualpic_logo()
        self.set_background(self.vis_config['background_color'])

    def add_field(self, field, cmap='viridis', opacity='auto',
                  vmax=None, vmin=None, xtrim=None, ytrim=None, ztrim=None,
                  resolution=None):
        """
        Add a field to the 3D visualization.

        Parameters
        ----------

        field : Field
            The field to be displayed.

        cmap : str
            Colormap to be used. Possible values are the same as those availabe
            in matplotlib.

        opacity : str or Opacity
            The opacity scheme to be used. Possible values are 'auto',
            'linear positive', 'linear negative', 'v shape', 'inverse v shape',
            'uniform' or any instace of Opacity.

        vmin, vmax : float
            Define the minimum and the maximum of the range of field values
            that the colormap and opacity cover.

        xtrim, ytrim, ztrim : list
            Allow to downselect the field volume to be displayed by trimming
            off the parts out of the range defined by these parameters. The
            provided value should be a list of two values containing the
            minimum and maximum of the spatial range to be displayes along the
            desired axis. These values should be between -1 and 1, which
            correspond to the minimum and the maximum of the original data. For
            example xtrim=[-1, 1] wont have any effect, as it preserves all
            data. On the contrary, xtrim=[-0.5, 0.5] would lead to only half of
            the field around the x axis.

        resolution : list
            This allows rendering the field with a different 3D resolution than
            that of the original data. A list of 3 integers shoud be provided
            contaning the resoltion along z (longitudinal), x and y (transv.).
            
        """
        if field.get_geometry() in ['thetaMode', '3dcartesian']:
            self.volume_field_list.append(VolumetricField(
                field, cmap, opacity, vmax, vmin, xtrim, ytrim, ztrim,
                resolution))
        else:
            fld_geom = field.get_geometry()
            raise ValueError(
                "Field geometry '{}' not supported.".format(fld_geom))

    def render_to_file(self, timestep, file_path, resolution=None):
        """
        Render the fields in the visualizer at a specific time step and save
        image to a file.

        Parameters
        ----------

        timestep : int
            Time step of the fiels to be rendered.

        file_path : str
            Path to the file to which the render should be saved.

        resolution : list
            List containing the horizontal and vertical resolution of the
            rendered image.
        """
        self.window.SetOffScreenRendering(1)
        if resolution is not None:
            self.window.SetSize(*resolution)
        self._load_data_into_volume(timestep)
        self.window.Render()
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(self.window)        
        w2if.Update()
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(file_path)
        writer.SetInputConnection(w2if.GetOutputPort())
        writer.Write()

    def show(self, timestep):
        """
        Render and show the fields in the visualizer at a specific time step.

        Parameters
        ----------

        timestep : int
            Time step of the fiels to be rendered.
        """
        self.window.SetOffScreenRendering(0)
        self._load_data_into_volume(timestep)
        if self.vis_config['use_qt']:
            app = QtWidgets.QApplication(sys.argv)
            window = BasicRenderWindow(self.window, self.interactor)
            app.exec_()
        else:
            self.window.Render()
            self.interactor.Start()

    def show_axes(self, value):
        """
        Show (for value=True) or hide (for value=False) the 3D axes in the
        render.
        """
        self.vis_config['show_axes'] = value
        self.vtk_orientation_marker.SetEnabled(value)

    def show_logo(self, value):
        """
        Show (for value=True) or hide (for value=False) the VisualPIC logo in
        the render.
        """
        self.vis_config['show_logo'] = value
        if value:
            self.vtk_logo_widget.On()
        else:
            self.vtk_logo_widget.Off()

    def set_background(self, color):
        """
        Set the background color of the 3D visualizer.

        Parameters
        ----------

        color : str or list
            Background color of the render. Possible values are 'black',
            'white' or a list of 3 floats with the RGB values.
        """
        if isinstance(color, str):
            if color == 'white':
                self.renderer.SetBackground(1, 1, 1)
            elif color == 'black':
                self.renderer.SetBackground(0, 0, 0)
        else:
            self.renderer.SetBackground(*color)

    def _initialize_base_vtk_elements(self):
        self.vtk_volume = vtk.vtkVolume()
        self.renderer = vtk.vtkRenderer()
        self.renderer.AddVolume(self.vtk_volume)
        self.window = vtk.vtkRenderWindow()
        self.window.SetSize(500, 500)
        self.window.AddRenderer(self.renderer)
        self.window.SetOffScreenRendering(1)
        if self.vis_config['use_qt']:
            self.interactor = vtk.vtkGenericRenderWindowInteractor()
        else:
            self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.window)
        self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

    def _add_axes_widget(self):
        self.vtk_axes = vtk.vtkAxesActor()
        self.vtk_axes.SetXAxisLabelText("Z")
        self.vtk_axes.SetZAxisLabelText("X")
        self.vtk_axes.GetZAxisShaftProperty().SetColor(0.129,0.467,0.694)
        self.vtk_axes.GetZAxisTipProperty().SetColor(0.129,0.467,0.694)
        self.vtk_axes.GetXAxisShaftProperty().SetColor(0.835,0.165,0.176)
        self.vtk_axes.GetXAxisTipProperty().SetColor(0.835,0.165,0.176)
        self.vtk_axes.GetYAxisShaftProperty().SetColor(0.188,0.627,0.224)
        self.vtk_axes.GetYAxisTipProperty().SetColor(0.188,0.627,0.224)
        self.vtk_orientation_marker = vtk.vtkOrientationMarkerWidget()
        self.vtk_orientation_marker.SetOutlineColor(1, 1, 1)
        self.vtk_orientation_marker.SetOrientationMarker(self.vtk_axes)
        self.vtk_orientation_marker.SetInteractor(self.interactor)
        self.vtk_orientation_marker.SetViewport(0, 0, 0.2, 0.2)
        self.show_axes(self.vis_config['show_axes'])
        self.vtk_orientation_marker.InteractiveOff()

    def _add_visualpic_logo(self):
        self.vtk_image_data = vtk.vtkImageData()
        self.logo_path = resource_filename(
                'VisualPIC.Icons', 'logo_horiz_transp.png')
        self.vtk_png_reader = vtk.vtkPNGReader()
        self.vtk_png_reader.SetFileName(self.logo_path)
        self.vtk_png_reader.Update()
        self.vtk_image_data = self.vtk_png_reader.GetOutput()
        self.vtk_logo_representation = vtk.vtkLogoRepresentation()
        self.vtk_logo_representation.SetImage(self.vtk_image_data)
        self.vtk_logo_representation.SetPosition(0.79, 0.01)
        self.vtk_logo_representation.SetPosition2(.2, .1)
        self.vtk_logo_representation.GetImageProperty().SetOpacity(1)
        self.vtk_logo_widget = vtk.vtkLogoWidget()
        self.vtk_logo_widget.SetInteractor(self.interactor)
        self.vtk_logo_widget.SetRepresentation(self.vtk_logo_representation)
        self.vtk_logo_widget.GetBorderRepresentation().SetShowBorderToOff()
        self.show_logo(self.vis_config['show_logo'])

    def _load_data_into_volume(self, timestep):
        vtk_volume_prop = self._get_volume_properties(timestep)
        vtk_data_import = self._import_data(timestep)
        # Create the mapper
        vtk_volume_mapper = vtk.vtkGPUVolumeRayCastMapper()
        vtk_volume_mapper.SetInputConnection(vtk_data_import.GetOutputPort())
        vtk_volume_mapper.Update()
        # Add to volume
        self.vtk_volume.SetMapper(vtk_volume_mapper)
        self.vtk_volume.SetProperty(vtk_volume_prop)
        self.renderer.ResetCamera()
    
    def _get_volume_properties(self, timestep):
        vtk_volume_prop = vtk.vtkVolumeProperty()
        vtk_volume_prop.IndependentComponentsOn()
        vtk_volume_prop.SetInterpolationTypeToLinear()
        for i, vol_field in enumerate(self.volume_field_list):
            vtk_volume_prop.SetColor(i, vol_field.get_vtk_colormap())
            vtk_volume_prop.SetScalarOpacity(
                i, vol_field.get_vtk_opacity(timestep))
            vtk_volume_prop.ShadeOff(i)
        return vtk_volume_prop

    def _import_data(self, timestep):
        # Get data
        npdatauchar = list()
        for i, vol_field in enumerate(self.volume_field_list):
            npdatauchar.append(vol_field.get_data(timestep))
        self.npdatamulti = np.concatenate(
            [aux[...,np.newaxis] for aux in npdatauchar], axis=3)
        ax_orig, ax_spacing = self.volume_field_list[0].get_axes_data(timestep)
        max_spacing = max(ax_spacing)
        max_cell_size = 0.1
        norm_factor = max_cell_size/max_spacing
        ax_orig *= norm_factor
        ax_spacing *= norm_factor

        # Put data in VTK format
        vtk_data_import = vtk.vtkImageImport()
        vtk_data_import.SetImportVoidPointer(self.npdatamulti)
        vtk_data_import.SetDataScalarTypeToUnsignedChar()
        vtk_data_import.SetNumberOfScalarComponents(
            len(self.volume_field_list))
        vtk_data_import.SetDataExtent(0, self.npdatamulti.shape[2]-1,
                                      0, self.npdatamulti.shape[1]-1,
                                      0, self.npdatamulti.shape[0]-1)
        vtk_data_import.SetWholeExtent(0, self.npdatamulti.shape[2]-1,
                                       0, self.npdatamulti.shape[1]-1,
                                       0, self.npdatamulti.shape[0]-1)
        vtk_data_import.SetDataSpacing(ax_spacing[0],
                                       ax_spacing[1],
                                       ax_spacing[2])
        # data origin is also changed by the normalization
        vtk_data_import.SetDataOrigin(ax_orig[0], ax_orig[1], ax_orig[2])
        vtk_data_import.Update()
        return vtk_data_import


class VolumetricField():

    """Class for the volumetric fields to be displayed."""

    def __init__(self, field, cmap='viridis', opacity='auto', vmax=None,
                 vmin=None, xtrim=None, ytrim=None, ztrim=None,
                 resolution=None):
        self.field = field
        self.style_handler = VolumeStyleHandler()
        self.cmap = cmap
        self.opacity = opacity
        self.vmax = vmax
        self.vmin = vmin
        self.xtrim = xtrim # [-1, 1]
        self.ytrim = ytrim
        self.ztrim = ztrim
        self.resolution = resolution

    def get_name(self):
        return field.field_name

    def get_data(self, timestep):
        fld_data, *_ = self.field.get_data(timestep, theta=None)
        fld_data = self._trim_field(fld_data)
        fld_data = self._change_resolution(fld_data)
        fld_data = self._normalize_field(fld_data)
        return fld_data

    def get_axes_data(self, timestep):
        fld_md = self.field.get_only_metadata(timestep, theta=None)
        z = fld_md['axis']['z']['array']
        x = fld_md['axis']['x']['array']
        y = fld_md['axis']['y']['array']
        x, y, z = self._trim_axes(x, y, z)
        x, y, z = self._change_resolution_axes(x, y, z)
        ax_orig = np.array([z[0], x[0], y[0]])
        ax_spacing = np.array([z[1] - z[0], x[1] - x[0], y[1] - y[0]])
        return ax_orig, ax_spacing

    def get_vtk_opacity(self, timestep=None):
        vtk_opacity = vtk.vtkPiecewiseFunction()
        if isinstance(self.opacity, Opacity):
            opacity = self.opacity
        elif self.opacity != 'auto':
            if self.style_handler.opacity_exists(self.opacity):
                opacity = self.style_handler.get_opacity(self.opacity)
            else:
                raise ValueError(
                    "Opacity '{}' does not exist.".format(self.opacity))
        else:
            opacity = self.get_optimized_opacity(timestep)
        fld_vals, op_vals = opacity.get_opacity_values()
        for fv, ov in zip(fld_vals, op_vals):
            vtk_opacity.AddPoint(fv, ov)
        return vtk_opacity

    def get_vtk_colormap(self):
        vtk_cmap = vtk.vtkColorTransferFunction()
        if isinstance(self.cmap, Colormap):
            cmap = self.cmap
        else:
            if self.style_handler.cmap_exists(self.cmap):
                cmap = self.style_handler.get_cmap(self.cmap)
            else:
                raise ValueError(
                    "Colormap '{}' does not exist.".format(self.cmap))
        fld_val, r_val, g_val, b_val = cmap.get_cmap_values()
        # points = [x0, r0, g0, b0, x1, r1, g1, b1, ..., xN, rN, gN, bN]
        points = list(np.column_stack((fld_val, r_val, g_val, b_val)).flat)
        vtk_cmap.FillFromDataPointer(int(len(points)/4), points)
        return vtk_cmap

    def get_optimized_opacity(self, time_step):
        nel = 11
        fld_data = self.get_data(time_step)
        hist, hist_edges = np.histogram(fld_data, bins=nel)
        hist = np.ma.log(hist).filled(0)
        fld_val = np.linspace(0, 255, nel)
        op_val = 1 - hist/hist.max()
        opacity = Opacity(name='auto', fld_values=fld_val, op_values=op_val)
        return opacity

    def _trim_field(self, fld_data):
        shape = fld_data.shape
        if self.xtrim is not None:
            xmin = int(np.round(shape[0]/2 * (self.xtrim[0] + 1)))
            xmax = int(np.round(shape[0]/2 * (self.xtrim[1] + 1)))
            fld_data = fld_data[xmin:xmax]
        if self.ytrim is not None:
            ymin = int(np.round(shape[1]/2 * (self.ytrim[0] + 1)))
            ymax = int(np.round(shape[1]/2 * (self.ytrim[1] + 1)))
            fld_data = fld_data[:, ymin:ymax]
        if self.ztrim is not None:
            zmin = int(np.round(shape[1]/2 * (self.ztrim[0] + 1)))
            zmax = int(np.round(shape[1]/2 * (self.ztrim[1] + 1)))
            fld_data = fld_data[:, :, zmin:zmax]
        return fld_data

    def _trim_axes(self, x, y, z):
        if self.xtrim is not None:
            ax_len = len(x)
            xmin = int(np.round(ax_len/2 * (self.xtrim[0] + 1)))
            xmax = int(np.round(ax_len/2 * (self.xtrim[1] + 1)))
            x = x[xmin:xmax]
        if self.ytrim is not None:
            ax_len = len(y)
            ymin = int(np.round(ax_len/2 * (self.ytrim[0] + 1)))
            ymax = int(np.round(ax_len/2 * (self.ytrim[1] + 1)))
            y = y[ymin:ymax]
        if self.ztrim is not None:
            ax_len = len(z)
            zmin = int(np.round(ax_len/2 * (self.ztrim[0] + 1)))
            zmax = int(np.round(ax_len/2 * (self.ztrim[1] + 1)))
            z = z[zmin:zmax]
        return x, y, z

    def _normalize_field(self, fld_data):
        if self.vmax is None:
            max_value = np.max(fld_data)
        else:
            max_value = self.vmax
        if self.vmin is None:
            min_value = np.min(fld_data)
        else:
            min_value = self.vmin
        fld_data -= min_value
        fld_data *= 255 / (max_value-min_value)
        # norm_data = 255 * (fld_data-min_value)/(max_value-min_value)
        fld_data[fld_data < 0] = 0
        fld_data[fld_data > 255] = 255
        # Change data from float to unsigned char
        fld_data = np.array(fld_data, dtype=np.uint8)
        return fld_data

    def _change_resolution(self, fld_data):
        if self.resolution is not None:
            shape = np.array(fld_data.shape)
            fld_zoom = np.array(self.resolution) / shape
            fld_data = zoom(fld_data, fld_zoom, order=0)
        return fld_data

    def _change_resolution_axes(self, x, y, z):
        if self.resolution is not None:
            x_zoom = self.resolution[0] / len(x)
            y_zoom = self.resolution[1] / len(y)
            z_zoom = self.resolution[2] / len(z)
            x = zoom(x, x_zoom)
            y = zoom(y, y_zoom)
            z = zoom(z, z_zoom)
        return x, y, z


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
                'VisualPIC.Assets.Visualizer3D.Opacities', '')
            self.cmaps_folder_path = resource_filename(
                'VisualPIC.Assets.Visualizer3D.Colormaps', '')
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

        def get_opacity_data(self, op_name):
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

        def get_cmap_data(self, cmap_name):
            for cmap in self.default_cmaps + self.other_cmaps:
                if cmap.get_name() == cmap_name:
                    return cmap.get_cmap()

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
