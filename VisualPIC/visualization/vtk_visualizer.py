"""This module contains the classes for 3D visualization with VTK"""

import sys
from pkg_resources import resource_filename

import vtk
import numpy as np
from scipy.ndimage import zoom
try:
    from PyQt5 import QtWidgets
    qt_installed = True
except:
    qt_installed = False

from VisualPIC.helper_functions import get_common_timesteps
from VisualPIC.visualization.volume_appearance import *
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
        self.camera_props = {'zoom': 1}
        self.volume_field_list = []
        self.current_time_step = -1
        self.available_time_steps = None
        self._initialize_base_vtk_elements()
        self._add_axes_widget()
        self._add_visualpic_logo()
        self.set_background(self.vis_config['background_color'])

    def add_field(self, field, cmap='viridis', opacity='auto',
                  vmax=None, vmin=None, xtrim=None, ytrim=None, ztrim=None,
                  resolution=None, max_resolution_3d_tm=[100, 100]):
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

        max_resolution_3d_tm : list
            Maximum longitudinal and transverse resolution (eg. [1000, 500])
            that the 3d field generated from thetaMode data should have. This
            allows for faster reconstruction of the 3d field and less memory
            usage.
        """
        if field.get_geometry() in ['thetaMode', '3dcartesian']:
            self.volume_field_list.append(VolumetricField(
                field, cmap, opacity, vmax, vmin, xtrim, ytrim, ztrim,
                resolution, max_resolution_3d_tm))
            self.available_time_steps = self.get_possible_timesteps()
        else:
            fld_geom = field.get_geometry()
            raise ValueError(
                "Field geometry '{}' not supported.".format(fld_geom))

    def render_to_file(self, timestep, file_path, resolution=None,
                       ts_is_index=True):
        """
        Render the fields in the visualizer at a specific time step and save
        image to a file.

        Parameters
        ----------

        timestep : int
            Time step of the fiels to be rendered. Can be the index of a
            time step in self.available_time_steps or directly the numerical
            value of a time step. This is indicated by the 'ts_is_insex'
            parameter.

        file_path : str
            Path to the file to which the render should be saved.

        resolution : list
            List containing the horizontal and vertical resolution of the
            rendered image.

        ts_is_index : Bools
            Indicates whether the value provided in 'timestep' is the index of
            the time step (True) or the numerical value of the time step
            (False).
        """
        if ts_is_index:
            self.current_time_step = self.available_time_steps[timestep]
        else:
            if timestep not in self.available_time_steps:
                raise ValueError(
                    'Time step {} is not available.'.format(timestep))
            self.current_time_step = timestep
        self.window.SetOffScreenRendering(1)
        if resolution is not None:
            self.window.SetSize(*resolution)
        if self.old_vtk:
            self._load_data_into_volume(self.current_time_step)
        else:
            self._load_data_into_multi_volume(self.current_time_step)
        self._setup_camera()
        self.window.Render()
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(self.window)        
        w2if.Update()
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(file_path)
        writer.SetInputConnection(w2if.GetOutputPort())
        writer.Write()

    def show(self, timestep=0, ts_is_index=True):
        """
        Render and show the fields in the visualizer at a specific time step.

        Parameters
        ----------

        timestep : int
            Time step of the fiels to be rendered. Can be the index of a
            time step in self.available_time_steps or directly the numerical
            value of a time step. This is indicated by the 'ts_is_insex'
            parameter.

        ts_is_index : Bools
            Indicates whether the value provided in 'timestep' is the index of
            the time step (True) or the numerical value of the time step
            (False).
        """
        if ts_is_index:
            self.current_time_step = self.available_time_steps[timestep]
        else:
            if timestep not in self.available_time_steps:
                raise ValueError(
                    'Time step {} is not available.'.format(timestep))
            self.current_time_step = timestep
        self.window.SetOffScreenRendering(0)
        if self.old_vtk:
            self._load_data_into_volume(self.current_time_step)
        else:
            self._load_data_into_multi_volume(self.current_time_step)
        self._setup_camera()
        if self.vis_config['use_qt']:
            app = QtWidgets.QApplication(sys.argv)
            window = BasicRenderWindow(self)
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

    def get_list_of_fields(self):
        """Returns a list with the names of all available fields."""
        fld_list = []
        for vol_field in self.volume_field_list:
            fld_list.append(vol_field.get_name())
        return fld_list

    def set_camera_angles(self, azimuth, elevation):
        self.camera.Azimuth(azimuth)
        self.camera.Elevation(elevation)

    def set_camera_zoom(self, zoom):
        self.camera_props['zoom'] = zoom
        self.camera.Zoom(zoom)

    def get_possible_timesteps(self):
        """
        Returns a numpy array with all the time steps commonly available
        to all fields in the visualizer.
        """
        fld_list = []
        for volume in self.volume_field_list:
            fld_list.append(volume.field)
        return get_common_timesteps(fld_list)

    def _setup_camera(self):
        self.renderer.ResetCamera()
        self.camera.Zoom(self.camera_props['zoom'])

    def _initialize_base_vtk_elements(self):
        try:
            # vtkMultiVolume class available only in vtk >= 8.2.0
            self.vtk_volume = vtk.vtkMultiVolume()
            self.old_vtk = False
        except:
            self.vtk_volume = vtk.vtkVolume()
            self.old_vtk = True
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
        self.camera = self.renderer.GetActiveCamera()

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

    def _load_data_into_multi_volume(self, timestep):
        vtk_vols, imports = self._create_volumes(timestep)
        # Create the mapper
        vtk_volume_mapper = vtk.vtkGPUVolumeRayCastMapper()
        vtk_volume_mapper.UseJitteringOn()
        self.vtk_volume.SetMapper(vtk_volume_mapper)
        for i, (vol, imp) in enumerate(zip(vtk_vols, imports)):
            vtk_volume_mapper.SetInputConnection(i, imp.GetOutputPort())
            self.vtk_volume.SetVolume(vol, i)
        self.renderer.ResetCamera()

    def _create_volumes(self, timestep):
        self.npdatamulti = list()
        vol_list = list()
        imports_list = list()
        for i, vol_field in enumerate(self.volume_field_list):
            vtk_vol = vtk.vtkVolume()
            vtk_volume_prop = vtk.vtkVolumeProperty()
            vtk_volume_prop.SetInterpolationTypeToLinear()
            vtk_volume_prop.SetColor(vol_field.get_vtk_colormap())
            vtk_volume_prop.SetScalarOpacity(vol_field.get_vtk_opacity(timestep))
            vtk_volume_prop.ShadeOff()
            vtk_vol.SetProperty(vtk_volume_prop)
            self.npdatamulti.append(vol_field.get_data(timestep))
            vol_list.append(vtk_vol)

            ax_orig, ax_spacing = vol_field.get_axes_data(timestep)
            max_spacing = max(ax_spacing)
            max_cell_size = 0.1
            norm_factor = max_cell_size/max_spacing
            ax_orig *= norm_factor
            ax_spacing *= norm_factor

            # Put data in VTK format
            vtk_data_import = vtk.vtkImageImport()
            vtk_data_import.SetImportVoidPointer(self.npdatamulti[i])
            vtk_data_import.SetDataScalarTypeToUnsignedChar()
            vtk_data_import.SetDataExtent(0, self.npdatamulti[i].shape[2]-1,
                                          0, self.npdatamulti[i].shape[1]-1,
                                          0, self.npdatamulti[i].shape[0]-1)
            vtk_data_import.SetWholeExtent(0, self.npdatamulti[i].shape[2]-1,
                                           0, self.npdatamulti[i].shape[1]-1,
                                           0, self.npdatamulti[i].shape[0]-1)
            vtk_data_import.SetDataSpacing(ax_spacing[0],
                                           ax_spacing[1],
                                           ax_spacing[2])
            # data origin is also changed by the normalization
            vtk_data_import.SetDataOrigin(ax_orig[0], ax_orig[1], ax_orig[2])
            vtk_data_import.Update()
            imports_list.append(vtk_data_import)
        return vol_list, imports_list

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
                 resolution=None, max_resolution_3d_tm=None):
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
        self.max_resolution_3d_tm = max_resolution_3d_tm
        self.vtk_opacity = vtk.vtkPiecewiseFunction()
        self.vtk_cmap = vtk.vtkColorTransferFunction()

    def get_name(self):
        fld_name = self.field.field_name
        fld_sp = self.field.species_name
        if fld_sp is not None:
            fld_name += ' [{}]'.format(fld_sp)
        return fld_name

    def get_data(self, timestep):
        fld_data, *_ = self.field.get_data(
            timestep, theta=None,
            max_resolution_3d_tm=self.max_resolution_3d_tm)
        fld_data = self._trim_field(fld_data)
        fld_data = self._change_resolution(fld_data)
        fld_data = self._normalize_field(fld_data)
        return fld_data

    def get_axes_data(self, timestep):
        fld_md = self.field.get_only_metadata(
            timestep, theta=None,
            max_resolution_3d_tm=self.max_resolution_3d_tm)
        z = fld_md['axis']['z']['array']
        x = fld_md['axis']['x']['array']
        y = fld_md['axis']['y']['array']
        x, y, z = self._trim_axes(x, y, z)
        x, y, z = self._change_resolution_axes(x, y, z)
        ax_orig = np.array([z[0], x[0], y[0]])
        ax_spacing = np.array([z[1] - z[0], x[1] - x[0], y[1] - y[0]])
        return ax_orig, ax_spacing

    def get_vtk_opacity(self, timestep=None):
        opacity = self.get_opacity(timestep)
        self._set_vtk_opacity(opacity)
        return self.vtk_opacity

    def get_opacity(self, timestep=None):
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
        return opacity

    def set_opacity(self, opacity):
        self.opacity = opacity
        self._set_vtk_opacity(opacity)

    def get_vtk_colormap(self):
        cmap = self.get_colormap()
        self._set_vtk_colormap(cmap)
        return self.vtk_cmap

    def get_colormap(self):
        if isinstance(self.cmap, Colormap):
            cmap = self.cmap
        else:
            if self.style_handler.cmap_exists(self.cmap):
                cmap = self.style_handler.get_cmap(self.cmap)
            else:
                raise ValueError(
                    "Colormap '{}' does not exist.".format(self.cmap))
        return cmap

    def set_colormap(self, cmap):
        self.cmap = cmap
        self._set_vtk_colormap(cmap)

    def get_optimized_opacity(self, time_step, bins=11):
        hist, *_ = self.get_field_data_histogram(time_step, bins=bins)
        fld_val = np.linspace(0, 255, bins)
        op_val = 1 - hist
        opacity = Opacity(name='auto', fld_values=fld_val, op_values=op_val)
        return opacity

    def get_field_data_histogram(self, time_step, bins=11):
        fld_data = self.get_data(time_step)
        hist, hist_edges = np.histogram(fld_data, bins=bins)
        hist = np.ma.log(hist).filled(0)
        hist /= hist.max()
        return hist, hist_edges

    def _set_vtk_opacity(self, opacity):
        fld_vals, op_vals = opacity.get_opacity_values()
        self.vtk_opacity.RemoveAllPoints()
        for fv, ov in zip(fld_vals, op_vals):
            self.vtk_opacity.AddPoint(fv, ov)

    def _set_vtk_colormap(self, cmap):
        self.vtk_cmap.RemoveAllPoints()
        fld_val, r_val, g_val, b_val = cmap.get_cmap_values()
        # points = [x0, r0, g0, b0, x1, r1, g1, b1, ..., xN, rN, gN, bN]
        points = list(np.column_stack((fld_val, r_val, g_val, b_val)).flat)
        self.vtk_cmap.FillFromDataPointer(int(len(points)/4), points)

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

