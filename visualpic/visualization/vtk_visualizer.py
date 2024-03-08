"""
This file is part of VisualPIC.

The module contains the classes for 3D visualization with VTK.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""


import os
import sys
from pkg_resources import resource_filename
import warnings

import numpy as np
from scipy.ndimage import zoom
try:
    import vtk
    vtk_installed = True
except:
    vtk_installed = False
try:
    import pyvista as pv
    pyvista_installed = True
except:
    pyvista_installed = False
try:
    from PyQt5 import QtWidgets
    qt_installed = True
except:
    qt_installed = False

from visualpic.helper_functions import get_common_timesteps
from visualpic.visualization.volume_appearance import (VolumeStyleHandler,
                                                       Colormap, Opacity)
if qt_installed and vtk_installed:
    from visualpic.ui.basic_render_window import BasicRenderWindow


class VTKVisualizer():

    """Main class controlling the 3D visualization"""

    def __init__(self, show_axes=True, show_cube_axes=True,
                 show_bounding_box=True, show_colorbars=True, show_logo=True,
                 background='default gradient', scale_x=1, scale_y=1,
                 scale_z=1, forced_norm_factor=None,
                 use_qt=True, use_multi_volume=False,
                 window_size=[600, 400]):
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

        scale_x : float
            Scaling factor of the horizontal direction. A value < 1 will lead
            to a shrinking of the x-axis, while a value > 1 will magnify it.

        scale_y : float
            Scaling factor of the vertical direction. A value < 1 will lead
            to a shrinking of the y-axis, while a value > 1 will magnify it.

        scale_z : float
            Scaling factor of the longitudinal direction. A value < 1 will lead
            to a shrinking of the z-axis, while a value > 1 will magnify it.

        forced_norm_factor : float
            Normalization factor between the data units and the vtk units. By
            default, visualpic applies a scaling factor to the visualized data
            (its value depends on the data units) to normalize its spatial
            dimesions in order to make sure that it has a reasonable size in
            spatial units. If for some reason the automatic scaling leads to
            issues, a custom scaling can be forced by specifying this
            parameter.

        use_qt : bool
            Whether to use Qt for the windows opened by the visualizer.

        use_multi_volume : bool
            Whether to use vtkMultiVolume or vtkVolume for the volume
            rendering.

        window_size : sequence[int], optional
            Window size in pixels.  Defaults to ``[600, 400]``

        """
        self._check_dependencies()
        use_qt = self._check_qt(use_qt)
        self.vis_config = {'background': background,
                           'show_logo': show_logo,
                           'show_axes': show_axes,
                           'show_cube_axes': show_cube_axes,
                           'show_bounding_box': show_bounding_box,
                           'show_colorbars': show_colorbars,
                           'axes_scale': [scale_z, scale_y, scale_x],
                           'use_qt': use_qt,
                           'use_multi_volume': use_multi_volume}
        self._unit_norm_factors = {'m': 1e5,
                                   'um': 0.1,
                                   'c/\\omega_p': 1}
        self.forced_norm_factor = forced_norm_factor
        self.camera_props = {'zoom': 1, 'focus_shift': None}
        self.volume_field_list = []
        self.scatter_species_list = []
        self.colorbar_list = []
        self.colorbar_widgets = []
        self._colorbar_visibility = []
        self.current_time_step = -1
        self.available_time_steps = None
        self._window_size = window_size
        self._initialize_base_vtk_elements()
        self.set_background(background)

    def add_field(self, field, cmap='viridis', opacity='auto',
                  gradient_opacity='uniform opaque', vmax=None, vmin=None,
                  xtrim=None, ytrim=None, ztrim=None, resolution=None,
                  max_resolution_3d=[100, 100]):
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
            'uniform opaque', 'uniform translucid', the path to an .h5 file
            containing an opacity or any instace of Opacity.

        gradient_opacity : str or Opacity
            The gradient opacity to be used. Possible values are 'auto',
            'linear positive', 'linear negative', 'v shape', 'inverse v shape',
            'uniform opaque', 'uniform translucid', the path to an .h5 file
            containing an opacity or any instace of Opacity.

        vmin, vmax : float
            Define the minimum and the maximum of the range of field values
            that the colormap and opacity cover.

        xtrim, ytrim, ztrim : list
            Allow to downselect the field volume to be displayed by trimming
            off the parts out of the range defined by these parameters. The
            provided value should be a list of two values containing the
            minimum and maximum of the spatial range to be displayed along the
            desired axis. These values should be between -1 and 1, which
            correspond to the minimum and the maximum of the original data. For
            example xtrim=[-1, 1] wont have any effect, as it preserves all
            data. On the contrary, xtrim=[-0.5, 0.5] would lead to only half of
            the field around the x axis.

        resolution : list
            This allows rendering the field with a different 3D resolution than
            that of the original data. A list of 3 integers should be provided
            contaning the resolution along z (longitudinal), x and y
            (transverse).

        max_resolution_3d : list
            Maximum longitudinal and transverse resolution (eg. [1000, 500])
            that the 3d field generated from thetaMode cylindrical data should
            have. This allows for faster reconstruction of the 3d field and
            less memory usage.

        """
        if field.get_geometry() in ['cylindrical', 'thetaMode', '3dcartesian']:
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
                ytrim, ztrim, resolution, max_resolution_3d, name_suffix)
            self.volume_field_list.append(volume_field)
            self.colorbar_list.append(volume_field.get_colorbar(5))
            self.available_time_steps = self.get_possible_timesteps()
        else:
            fld_geom = field.get_geometry()
            raise ValueError(
                "Field geometry '{}' not supported.".format(fld_geom))

    def add_species(self, species, color='w', cmap='viridis', vmax=None,
                    vmin=None, xtrim=None, ytrim=None, ztrim=None, size=1,
                    color_according_to=None, scale_with_charge=False):
        """
        Add a particle species to the 3D visualization.

        Parameters
        ----------

        species : Species
            The particle species to be displayed.

        color : str or list
            The color of the particles. Can be a string with the name of any
            matplotlib color or a list with 3 RGV values (range 0 to 1). This
            parameter is ignore if color_according_to is not None. In this
            case a colormap is instead used.

        cmap : str
            Colormap to apply to the particles. Only used if color_according_to
            is not None. Possible values are the same as those availabe
            in matplotlib.

        vmin, vmax : float
            Define the minimum and the maximum of the range of field values
            that the colormap covers.

        xtrim, ytrim, ztrim : list
            Allow to downselect the particles to be displayed by trimming
            off the those out of the range defined by these parameters. The
            provided value should be a list of two values containing the
            minimum and maximum of the spatial range to be displayed along the
            desired axis. These values should be between -1 and 1, which
            correspond to the minimum and the maximum of the simulation box.
            For example xtrim=[-1, 1] will cut any particle out of the
            simulation box. xtrim=[0, 1] would lead to showing only the
            particles along the positive x within the simulation box.

        size : float
            Size of the particles.

        color_according_to : str
            Name of a particle component according to which the particles
            should be colored. The colors follow the specified colormap.

        scale_with_charge : bool
            If true, the size of the particles will be proportional to their
            charge, where those with the maximum charge will have the size
            specified by the size parameter.

        """
        sp_comps = species.get_list_of_available_components()
        if ('x' in sp_comps) and ('y' in sp_comps) and ('z' in sp_comps):
            # check if this species has already been added to a ScatterSpecies
            name_suffix = None
            sp_repeated_idx = 0
            for sc_species in self.scatter_species_list:
                if sc_species.species == species:
                    sp_repeated_idx += 1
                    name_suffix = str(sp_repeated_idx)
            scatter_species = ScatterSpecies(
                species, color, cmap, vmax, vmin, xtrim, ytrim, ztrim, size,
                color_according_to, scale_with_charge, self._unit_norm_factors,
                self.forced_norm_factor, name_suffix)
            self.scatter_species_list.append(scatter_species)
            self.renderer.AddActor(scatter_species.get_actor())
            self.available_time_steps = self.get_possible_timesteps()
            self.colorbar_list.append(scatter_species.get_colorbar(5))
        else:
            raise ValueError(
                'Particle species cannot be added because it is not 3D.')

    def render_to_file(self, timestep, file_path, resolution=None,
                       scale=1, ts_is_index=True):
        """
        Render the fields in the visualizer at a specific time step and save
        image to a file.

        Parameters
        ----------

        timestep : int
            Time step of the fields to be rendered. Can be the index of a
            time step in self.available_time_steps or directly the numerical
            value of a time step. This is indicated by the 'ts_is_index'
            parameter.

        file_path : str
            Path to the file to which the render should be saved.

        resolution : list
            List containing the horizontal and vertical resolution of the
            rendered image.

        scale : int
            Scales the output resolution by this factor.

        ts_is_index : bool
            Indicates whether the value provided in 'timestep' is the index of
            the time step (True) or the numerical value of the time step
            (False).

        """
        self.window.SetOffScreenRendering(1)
        if resolution is not None:
            self.window.SetSize(*resolution)
        # Only make render if any data has been added for visualization
        if len(self.volume_field_list + self.scatter_species_list) > 0:
            self._make_timestep_render(timestep, ts_is_index)
        self.window.Render()
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(self.window)
        w2if.SetScale(scale)
        w2if.Update()
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(file_path)
        writer.SetInputConnection(w2if.GetOutputPort())
        writer.Write()

    def show(self, timestep=0, ts_is_index=True, window_size=None):
        """
        Render and show the fields in the visualizer at a specific time step.

        Parameters
        ----------

        timestep : int
            Time step of the fields to be rendered. Can be the index of a
            time step in self.available_time_steps or directly the numerical
            value of a time step. This is indicated by the 'ts_is_index'
            parameter.

        ts_is_index : bool
            Indicates whether the value provided in 'timestep' is the index of
            the time step (True) or the numerical value of the time step
            (False).

        window_size : list
            List containing the horizontal and vertical size of the
            render window. If given, it overrides the window size of the
            `VTKVisualizer`.

        """
        # Only make render if any data has been added for visualization
        if len(self.volume_field_list + self.scatter_species_list) > 0:
            self._make_timestep_render(timestep, ts_is_index)
        self.window.SetOffScreenRendering(0)
        if window_size is None:
            window_size = self._window_size
        if self.vis_config['use_qt']:
            app = QtWidgets.QApplication(sys.argv)
            self.qt_window = BasicRenderWindow(self, window_size=window_size)
            app.exec_()
        else:
            self.window.SetSize(*window_size)
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
        if isinstance(background, list) and (len(background) == 2):
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

    def get_list_of_species(self):
        """Returns a list with the names of all available species."""
        sp_list = []
        for species in self.scatter_species_list:
            sp_list.append(species.get_name())
        return sp_list

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

    def set_camera_shift(self, shift):
        """
        Shift the focal point of the camera in three directions.

        Parameters
        ----------

        shift : list
            The three components of the shift vector.
        """
        self.camera_props['focus_shift'] = shift

    def get_possible_timesteps(self):
        """
        Returns a numpy array with all the time steps commonly available
        to all fields in the visualizer.
        """
        data_list = []
        for volume in self.volume_field_list:
            data_list.append(volume.field)
        for species in self.scatter_species_list:
            data_list.append(species.species)
        return get_common_timesteps(data_list)

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
        color_level = self.vtk_volume_mapper.GetFinalColorLevel()
        color_window = self.vtk_volume_mapper.GetFinalColorWindow()
        return (1 - 2*color_level) / (1 + np.abs(color_window))

    def draw_colorbars(self):
        cbar_visibility = [True] * len(self.colorbar_list)
        for species in self.scatter_species_list:
            if species.get_color_according_to() is None:
                cbar_idx = self.colorbar_list.index(species.cbar)
                cbar_visibility[cbar_idx] = False
        if cbar_visibility != self._colorbar_visibility:
            self._colorbar_visibility = cbar_visibility
            self.colorbar_widgets.clear()
            for cbar, cbar_vis in zip(self.colorbar_list, cbar_visibility):
                if cbar_vis:
                    self._add_colorbar_widget(cbar)
            self._position_colorbars()

    def _initialize_base_vtk_elements(self):
        if self.vis_config['use_multi_volume']:
            try:
                # vtkMultiVolume class available only in vtk >= 8.2.0
                self.vtk_volume = vtk.vtkMultiVolume()
            except:
                self.vtk_volume = vtk.vtkVolume()
                self.vis_config['use_multi_volume'] = False
        else:
            self.vtk_volume = vtk.vtkVolume()
        self.vtk_volume_mapper = vtk.vtkGPUVolumeRayCastMapper()
        self.vtk_volume_mapper.UseJitteringOn()
        self.vtk_volume.SetMapper(self.vtk_volume_mapper)
        self.renderer = vtk.vtkRenderer()
        self.renderer.AddVolume(self.vtk_volume)
        self.window = vtk.vtkRenderWindow()
        self.window.SetSize(*self._window_size)
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

    def _make_timestep_render(self, timestep, ts_is_index=True):
        if ts_is_index:
            self.current_time_step = self.available_time_steps[timestep]
        else:
            if timestep not in self.available_time_steps:
                raise ValueError(
                    'Time step {} is not available.'.format(timestep))
            self.current_time_step = timestep
        self._render_volumes(self.current_time_step)
        self._render_species(self.current_time_step)
        self.draw_colorbars()
        self._scale_actors()
        self._setup_cube_axes_and_bbox()
        self._setup_camera()

    def _render_volumes(self, timestep):
        if self.vis_config['use_multi_volume']:
            self._load_data_into_multi_volume(self.current_time_step)
        else:
            self._load_data_into_single_volume(self.current_time_step)

    def _load_data_into_single_volume(self, timestep):
        vtk_volume_prop = self._get_single_volume_properties(timestep)
        vtk_data_import = self._import_single_volume_data(timestep)
        # Setup mapper
        self.vtk_volume_mapper.SetInputConnection(
            vtk_data_import.GetOutputPort())
        self.vtk_volume_mapper.Update()
        # Add to volume
        self.vtk_volume.SetProperty(vtk_volume_prop)

    def _get_single_volume_properties(self, timestep):
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

    def _import_single_volume_data(self, timestep):
        # Get data
        volume_data_list = list()
        for vol_field in self.volume_field_list:
            volume_data_list.append(vol_field.get_data(timestep))
        self._data_all_volumes = np.concatenate(
            [aux[..., np.newaxis] for aux in volume_data_list], axis=3)
        ax_data = self.volume_field_list[0].get_axes_data(timestep)
        ax_origin = ax_data[0]
        ax_spacing = ax_data[1]
        ax_units = ax_data[3]

        # Normalize volume spacing
        ax_spacing, ax_origin = self._normalize_volume_spacing(
            ax_spacing, ax_origin, ax_units)

        # Put data in VTK format
        vtk_data_import = self._create_vtk_image_import(
            self._data_all_volumes, ax_origin, ax_spacing,
            num_comps=len(self.volume_field_list))
        return vtk_data_import

    def _load_data_into_multi_volume(self, timestep):
        # Workaround to fix wrong volume boundaries when a 'vtkMultiVolume' has
        # only a single volume. The fix replaces the 'vtkMultiVolume' for a
        # 'vtkVolume' and then calls '_load_data_into_single_volume'.
        if len(self.volume_field_list) == 1:
            if isinstance(self.vtk_volume, vtk.vtkMultiVolume):
                self.renderer.RemoveVolume(self.vtk_volume)
                self.vtk_volume = vtk.vtkVolume()
                self.renderer.AddVolume(self.vtk_volume)
                self.vtk_volume.SetMapper(self.vtk_volume_mapper)
            return self._load_data_into_single_volume(timestep)
        # If the 'vtkMultiVolume' was replaced by a 'vtkVolume' but now the
        # number of volumes is >1, go back to having a 'vtkMultiVolume'.
        if not isinstance(self.vtk_volume, vtk.vtkMultiVolume):
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
        for vol_field in self.volume_field_list:
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

            # Normalize volume spacing
            ax_data = vol_field.get_axes_data(timestep)
            ax_origin = ax_data[0]
            ax_spacing = ax_data[1]
            ax_units = ax_data[3]
            ax_spacing, ax_origin = self._normalize_volume_spacing(
                ax_spacing, ax_origin, ax_units)

            # Put data in VTK format
            imports_list.append(
                self._create_vtk_image_import(vol_data, ax_origin, ax_spacing))
        return vol_list, imports_list

    def _normalize_volume_spacing(self, ax_spacing, ax_origin, ax_units):
        if self.forced_norm_factor is not None:
            norm_factor = self.forced_norm_factor
        else:
            norm_factor = self._unit_norm_factors[ax_units[0]]
        ax_origin *= norm_factor
        ax_spacing *= norm_factor
        return ax_spacing, ax_origin

    def _create_vtk_image_import(self, volume_data, ax_origin, ax_spacing,
                                 num_comps=1):
        vtk_data_import = vtk.vtkImageImport()
        vtk_data_import.SetImportVoidPointer(volume_data)
        vtk_data_import.SetDataScalarTypeToFloat()
        vtk_data_import.SetNumberOfScalarComponents(num_comps)
        vtk_data_import.SetDataExtent(0, volume_data.shape[2]-1,
                                      0, volume_data.shape[1]-1,
                                      0, volume_data.shape[0]-1)
        vtk_data_import.SetWholeExtent(0, volume_data.shape[2]-1,
                                       0, volume_data.shape[1]-1,
                                       0, volume_data.shape[0]-1)
        vtk_data_import.SetDataSpacing(ax_spacing[0],
                                       ax_spacing[2],
                                       ax_spacing[1])
        # data origin is also changed by the normalization
        vtk_data_import.SetDataOrigin(ax_origin[0], ax_origin[2], ax_origin[1])
        vtk_data_import.Update()
        return vtk_data_import

    def _render_species(self, timestep):
        for species in self.scatter_species_list:
            species.update_data(timestep)

    def _scale_actors(self):
        scale = self.vis_config['axes_scale']
        self.vtk_volume.SetScale(*scale)
        for species in self.scatter_species_list:
            species.get_actor().SetScale(*scale)

    def _setup_cube_axes_and_bbox(self):
        # Determine axes range of all volumes and species
        z_range_all = []
        x_range_all = []
        y_range_all = []
        ax_units_all = []
        for element in self.volume_field_list + self.scatter_species_list:
            el_has_range = False
            if isinstance(element, VolumetricField):
                ax_data = element.get_axes_data(self.current_time_step)
                ax_range = ax_data[2]
                z_range = ax_range[0]
                x_range = ax_range[1]
                y_range = ax_range[2]
                ax_units = ax_data[3]
                el_has_range = True
            elif (isinstance(element, ScatterSpecies) and
                  not element.is_empty(self.current_time_step)):
                z_range, y_range, x_range, ax_units = element.get_data_range(
                    self.current_time_step)
                el_has_range = True
            if el_has_range:
                if len(z_range_all) == 0:
                    z_range_all = z_range
                    x_range_all = x_range
                    y_range_all = y_range
                    ax_units_all = ax_units
                else:
                    z_range_all = [np.min((z_range_all[0], z_range[0])),
                                   np.max((z_range_all[1], z_range[1]))]
                    x_range_all = [np.min((x_range_all[0], x_range[0])),
                                   np.max((x_range_all[1], x_range[1]))]
                    y_range_all = [np.min((y_range_all[0], y_range[0])),
                                   np.max((y_range_all[1], y_range[1]))]
        # Determine bounds in vtk coordinates
        bounds = None
        if len(self.volume_field_list) > 0:
            bounds = np.array(self.vtk_volume.GetBounds())
        for species in self.scatter_species_list:
            if not species.is_empty(self.current_time_step):
                sp_bounds = np.array(species.get_actor().GetBounds())
                if bounds is None:
                    bounds = sp_bounds
                else:
                    bounds[[0, 2, 4]] = np.where(
                        sp_bounds[[0, 2, 4]] < bounds[[0, 2, 4]],
                        sp_bounds[[0, 2, 4]], bounds[[0, 2, 4]])
                    bounds[[1, 3, 5]] = np.where(
                        sp_bounds[[1, 3, 5]] > bounds[[1, 3, 5]],
                        sp_bounds[[1, 3, 5]], bounds[[1, 3, 5]])
        # If there are no bounds (i.e. no data is displayed) hide axes and bbox
        if bounds is None:
            self.show_cube_axes(False)
            self.show_bounding_box(False)
        else:
            bounds = list(bounds)
            self.vtk_cube_axes_edges.SetBounds(bounds)
            self.vtk_cube_axes.SetBounds(bounds)
            self.vtk_cube_axes.SetXTitle('z')
            self.vtk_cube_axes.SetYTitle('y')
            self.vtk_cube_axes.SetZTitle('x')
            self.vtk_cube_axes.SetXAxisRange(z_range_all[0], z_range_all[1])
            self.vtk_cube_axes.SetYAxisRange(y_range_all[0], y_range_all[1])
            self.vtk_cube_axes.SetZAxisRange(x_range_all[0], x_range_all[1])
            self.vtk_cube_axes.SetXUnits(ax_units_all[0])
            self.vtk_cube_axes.SetYUnits(ax_units_all[2])
            self.vtk_cube_axes.SetZUnits(ax_units_all[1])

    def _setup_camera(self):
        self.renderer.ResetCamera()
        self.camera.Zoom(self.camera_props['zoom'])
        if self.camera_props['focus_shift'] is not None:
            focus = np.array(self.camera.GetFocalPoint()) \
                + self.camera_props['focus_shift']
            self.camera.SetFocalPoint(focus[0], focus[1], focus[2])

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

    def _add_colorbar_widget(self, cbar):
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

    def _position_colorbars(self):
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

    def _check_dependencies(self):
        missing_dependencies = []
        if not vtk_installed:
            missing_dependencies.append('vtk')
        if not pyvista_installed:
            missing_dependencies.append('pyvista')
        if len(missing_dependencies) > 0:
            dep_str = ' '.join(missing_dependencies)
            raise ImportError(
                "Missing required dependencies: {}.".format(dep_str) +
                "Install by running " +
                "'python -m pip install {}'.".format(dep_str))

    def _check_qt(self, use_qt):
        if use_qt and not qt_installed:
            warnings.warn(
                "Qt is not installed. Default VTK windows will be used. "
                "Install by running 'python -m pip install pyqt5'.")
            use_qt = False
        return use_qt


class VolumetricField():

    """Class for the volumetric fields to be displayed."""

    def __init__(self, field, cmap='viridis', opacity='auto',
                 gradient_opacity='uniform opaque', vmax=None, vmin=None,
                 xtrim=None, ytrim=None, ztrim=None, resolution=None,
                 max_resolution_3d=None, name_suffix=None):
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
        self.max_resolution_3d = max_resolution_3d
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
            self._update_colorbar(self._loaded_timestep)
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
        return self._get_opacity_instance(self.opacity, timestep=timestep)

    def get_gradient_opacity(self, timestep=None):
        return self._get_opacity_instance(
            self.gradient_opacity, gradient_opacity=True, timestep=timestep)

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

    def get_optimized_opacity(self, time_step, bins=11,
                              gradient_opacity=False):
        if gradient_opacity:
            hist, *_ = self.get_field_data_gradient_histogram(time_step,
                                                              bins=bins)
        else:
            hist, *_ = self.get_field_data_histogram(time_step, bins=bins)
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
            bin_edges = bin_edges[1:]
        if fld_max > 255:
            hist[-2] += hist[-1]
            hist = hist[:-1]
            bin_edges = bin_edges[:-1]
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

    def _load_data(self, timestep, only_metadata=False):
        if self._loaded_timestep != timestep:
            fld_data, fld_md = self.field.get_data(
                timestep, theta=None,
                max_resolution_3d=self.max_resolution_3d)
            fld_data = self._trim_field(fld_data)
            fld_data = self._change_resolution(fld_data)
            min_fld = np.min(fld_data)
            max_fld = np.max(fld_data)
            self._original_data_range = [min_fld, max_fld]
            fld_data = self._normalize_field(fld_data)
            # Make sure the array is contiguous, otherwise this can lead to
            # errors in vtk_data_import.SetImportVoidPointer in some cases when
            # trimming in the y or z planes is applied, or when the array has
            # been rearranged in the FieldReader (such as for HiPACE data).
            self._field_data = np.ascontiguousarray(fld_data)
            self._field_metadata = fld_md
            if not only_metadata:
                self._loaded_timestep = timestep
            if self.cbar is not None:
                self._update_colorbar(timestep)

    def _update_colorbar(self, timestep):
        cbar_range = np.array(self.get_range(timestep))
        self.vtk_cmap.ResetAnnotations()
        max_val = np.max(np.abs(cbar_range))
        try:
            ord = int(np.log10(max_val))  # get order of magnitude
        except:
            ord = 1
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
        title = self.get_name()
        units_str = ''
        if order_str != '':
            units_str += order_str + '\n'
        units_str += self.get_field_units()
        if units_str != '':
            title += '\n[' + units_str + ']'
        self.cbar.SetTitle(title)

    def _get_opacity_instance(self, opacity, gradient_opacity=False,
                              timestep=None):
        if not isinstance(opacity, Opacity):
            # Check if opacity is a path to a file
            if opacity.endswith('.h5'):
                if os.path.exists(opacity):
                    opacity = Opacity(file_path=opacity)
                else:
                    raise ValueError('Cannot find specified opacity file'
                                     ' {}.'.format(opacity))
            # If it's not 'auto', it should be one of the available opacities
            elif opacity != 'auto':
                if self.style_handler.opacity_exists(opacity):
                    opacity = self.style_handler.get_opacity(opacity)
                else:
                    raise ValueError(
                        "Opacity '{}' does not exist.".format(opacity))
            else:
                opacity = self.get_optimized_opacity(
                    timestep, gradient_opacity=gradient_opacity)
        return opacity

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
        if np.abs(max_value-min_value) > 0:
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


class ScatterSpecies():

    """Class for the particle species to be displayed"""

    def __init__(self, species, color='w', cmap='viridis',  vmax=None,
                 vmin=None, xtrim=None, ytrim=None, ztrim=None, size=1,
                 color_according_to=None, scale_with_charge=False,
                 unit_norm_factors=None, forced_norm_factor=None,
                 name_suffix=None):
        self.species = species
        self.color = color
        self.cmap = cmap
        self.vmax = vmax
        self.vmin = vmin
        self.xtrim = xtrim
        self.ytrim = ytrim
        self.ztrim = ztrim
        self.size = size
        self.color_according_to = color_according_to
        self.scale_with_charge = scale_with_charge
        self._unit_norm_factors = unit_norm_factors
        self.forced_norm_factor = forced_norm_factor
        self.name_suffix = name_suffix
        self._setup_vtk_elements()
        self._current_timestep = None
        self._current_color_variable = None
        self._current_scaling_with_charge = None
        self._current_forced_colormap_range = [vmin, vmax]

    def get_name(self):
        sp_name = self.species.species_name
        if self.name_suffix is not None:
            sp_name += ' ({})'.format(self.name_suffix)
        return sp_name

    def get_actor(self):
        return self.species_actor

    def get_colorbar(self, n_ticks):
        self.cbar_ticks = n_ticks
        return self.cbar

    def is_empty(self, timestep):
        part_data = self._get_data(timestep)
        data_arr = part_data[0]
        if len(data_arr) == 0:
            return True
        else:
            return False

    def get_data_range(self, timestep):
        part_data = self._get_data(timestep)
        data_arr = part_data[0]
        data_units = part_data[3]
        if len(data_arr) > 0:
            z_arr = data_arr[:, 0]
            y_arr = data_arr[:, 1]
            x_arr = data_arr[:, 2]
            z_range = [np.min(z_arr), np.max(z_arr)]
            y_range = [np.min(y_arr), np.max(y_arr)]
            x_range = [np.min(x_arr), np.max(x_arr)]
        else:
            z_range = None
            y_range = None
            x_range = None
        return z_range, y_range, x_range, data_units

    def update_data(self, timestep):
        # Get data
        (data_arr, color_arr, scale_arr, data_units, update_data, update_color,
         update_scale) = self._get_data(timestep)
        if update_data:
            if self.forced_norm_factor is not None:
                norm_factor = self.forced_norm_factor
            else:
                norm_factor = self._unit_norm_factors[data_units[0]]
            data_arr *= norm_factor
            # Create vtkPolyData
            self.poly_data = pv.PolyData(data_arr)
            self.map.SetInputData(self.poly_data)
        if update_color and self.color_according_to is not None:
            self._normalize_color_variable(color_arr)
            self.poly_data.point_data['color'] = color_arr
        if update_scale and self.scale_with_charge:
            self._normalize_scale(scale_arr, max_size=self.size * 0.02)
            self.poly_data.point_data['scale'] = scale_arr

    def set_scale_with_charge(self, value):
        self.scale_with_charge = value
        self._set_mapper_scaling()

    def get_scale_with_charge(self):
        return self.scale_with_charge

    def set_color_according_to(self, var):
        self.color_according_to = var
        self._set_mapper_color_mode()

    def get_color_according_to(self):
        return self.color_according_to

    def get_color(self):
        return self.color

    def set_color(self, color):
        if isinstance(color, str):
            r, g, b = self.style_handler.get_mpl_color_rgb(color)
        elif isinstance(color, list):
            r, g, b = color
        self.species_actor.GetProperty().SetColor(r, g, b)
        self.color = color

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
        self._set_vtk_colormap()

    def get_colormap_range(self):
        color_var = self.color_according_to
        if color_var is not None and color_var in self._timestep_data:
            color_arr = self._timestep_data[color_var][0]
            color_arr_range = [np.min(color_arr), np.max(color_arr)]
            vmin, vmax = self._get_colorbar_range(color_arr_range)
        else:
            warnings.warn('Colormap data not yet specified or loaded.'
                          ' Range values might not be accurate.',
                          RuntimeWarning)
            vmin = self.vmin
            vmax = self.vmax
        return vmin, vmax

    def set_colormap_range(self, vmin=None, vmax=None):
        self.vmin = vmin
        self.vmax = vmax

    def get_size(self):
        return self.size

    def set_size(self, size):
        self.size = size
        if self.scale_with_charge and self._current_timestep is not None:
            part_data = self._get_data(self._current_timestep)
            scale_arr = part_data[2]
            self._normalize_scale(scale_arr, max_size=self.size * 0.02)
            self.poly_data.point_data['scale'] = scale_arr
        else:
            self.map.SetRadius(self.size * 0.02)

    def get_current_timestep(self):
        return self._current_timestep

    def _setup_vtk_elements(self):
        self.vtk_cmap = vtk.vtkColorTransferFunction()
        self.map = vtk.vtkOpenGLSphereMapper()
        self.map.SetLookupTable(self.vtk_cmap)
        self.species_actor = vtk.vtkActor()
        self.species_actor.SetMapper(self.map)
        self.style_handler = VolumeStyleHandler()
        self.set_color(self.color)
        self._create_colorbar()
        self._set_vtk_colormap()
        self._set_mapper_scaling()
        self._set_mapper_color_mode()

    def _create_colorbar(self):
        self.cbar = vtk.vtkScalarBarActor()
        self.cbar.SetLookupTable(self.vtk_cmap)
        self.cbar.DrawTickLabelsOff()
        self.cbar.AnnotationTextScalingOn()
        self.cbar.GetAnnotationTextProperty().SetFontSize(6)
        self.cbar.GetTitleTextProperty().SetFontSize(6)
        self.cbar.SetTextPositionToPrecedeScalarBar()

    def _set_vtk_colormap(self):
        cmap = self.get_colormap()
        fld_val, r_val, g_val, b_val = cmap.get_cmap_values()
        points = list(np.column_stack((fld_val, r_val, g_val, b_val)).flat)
        self.vtk_cmap.RemoveAllPoints()
        self.vtk_cmap.FillFromDataPointer(int(len(points)/4), points)

    def _set_mapper_scaling(self):
        if self.scale_with_charge:
            self.map.SetScaleArray('scale')
        else:
            self.map.SetScaleArray(None)
            self.map.SetRadius(self.size * 0.02)

    def _set_mapper_color_mode(self):
        if self.color_according_to is not None:
            self.map.SetScalarVisibility(True)
            self.map.SetScalarModeToUsePointFieldData()
            self.map.SelectColorArray('color')
        else:
            self.map.SetScalarVisibility(False)
            self.map.SetScalarModeToDefault()

    def _get_data(self, timestep):
        # Determine components to read
        comp_to_read = []
        color_var = self.color_according_to
        scale_var = 'q'
        update_data = self._current_timestep != timestep
        update_color = (update_data or
                        color_var != self._current_color_variable)
        update_scale = (
            update_data or
            self.scale_with_charge != self._current_scaling_with_charge
        )
        if update_data:
            comp_to_read += ['x', 'y', 'z']
            self._current_timestep = timestep
        if update_color:
            self._current_color_variable = color_var
        if update_scale:
            self._current_scaling_with_charge = self.scale_with_charge
        if (update_color and
            color_var is not None and
                color_var not in comp_to_read):
            comp_to_read.append(color_var)
        if (update_scale and
            self.scale_with_charge and
                scale_var not in comp_to_read):
            comp_to_read.append(scale_var)
        # Read data
        if len(comp_to_read) > 0:
            data = self.species.get_data(timestep, comp_to_read)
            if update_data:
                self._timestep_data = data
            elif update_color:
                self._timestep_data[color_var] = data[color_var]
            elif update_scale:
                self._timestep_data[scale_var] = data[scale_var]
        # Create particle array
        x_arr = self._timestep_data['x'][0]
        y_arr = self._timestep_data['y'][0]
        z_arr = self._timestep_data['z'][0]
        part_arr = np.vstack((z_arr, y_arr, x_arr)).T
        # Create color array and update colorbar
        if color_var is not None:
            # Make copy of array to prevent modifying stored data in any way
            color_arr = np.array(self._timestep_data[color_var][0])
            color_arr = color_arr.astype(np.float32, copy=False)
            cmap_range_changed = (self._current_forced_colormap_range !=
                                  [self.vmin, self.vmax])
            # Make it true now also if the range has been changed
            update_color = update_color or cmap_range_changed
            if update_color:
                color_var_units = self._timestep_data[color_var][1]['units']
                if len(color_arr) > 0:
                    color_var_range = [np.min(color_arr), np.max(color_arr)]
                else:
                    color_var_range = [0, 1]
                self._update_colorbar(color_var, color_var_units,
                                      color_var_range)
        else:
            color_arr = np.array([])
        # Create scale array
        if self.scale_with_charge:
            scale_arr = np.abs(self._timestep_data[scale_var][0])
            scale_arr = scale_arr.astype(np.float32, copy=False)
        else:
            scale_arr = np.array([])
        # Trim distribution
        metadata = self._timestep_data['x'][1]
        if any(el is not None for el in [self.xtrim, self.ytrim, self.ztrim]):
            part_arr, color_arr, scale_arr = self._trim_particle_distribution(
                part_arr, color_arr, scale_arr, metadata)
        # Get data units
        data_units = [self._timestep_data['z'][1]['units'],
                      self._timestep_data['y'][1]['units'],
                      self._timestep_data['x'][1]['units']]
        # Return data
        return (part_arr, color_arr, scale_arr, data_units, update_data,
                update_color, update_scale)

    def _trim_particle_distribution(self, part_arr, color_arr, scale_arr,
                                    metadata):
        sim_grid_size = metadata['grid']['size']
        sim_grid_range = metadata['grid']['range']
        z_arr = part_arr[:, 0]
        y_arr = part_arr[:, 1]
        x_arr = part_arr[:, 2]
        if sim_grid_size is not None:
            if len(sim_grid_size) == 2:
                z_range, r_range = sim_grid_range
                x_range = [-r_range[1], r_range[1]]
                y_range = x_range
            elif len(sim_grid_size) == 3:
                z_range, x_range, y_range = sim_grid_range
        else:
            warnings.warn('Could not determine dimesions of simulation box.'
                          'Range of trimming will be determined from maximum'
                          'extension of particle distribution.',
                          RuntimeWarning)
            z_range = [np.min(z_arr), np.max(z_arr)]
            y_range = [np.min(y_arr), np.max(y_arr)]
            x_range = [np.min(x_arr), np.max(x_arr)]
        elements_to_keep = np.ones_like(x_arr)
        if self.xtrim is not None:
            x_trim_range = self._determine_trimming_range(self.xtrim, x_range)
            elements_to_keep = np.where((x_arr > x_trim_range[0]) &
                                        (x_arr < x_trim_range[1]),
                                        elements_to_keep, 0)
        if self.ytrim is not None:
            y_trim_range = self._determine_trimming_range(self.ytrim, y_range)
            elements_to_keep = np.where((y_arr > y_trim_range[0]) &
                                        (y_arr < y_trim_range[1]),
                                        elements_to_keep, 0)
        if self.ztrim is not None:
            z_trim_range = self._determine_trimming_range(self.ztrim, z_range)
            elements_to_keep = np.where((z_arr > z_trim_range[0]) &
                                        (z_arr < z_trim_range[1]),
                                        elements_to_keep, 0)
        elements_to_keep = np.array(elements_to_keep, dtype=bool)
        part_arr = part_arr[elements_to_keep]
        if self.color_according_to is not None:
            color_arr = color_arr[elements_to_keep]
        if self.scale_with_charge:
            scale_arr = scale_arr[elements_to_keep]
        return part_arr, color_arr, scale_arr

    def _determine_trimming_range(self, x_trim, x_range):
        x_trim_norm = np.array(x_trim)
        x_min, x_max = x_range
        a = 2 / (x_max - x_min)
        b = -1 - 2*x_min / (x_max - x_min)
        x_trim_real = (x_trim_norm - b) / a
        return x_trim_real

    def _normalize_color_variable(self, part_data):
        if len(part_data) > 0:
            if self.vmax is None:
                max_value = np.max(part_data)
            else:
                max_value = self.vmax
            if self.vmin is None:
                min_value = np.min(part_data)
            else:
                min_value = self.vmin
            part_data -= min_value
            if np.abs(max_value-min_value) > 0:
                part_data *= 255 / (max_value-min_value)

    def _normalize_scale(self, part_data, max_size):
        if len(part_data) > 0:
            max_value = np.max(part_data)
            min_value = np.min(part_data)
            part_data -= min_value
            if np.abs(max_value-min_value) > 0:
                part_data *= max_size / (max_value-min_value)

    def _update_colorbar(self, var_name, var_units, var_range):
        self.vtk_cmap.ResetAnnotations()
        cbar_range = self._get_colorbar_range(var_range)
        max_val = np.max(np.abs(cbar_range))
        try:
            ord = int(np.log10(max_val))  # get order of magnitude
        except:
            ord = 1
        cbar_range = cbar_range/10**ord
        norm_var_vals = np.linspace(0, 255, self.cbar_ticks)
        real_var_vals = np.linspace(
            cbar_range[0], cbar_range[1], self.cbar_ticks)
        for j in np.arange(self.cbar_ticks):
            self.vtk_cmap.SetAnnotation(norm_var_vals[j],
                                        format(real_var_vals[j], '.2f'))
        if ord != 0:
            order_str = '10^' + str(ord) + ' '
        else:
            order_str = ''
        title = var_name + '\n['
        if order_str != '':
            title += order_str + '\n'
        title += var_units + ']'
        self.cbar.SetTitle(title)

    def _get_colorbar_range(self, original_range):
        if (self.vmin is None) or (self.vmax is None):
            vmin, vmax = original_range
        if self.vmin is not None:
            vmin = self.vmin
        if self.vmax is not None:
            vmax = self.vmax
        return np.array([vmin, vmax])
