"""
This file is part of VisualPIC.

The module contains the classes for 3D visualization with VTK.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""


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

from visualpic.helper_functions import get_common_timesteps
from visualpic.visualization.volume_appearance import *
if qt_installed:
    from visualpic.ui.basic_render_window import BasicRenderWindow


class VTKVisualizer():

    """Main class controlling the visualization"""

    def __init__(self, show_axes=True, show_cube_axes=False,
                 show_bounding_box=True, show_colorbars=True, show_logo=True,
                 background='default gradient', use_qt=True):
        """
        Initialize the 3D visualizer.

        Parameters
        ----------

        show_axes : bool
            Determines whether to show a 3D axis in the render.

        show_cube_axes : bool
            Determines whether to show a bounding box with the volume axes.

        show_bounding_box : bool
            Determines whether to show a bounding box around the 3D volume.

        show_colorbars : bool
            Determines whether to show the field colorbars.

        show_logo : bool
            Determines whether to show the VisualPIC logo in the render.

        background : str or list
            Background of the render. Possible string values are
            'default gradient', 'white' and 'black'. A list of 3 floats
            containing the RGB components (range 0 to 1) of any color can
            also be provided (e.g. background=[1, 1, 0.5]). Alternatively, 
            a list of two colors can also be given
            (e.g. background=['black', [1, 1, 0.5]]). In this case, the
            background will be a linear gradient between the two specified
            colors.

        use_qt : bool
            Whether to use Qt for the windows opened by the visualizer.
        """
        if use_qt and not qt_installed:
            print('Qt is not installed. Default VTK windows will be used.')
            use_qt = False
        self.vis_config = {'background': background,
                           'show_logo': show_logo,
                           'show_axes': show_axes,
                           'show_cube_axes': show_cube_axes,
                           'show_bounding_box': show_bounding_box,
                           'show_colorbars': show_colorbars,
                           'use_qt': use_qt}
        self.camera_props = {'zoom': 1}
        self.volume_field_list = []
        self.colorbar_widgets = []
        self.current_time_step = -1
        self.available_time_steps = None
        self._initialize_base_vtk_elements()
        self.set_background(background)

    def add_field(self, field, cmap='viridis', opacity='auto',
                  gradient_opacity='uniform opaque', vmax=None, vmin=None,
                  xtrim=None, ytrim=None, ztrim=None, resolution=None,
                  max_resolution_3d_tm=[100, 100]):
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
            'uniform opaque', 'uniform translucid' or any instace of Opacity.

        gradient_opacity : str or Opacity
            The gradient opacity to be used. Possible values are 'auto',
            'linear positive', 'linear negative', 'v shape', 'inverse v shape',
            'uniform opaque', 'uniform translucid' or any instace of Opacity.

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
            # check if this field has already been added to a volume
            name_suffix = None
            fld_repeated_idx = 0
            for vol_field in self.volume_field_list:
                if vol_field.field == field:
                    fld_repeated_idx += 1
                    name_suffix = str(fld_repeated_idx)
            # add to volume list
            volume_field = VolumetricField(
                field, cmap, opacity, gradient_opacity, vmax, vmin, xtrim,
                ytrim, ztrim, resolution, max_resolution_3d_tm, name_suffix)
            self.volume_field_list.append(volume_field)
            self._add_colorbar(volume_field)
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
        self.window.SetOffScreenRendering(1)
        if resolution is not None:
            self.window.SetSize(*resolution)
        self._make_timestep_render(timestep, ts_is_index)
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
        self._make_timestep_render(timestep, ts_is_index)
        self.window.SetOffScreenRendering(0)
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

    def show_cube_axes(self, value):
        """
        Show (for value=True) or hide (for value=False) the cube axes around
        the 3D volume.
        """
        self.vis_config['show_cube_axes'] = value
        self.vtk_cube_axes.SetVisibility(self.vis_config['show_cube_axes'])

    def show_bounding_box(self, value):
        """
        Show (for value=True) or hide (for value=False) the bounding box 
        around the 3D volume.
        """
        self.vis_config['show_bounding_box'] = value
        self.vtk_cube_axes_edges.SetVisibility(
            self.vis_config['show_bounding_box'])

    def show_colorbars(self, value):
        """
        Show (for value=True) or hide (for value=False) the field colorbars.
        """
        self.vis_config['show_colorbars'] = value
        if len(self.colorbar_widgets) > 0:
            for cw in self.colorbar_widgets:
                if value:
                    cw.On()
                else:
                    cw.Off()

    def show_logo(self, value):
        """
        Show (for value=True) or hide (for value=False) the VisualPIC logo in
        the render.
        """
        self.vis_config['show_logo'] = value
        self.visualpic_logo.SetVisibility(value)

    def set_background(self, background):
        """
        Set the render background.

        Parameters
        ----------
        background : str or list
            Possible string values are 'default gradient', 'white' and 'black'.
            A list of 3 floats containing the RGB components (range 0 to 1)
            of any color can also be provided (e.g. background=[1, 1, 0.5]).
            Alternatively, a list of two colors can also be given
            (e.g. background=['black', [1, 1, 0.5]]). In this case, the
            background will be a linear gradient between the two specified
            colors.

        """
        if (type(background) == list) and (len(background) == 2):
            self._set_background_colors(*background)
        elif background == 'default gradient':
            self._set_background_colors('black', [0.12, 0.3, 0.475])
        else:
            self._set_background_colors(background)
        self.vis_config['background'] = background

    def get_background(self):
        """Return the current render background."""
        return self.vis_config['background']

    def get_list_of_fields(self):
        """Returns a list with the names of all available fields."""
        fld_list = []
        for vol_field in self.volume_field_list:
            fld_list.append(vol_field.get_name())
        return fld_list

    def set_camera_angles(self, azimuth, elevation):
        """
        Set the azimuth and elevation angles of the camera. This values are
        additive, meaning that every time this method is called the angles are
        increased or decreased (negative values) by the specified value.

        Parameters
        ----------

        azimuth : float
            The azimuth angle in degrees.

        elevation : float
            The elevation angle in degrees.
        """
        self.camera.Azimuth(azimuth)
        self.camera.Elevation(elevation)

    def set_camera_zoom(self, zoom):
        """
        Set the camera zoom.

        Parameters
        ----------

        zoom : float
            The zoom value of the camera. A value greater than 1 is a zoom-in,
            a value less than 1 is a zoom-out.
        """
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

    def set_color_window(self, value):
        """
        Set the color window of the mapper (controls the contrast). For more
        information see
        https://vtk.org/doc/nightly/html/classvtkGPUVolumeRayCastMapper.html
        or
        https://vtk.org/doc/nightly/html/classvtkSmartVolumeMapper.html

        Parameters
        ----------

        value : float
            Default window value is 1.0. The value can also be <0, leading to a
            'negative' effect in the color.
        """
        self.vtk_volume_mapper.SetFinalColorWindow(value)

    def set_color_level(self, value):
        """
        Set the color level of the mapper (controls the brightness). For more
        information see
        https://vtk.org/doc/nightly/html/classvtkGPUVolumeRayCastMapper.html
        or
        https://vtk.org/doc/nightly/html/classvtkSmartVolumeMapper.html

        Parameters
        ----------

        value : float
            Default level value is 0.5. The final color window will be centered
            at the final color level, and together represent a linear
            remapping of color values.
        """
        self.vtk_volume_mapper.SetFinalColorLevel(value)

    def set_contrast(self, value):
        """
        Set the contrast of the render without having to manually change the
        color window. For full control, using 'set_color_window' is advised.

        Parameters
        ----------

        value : float
            A float between -1 (minimum contrast) and 1 (maximum contrast).
            The default contrast is 0.
        """
        if value < -1:
            value = -1
        elif value > 1:
            value = 1
        color_window = 10 ** (-value)
        brightness = self.get_brightness()
        self.set_color_window(color_window)
        self.set_brightness(brightness)

    def set_brightness(self, value):
        """
        Set the brightness of the render without having to manually change the
        color level. For full control, using 'set_color_level' is advised.

        Parameters
        ----------

        value : float
            A float between -1 (minimum brightness) and 1 (maximum brightness).
            The default brightness is 0.
        """
        if value < -1:
            value = -1
        elif value > 1:
            value = 1
        w = self.get_color_window()
        color_level = 0.5 - (0.5 + w/2)*value
        self.set_color_level(color_level)

    def get_color_window(self):
        """Return the color window value"""
        return self.vtk_volume_mapper.GetFinalColorWindow()

    def get_color_level(self):
        """Return the color level value"""
        return self.vtk_volume_mapper.GetFinalColorLevel()

    def get_contrast(self):
        """Return the contrast value"""
        w = self.vtk_volume_mapper.GetFinalColorWindow()
        return -np.log10(np.abs(w))

    def get_brightness(self):
        """Return the brightness value"""
        l = self.vtk_volume_mapper.GetFinalColorLevel()
        w = self.vtk_volume_mapper.GetFinalColorWindow()
        return (1 - 2*l) / (1 + np.abs(w))

    def _make_timestep_render(self, timestep, ts_is_index=True):
        """
        Loads the time step data into the vtk volume and sets up the camera.
        """
        if ts_is_index:
            self.current_time_step = self.available_time_steps[timestep]
        else:
            if timestep not in self.available_time_steps:
                raise ValueError(
                    'Time step {} is not available.'.format(timestep))
            self.current_time_step = timestep
        if self.old_vtk:
            self._load_data_into_volume(self.current_time_step)
        else:
            self._load_data_into_multi_volume(self.current_time_step)
        self._setup_cube_axes_and_bbox()
        self._setup_camera()

    def _setup_cube_axes_and_bbox(self):
        ax_data = self.volume_field_list[0].get_axes_data(
            self.current_time_step)
        ax_range = ax_data[2]
        ax_units = ax_data[3]
        x_range = ax_range[0]
        y_range = ax_range[1]
        z_range = ax_range[2]
        self.vtk_cube_axes_edges.SetBounds(self.vtk_volume.GetBounds())
        self.vtk_cube_axes.SetBounds(self.vtk_volume.GetBounds())
        self.vtk_cube_axes.SetXTitle('z')
        self.vtk_cube_axes.SetYTitle('y')
        self.vtk_cube_axes.SetZTitle('x')
        self.vtk_cube_axes.SetXAxisRange(x_range[0], x_range[1])
        self.vtk_cube_axes.SetYAxisRange(y_range[0], y_range[1])
        self.vtk_cube_axes.SetZAxisRange(z_range[0], z_range[1])
        self.vtk_cube_axes.SetXUnits(ax_units[0])
        self.vtk_cube_axes.SetYUnits(ax_units[1])
        self.vtk_cube_axes.SetZUnits(ax_units[2])

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
        self.vtk_volume_mapper = vtk.vtkGPUVolumeRayCastMapper()
        self.vtk_volume_mapper.UseJitteringOn()
        self.vtk_volume.SetMapper(self.vtk_volume_mapper)
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
        self._add_axes_widget()
        self._add_cube_axes()
        self._add_bounding_box()
        self._add_visualpic_logo()

    def _set_background_colors(self, color, color_2=None):
        """
        Set the background color of the 3D visualizer.

        Parameters
        ----------

        color : str or list
            Background color of the render. Possible values are 'black',
            'white' or a list of 3 floats with the RGB values.

        color_2 : str or list
            If specified, a linear gradient backround is set where 'color_2'
            is the second color of the gradient. Possible values are 'black',
            'white' or a list of 3 floats with the RGB values.
        """
        if isinstance(color, str):
            if color == 'white':
                self.renderer.SetBackground(1, 1, 1)
            elif color == 'black':
                self.renderer.SetBackground(0, 0, 0)
        else:
            self.renderer.SetBackground(*color)
        if color_2 is not None:
            self.renderer.GradientBackgroundOn()
            if isinstance(color_2, str):
                if color_2 == 'white':
                    self.renderer.SetBackground2(1, 1, 1)
                elif color_2 == 'black':
                    self.renderer.SetBackground2(0, 0, 0)
            else:
                self.renderer.SetBackground2(*color_2)
        else:
            self.renderer.GradientBackgroundOff()

    def _add_axes_widget(self):
        self.vtk_axes = vtk.vtkAxesActor()
        self.vtk_axes.SetXAxisLabelText("Z")
        self.vtk_axes.SetZAxisLabelText("X")
        self.vtk_axes.GetZAxisShaftProperty().SetColor(0.129, 0.467, 0.694)
        self.vtk_axes.GetZAxisTipProperty().SetColor(0.129, 0.467, 0.694)
        self.vtk_axes.GetXAxisShaftProperty().SetColor(0.835, 0.165, 0.176)
        self.vtk_axes.GetXAxisTipProperty().SetColor(0.835, 0.165, 0.176)
        self.vtk_axes.GetYAxisShaftProperty().SetColor(0.188, 0.627, 0.224)
        self.vtk_axes.GetYAxisTipProperty().SetColor(0.188, 0.627, 0.224)
        self.vtk_orientation_marker = vtk.vtkOrientationMarkerWidget()
        self.vtk_orientation_marker.SetOutlineColor(1, 1, 1)
        self.vtk_orientation_marker.SetOrientationMarker(self.vtk_axes)
        self.vtk_orientation_marker.SetInteractor(self.interactor)
        self.vtk_orientation_marker.SetViewport(0, 0, 0.2, 0.2)
        self.show_axes(self.vis_config['show_axes'])
        self.vtk_orientation_marker.InteractiveOff()

    def _add_cube_axes(self):
        self.vtk_cube_axes = vtk.vtkCubeAxesActor()
        self.vtk_cube_axes.SetCamera(self.camera)
        self.vtk_cube_axes.StickyAxesOff()
        self.vtk_cube_axes.SetVisibility(self.vis_config['show_cube_axes'])
        self.renderer.AddActor(self.vtk_cube_axes)

    def _add_bounding_box(self):
        self.vtk_cube_axes_edges = vtk.vtkCubeAxesActor()
        self.vtk_cube_axes_edges.SetCamera(self.camera)
        self.vtk_cube_axes_edges.SetFlyModeToStaticEdges()
        self.vtk_cube_axes_edges.StickyAxesOff()
        self.vtk_cube_axes_edges.SetVisibility(
            self.vis_config['show_bounding_box'])
        self.vtk_cube_axes_edges.XAxisLabelVisibilityOff()
        self.vtk_cube_axes_edges.XAxisTickVisibilityOff()
        self.vtk_cube_axes_edges.YAxisLabelVisibilityOff()
        self.vtk_cube_axes_edges.YAxisTickVisibilityOff()
        self.vtk_cube_axes_edges.ZAxisLabelVisibilityOff()
        self.vtk_cube_axes_edges.ZAxisTickVisibilityOff()
        self.renderer.AddActor(self.vtk_cube_axes_edges)

    def _add_visualpic_logo(self):
        self.vtk_image_data = vtk.vtkImageData()
        self.logo_path = resource_filename(
            'visualpic.ui.icons', 'vp_logo_horiz_transp.png')
        self.vtk_png_reader = vtk.vtkPNGReader()
        self.vtk_png_reader.SetFileName(self.logo_path)
        self.vtk_png_reader.Update()
        self.vtk_image_data = self.vtk_png_reader.GetOutput()
        self.visualpic_logo = vtk.vtkLogoRepresentation()
        self.visualpic_logo.SetImage(self.vtk_image_data)
        self.visualpic_logo.SetPosition(0.79, 0.01)
        self.visualpic_logo.SetPosition2(.2, .1)
        self.visualpic_logo.GetImageProperty().SetOpacity(1)
        self.visualpic_logo.GetImageProperty().SetDisplayLocationToBackground()
        self.renderer.AddViewProp(self.visualpic_logo)
        self.visualpic_logo.SetRenderer(self.renderer)
        self.show_logo(self.vis_config['show_logo'])

    def _load_data_into_volume(self, timestep):
        vtk_volume_prop = self._get_volume_properties(timestep)
        vtk_data_import = self._import_data(timestep)
        # Setup mapper
        self.vtk_volume_mapper.SetInputConnection(
            vtk_data_import.GetOutputPort())
        self.vtk_volume_mapper.Update()
        # Add to volume
        self.vtk_volume.SetProperty(vtk_volume_prop)

    def _load_data_into_multi_volume(self, timestep):
        # Workaround to fix wrong volume boundaries when a 'vtkMultiVolume' has
        # only a single volume. The fix replaces the 'vtkMultiVolume' for a
        # 'vtkVolume' and then calls '_load_data_into_volume'.
        if len(self.volume_field_list) == 1:
            if type(self.vtk_volume) != vtk.vtkVolume:
                self.renderer.RemoveVolume(self.vtk_volume)
                self.vtk_volume = vtk.vtkVolume()
                self.renderer.AddVolume(self.vtk_volume)
                self.vtk_volume.SetMapper(self.vtk_volume_mapper)
            return self._load_data_into_volume(timestep)
        # If the 'vtkMultiVolume' was replaced by a 'vtkVolume' but now the
        # number of volumes is >1, go back to having a 'vtkMultiVolume'.
        if type(self.vtk_volume) != vtk.vtkMultiVolume:
            self.renderer.RemoveVolume(self.vtk_volume)
            self.vtk_volume = vtk.vtkMultiVolume()
            self.renderer.AddVolume(self.vtk_volume)
            self.vtk_volume.SetMapper(self.vtk_volume_mapper)
        # End of workaround

        # Workaround for avoiding segmentation fault using vtkMultiVolume.
        # A new mapper has to be created instead of updated when switching
        # time steps.
        cw = self.get_color_window()
        cl = self.get_color_level()
        self.vtk_volume_mapper = vtk.vtkGPUVolumeRayCastMapper()
        self.vtk_volume_mapper.UseJitteringOn()
        self.vtk_volume.SetMapper(self.vtk_volume_mapper)
        self.set_color_window(cw)
        self.set_color_level(cl)
        # End of workaround.

        vtk_vols, imports = self._create_volumes(timestep)
        for i, (vol, imp) in enumerate(zip(vtk_vols, imports)):
            self.vtk_volume_mapper.SetInputConnection(i, imp.GetOutputPort())
            self.vtk_volume.SetVolume(vol, i)

    def _create_volumes(self, timestep):
        vol_list = list()
        imports_list = list()
        for i, vol_field in enumerate(self.volume_field_list):
            vtk_vol = vtk.vtkVolume()
            vtk_volume_prop = vtk.vtkVolumeProperty()
            vtk_volume_prop.SetInterpolationTypeToLinear()
            vtk_volume_prop.SetColor(vol_field.get_vtk_colormap())
            vtk_volume_prop.SetScalarOpacity(
                vol_field.get_vtk_opacity(timestep))
            vtk_volume_prop.SetGradientOpacity(
                vol_field.get_vtk_gradient_opacity(timestep))
            vtk_volume_prop.ShadeOff()
            vtk_vol.SetProperty(vtk_volume_prop)
            vol_data = vol_field.get_data(timestep)
            vol_list.append(vtk_vol)

            ax_orig, ax_spacing, *_ = vol_field.get_axes_data(timestep)
            max_spacing = max(ax_spacing)
            max_cell_size = 0.1
            norm_factor = max_cell_size/max_spacing
            ax_orig *= norm_factor
            ax_spacing *= norm_factor

            # Put data in VTK format
            vtk_data_import = vtk.vtkImageImport()
            vtk_data_import.SetImportVoidPointer(vol_data)
            vtk_data_import.SetDataScalarTypeToFloat()
            vtk_data_import.SetDataExtent(0, vol_data.shape[2]-1,
                                          0, vol_data.shape[1]-1,
                                          0, vol_data.shape[0]-1)
            vtk_data_import.SetWholeExtent(0, vol_data.shape[2]-1,
                                           0, vol_data.shape[1]-1,
                                           0, vol_data.shape[0]-1)
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
            vtk_volume_prop.SetGradientOpacity(
                vol_field.get_vtk_gradient_opacity(timestep))
            vtk_volume_prop.ShadeOff(i)
        return vtk_volume_prop

    def _import_data(self, timestep):
        # Get data
        volume_data_list = list()
        for i, vol_field in enumerate(self.volume_field_list):
            volume_data_list.append(vol_field.get_data(timestep))
        self._data_all_volumes = np.concatenate(
            [aux[..., np.newaxis] for aux in volume_data_list], axis=3)
        ax_orig, ax_spacing, *_ = self.volume_field_list[0].get_axes_data(
            timestep)
        max_spacing = max(ax_spacing)
        max_cell_size = 0.1
        norm_factor = max_cell_size/max_spacing
        ax_orig *= norm_factor
        ax_spacing *= norm_factor

        # Put data in VTK format
        vtk_data_import = vtk.vtkImageImport()
        vtk_data_import.SetImportVoidPointer(self._data_all_volumes)
        vtk_data_import.SetDataScalarTypeToFloat()
        vtk_data_import.SetNumberOfScalarComponents(
            len(self.volume_field_list))
        vtk_data_import.SetDataExtent(0, self._data_all_volumes.shape[2]-1,
                                      0, self._data_all_volumes.shape[1]-1,
                                      0, self._data_all_volumes.shape[0]-1)
        vtk_data_import.SetWholeExtent(0, self._data_all_volumes.shape[2]-1,
                                       0, self._data_all_volumes.shape[1]-1,
                                       0, self._data_all_volumes.shape[0]-1)
        vtk_data_import.SetDataSpacing(ax_spacing[0],
                                       ax_spacing[1],
                                       ax_spacing[2])
        # data origin is also changed by the normalization
        vtk_data_import.SetDataOrigin(ax_orig[0], ax_orig[1], ax_orig[2])
        vtk_data_import.Update()
        return vtk_data_import

    def _add_colorbar(self, volume_field):
        cbar = volume_field.get_colorbar(5)
        cbar_widget = vtk.vtkScalarBarWidget()
        cbar_widget.SetInteractor(self.interactor)
        cbar_widget.SetScalarBarActor(cbar)
        cbar_widget.RepositionableOff()
        cbar_widget.ResizableOff()
        cbar_widget.SelectableOff()
        if self.vis_config['show_colorbars']:
            cbar_widget.On()
        else:
            cbar_widget.Off()
        self.colorbar_widgets.append(cbar_widget)
        # (re)position colorbars
        min_x = 0.87
        max_x = 0.93
        min_y = 0.12
        max_y = 0.98
        sep = 0.02
        tot_height = max_y - min_y
        tot_width = max_x - min_x
        n_cbars = len(self.colorbar_widgets)
        for i, cw in enumerate(self.colorbar_widgets):
            w_cw = tot_width
            h_cw = (tot_height - (n_cbars-1)*sep) / n_cbars
            y_1 = min_y + i*(h_cw+sep)
            y_2 = h_cw
            x_1 = min_x
            x_2 = w_cw
            rep = cw.GetRepresentation()
            rep.SetPosition(x_1, y_1)
            rep.SetPosition2(x_2, y_2)


class VolumetricField():

    """Class for the volumetric fields to be displayed."""

    def __init__(self, field, cmap='viridis', opacity='auto',
                 gradient_opacity='uniform opaque', vmax=None, vmin=None,
                 xtrim=None, ytrim=None, ztrim=None, resolution=None,
                 max_resolution_3d_tm=None, name_suffix=None):
        self.field = field
        self.style_handler = VolumeStyleHandler()
        self.cmap = cmap
        self.opacity = opacity
        self.gradient_opacity = gradient_opacity
        self.vmax = vmax
        self.vmin = vmin
        self.xtrim = xtrim  # [-1, 1]
        self.ytrim = ytrim
        self.ztrim = ztrim
        self.resolution = resolution
        self.name_suffix = name_suffix
        self.max_resolution_3d_tm = max_resolution_3d_tm
        self.vtk_opacity = vtk.vtkPiecewiseFunction()
        self.vtk_gradient_opacity = vtk.vtkPiecewiseFunction()
        self.vtk_cmap = vtk.vtkColorTransferFunction()
        self.cbar = None
        self.cbar_ticks = 5
        self._loaded_timestep = None

    def get_name(self):
        fld_name = self.field.field_name
        fld_sp = self.field.species_name
        if fld_sp is not None:
            fld_name += ' [{}]'.format(fld_sp)
        if self.name_suffix is not None:
            fld_name += ' ({})'.format(self.name_suffix)
        return fld_name

    def get_data(self, timestep):
        self._load_data(timestep)
        return self._field_data

    def _load_data(self, timestep, only_metadata=False):
        if self._loaded_timestep != timestep:
            fld_data, fld_md = self.field.get_data(
                timestep, theta=None,
                max_resolution_3d_tm=self.max_resolution_3d_tm)
            fld_data = self._trim_field(fld_data)
            fld_data = self._change_resolution(fld_data)
            min_fld = np.min(fld_data)
            max_fld = np.max(fld_data)
            self._original_data_range = [min_fld, max_fld]
            fld_data = self._normalize_field(fld_data)
            self._field_data = fld_data
            self._field_metadata = fld_md
            if not only_metadata:
                self._loaded_timestep = timestep
            if self.cbar is not None:
                self.update_colorbar(timestep)

    def update_colorbar(self, timestep):
        cbar_range = np.array(self.get_range(timestep))
        self.vtk_cmap.ResetAnnotations()
        max_val = np.max(np.abs(cbar_range))
        ord = int(np.log10(max_val))  # get order of magnitude
        cbar_range = cbar_range/10**ord
        norm_fld_vals = np.linspace(0, 255, self.cbar_ticks)
        real_fld_vals = np.linspace(
            cbar_range[0], cbar_range[1], self.cbar_ticks)
        for j in np.arange(self.cbar_ticks):
            self.vtk_cmap.SetAnnotation(norm_fld_vals[j],
                                        format(real_fld_vals[j], '.2f'))
        if ord != 0:
            order_str = '10^' + str(ord) + ' '
        else:
            order_str = ''
        title = self.get_name() + '\n['
        if order_str != '':
            title += order_str + '\n'
        title += self.get_field_units() + ']'
        self.cbar.SetTitle(title)

    def get_colorbar(self, n_ticks):
        if self.cbar is None:
            self.cbar = vtk.vtkScalarBarActor()
            self.cbar.SetLookupTable(self.vtk_cmap)
            self.cbar.DrawTickLabelsOff()
            self.cbar.AnnotationTextScalingOn()
            self.cbar.GetAnnotationTextProperty().SetFontSize(6)
            self.cbar.GetTitleTextProperty().SetFontSize(6)
            self.cbar.SetTextPositionToPrecedeScalarBar()
        self.cbar_ticks = n_ticks
        if self._loaded_timestep is not None:
            self.update_colorbar(self._loaded_timestep)
        return self.cbar

    def get_axes_data(self, timestep):
        self._load_data(timestep, only_metadata=True)
        fld_md = self._field_metadata
        z = fld_md['axis']['z']['array']
        x = fld_md['axis']['x']['array']
        y = fld_md['axis']['y']['array']
        x, y, z = self._trim_axes(x, y, z)
        x, y, z = self._change_resolution_axes(x, y, z)
        ax_orig = np.array([z[0], x[0], y[0]])
        ax_spacing = np.array([z[1] - z[0], x[1] - x[0], y[1] - y[0]])
        ax_range = [[z[0], z[-1]], [x[0], x[-1]], [y[0], y[-1]]]
        ax_units = [fld_md['axis']['z']['units'],
                    fld_md['axis']['x']['units'],
                    fld_md['axis']['y']['units']]
        return ax_orig, ax_spacing, ax_range, ax_units

    def get_field_units(self):
        if self._field_metadata is not None:
            fld_md = self._field_metadata
        else:
            fld_md = self.field.get_only_metadata(self.field.timesteps[0])
        return fld_md['field']['units']

    def get_range(self, timestep):
        if (self.vmin is None) or (self.vmax is None):
            vmin, vmax = self.get_original_data_range(timestep)
        if self.vmin is not None:
            vmin = self.vmin
        if self.vmax is not None:
            vmax = self.vmax
        return vmin, vmax

    def get_original_data_range(self, timestep):
        self._load_data(timestep)
        return self._original_data_range

    def set_range(self, vmin, vmax):
        # If data is already loaded, set range and renormalize data.
        if self._loaded_timestep is not None:
            current_vmin, current_vmax = self.get_range(self._loaded_timestep)
            self._field_data *= (current_vmax-current_vmin) / 255
            self._field_data += current_vmin
            self.vmin = vmin
            self.vmax = vmax
            self._field_data = self._normalize_field(self._field_data)
        # Otherwise just set the range
        else:
            self.vmin = vmin
            self.vmax = vmax

    def get_vtk_opacity(self, timestep=None):
        opacity = self.get_opacity(timestep)
        self._set_vtk_opacity(opacity)
        return self.vtk_opacity

    def get_vtk_gradient_opacity(self, timestep=None):
        opacity = self.get_gradient_opacity(timestep)
        self._set_vtk_gradient_opacity(opacity)
        return self.vtk_gradient_opacity

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

    def get_gradient_opacity(self, timestep=None):
        if (isinstance(self.gradient_opacity, Opacity) or
                self.gradient_opacity is None):
            opacity = self.gradient_opacity
        elif self.gradient_opacity != 'auto':
            if self.style_handler.opacity_exists(self.gradient_opacity):
                opacity = self.style_handler.get_opacity(self.gradient_opacity)
            else:
                raise ValueError(
                    "Opacity '{}' does not exist.".format(
                        self.gradient_opacity))
        else:
            opacity = self.get_optimized_gradient_opacity(timestep)
        return opacity

    def set_opacity(self, opacity):
        self.opacity = opacity
        self._set_vtk_opacity(opacity)

    def set_gradient_opacity(self, opacity):
        self.gradient_opacity = opacity
        self._set_vtk_gradient_opacity(opacity)

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

    def get_optimized_gradient_opacity(self, time_step, bins=11):
        hist, *_ = self.get_field_data_gradient_histogram(time_step, bins=bins)
        fld_val = np.linspace(0, 255, bins)
        op_val = 1 - hist
        opacity = Opacity(name='auto', fld_values=fld_val, op_values=op_val)
        return opacity

    def get_field_data_histogram(self, time_step, bins=11):
        """
        Create a 1D histogram of the field values. The amount of values below
        or under the [vmin, vmax] range (if specified) is added to the boundary
        bins.
        """
        fld_data = self.get_data(time_step)
        bin_edges = np.linspace(0, 255, bins+1)
        fld_min = np.min(fld_data)
        fld_max = np.max(fld_data)
        if fld_min < 0:
            bin_edges = np.insert(bin_edges, 0, fld_min)
        if fld_max > 255:
            bin_edges = np.append(bin_edges, fld_max)
        hist, *_ = np.histogram(fld_data, bins=bin_edges)
        if fld_min < 0:
            hist[1] += hist[0]
            hist = hist[1:]
        if fld_max > 255:
            hist[-2] += hist[-1]
            hist = hist[:-1]
        hist = np.ma.log(hist).filled(0)
        hist /= hist.max()
        return hist, bin_edges

    def get_field_data_gradient_histogram(self, time_step, bins=11):
        fld_data = self.get_data(time_step)
        fld_grad = np.gradient(fld_data)
        fld_grad = np.sqrt(fld_grad[0]**2 + fld_grad[1]**2 + fld_grad[2]**2)
        hist, hist_edges = np.histogram(fld_grad, bins=bins)
        hist = np.ma.log(hist).filled(0)
        hist /= hist.max()
        return hist, hist_edges

    def _set_vtk_opacity(self, opacity):
        fld_vals, op_vals = opacity.get_opacity_values()
        self.vtk_opacity.RemoveAllPoints()
        for fv, ov in zip(fld_vals, op_vals):
            self.vtk_opacity.AddPoint(fv, ov)

    def _set_vtk_gradient_opacity(self, opacity):
        fld_vals, op_vals = opacity.get_opacity_values()
        self.vtk_gradient_opacity.RemoveAllPoints()
        for fv, ov in zip(fld_vals, op_vals):
            self.vtk_gradient_opacity.AddPoint(fv, ov)

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
            zmin = int(np.round(shape[2]/2 * (self.ztrim[0] + 1)))
            zmax = int(np.round(shape[2]/2 * (self.ztrim[1] + 1)))
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
        # Normalizing to a range between 0-255 is not only useful to simplify
        # setting the colormaps and opacities. It also prevents large numbers
        # in the fields which might lead to problems with vtk depending on the
        # GPU used.
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
        # Type conversion to single precission, if needed
        fld_data = fld_data.astype(np.float32, copy=False)
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
