# -*- coding: utf-8 -*-

#Copyright 2016-2018 Angel Ferran Pousa, DESY
#
#This file is part of VisualPIC.
#
#VisualPIC is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#VisualPIC is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with VisualPIC.  If not, see <http://www.gnu.org/licenses/>.

import os
from pkg_resources import resource_filename

import numpy as np
from h5py import File as H5File
import vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class Visualizer3Dvtk():
    def __init__(self, dataContainer):
        self.dataContainer = dataContainer
        self.load_available_3d_fields()
        self.volume_list = list()
        self.vtk_volume = vtk.vtkVolume()
        self.volume_color_window = 1
        self.volume_color_level = 0.5
        self.render_quality = "Auto"
        self.render_quality_options = {"Auto": 0, "Low": 0.2, "Medium": 0.05,
                                       "High": 0.02, "Ultra": 0.005}
        self.background_color_options = {"Black": (0, 0, 0),
                                         "White": (1, 1, 1),
                                         "Custom": (-1, -1, -1)}
        self.background_color = "Black"
        self.display_logo = True
        self.display_axes = True
        self.axes_interactive = False
        self.display_cbars = False
        self.scalar_bar_widgets_list = list()
        self.update_cbars = True
        self.current_time_step = -1

    def load_available_3d_fields(self):
        self.available_fields = list()
        species_list = self.dataContainer.GetAvailableSpecies()
        domainFields = self.dataContainer.GetAvailableDomainFields()
        for species in species_list:
            for field in species.GetAvailableFields():
                #if field.GetFieldDimension() == "3D":
                self.available_fields.append(field)
        for field in domainFields:
            #if field.GetFieldDimension() == "3D":
            self.available_fields.append(field)

    def get_list_of_available_3d_fields(self):
        names_list = list()
        for field in self.available_fields:
            names_list.append({"field_name": field.GetName(),
                               "species_name": field.GetSpeciesName()})
        return names_list

    def get_time_steps(self):
        i = 0
        time_steps = np.array([])
        for volume in self.volume_list:
            if i == 0:
                time_steps = volume.get_time_steps()
            else :
                time_steps = np.intersect1d(time_steps, volume.get_time_steps())
            i += 1
        return time_steps

    def get_vtk_widget(self, parent_widget):
        # create widget and references to renderer and interactor
        self.vtk_widget = QVTKRenderWindowInteractor(parent_widget)
        self.renderer = vtk.vtkRenderer()
        self.set_renderer_background(self.background_color)
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        self.interactor.Initialize()
        self.vtk_camera = self.renderer.GetActiveCamera()
        # add widgets
        self.add_axes_widget()
        self.add_visualpic_logo()
        # set default interaction style
        self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
        return self.vtk_widget

    def add_axes_widget(self):
        self.vtk_axes = vtk.vtkAxesActor()
        self.vtk_axes.SetXAxisLabelText("Z")
        self.vtk_axes.SetZAxisLabelText("X")
        self.vtk_orientation_marker = vtk.vtkOrientationMarkerWidget()
        self.vtk_orientation_marker.SetOutlineColor(1, 1, 1)
        self.vtk_orientation_marker.SetOrientationMarker(self.vtk_axes)
        self.vtk_orientation_marker.SetInteractor(self.interactor)
        self.vtk_orientation_marker.SetViewport(0, 0, 0.2, 0.2)
        self.set_axes_widget_visibility(self.display_axes)
        self.set_axes_widget_interactive(self.axes_interactive)

    def add_visualpic_logo(self):
        self.vtk_image_data = vtk.vtkImageData()
        self.logo_path = resource_filename(
                'VisualPIC.Icons', 'logo_horizontal_text_only_no_transp.png')
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
        self.set_logo_widget_visibility(self.display_logo)

    def set_colorbar_visibility(self, value):
        self.display_cbars = value
        if self.current_time_step != -1:
            self.create_colorbars(self.current_time_step)
        if not value:
            self.remove_colorbars()

    def set_axes_widget_interactive(self, value):
        self.axes_interactive = value
        if self.display_axes:
            if value:
                self.vtk_orientation_marker.InteractiveOn()
            else:
                self.vtk_orientation_marker.InteractiveOff()

    def set_logo_widget_visibility(self, value):
        self.display_logo = value
        if value:
            self.vtk_logo_widget.On()
        else:
            self.vtk_logo_widget.Off()

    def get_logo_visibility(self):
        return self.display_logo

    def set_axes_widget_visibility(self, value):
        self.display_axes = value
        self.vtk_orientation_marker.SetEnabled(value)
        if value:
            self.set_axes_widget_interactive(self.axes_interactive)

    def get_axes_visibility(self):
        return self.display_axes

    def get_current_background_color_option(self):
        return self.background_color

    def get_renderer_background_color_options(self):
        return [*self.background_color_options]

    def set_renderer_background(self, option, r=None, g=None, b=None):
        self.background_color = option
        if option == "Custom":
            self.background_color_options[option] = (r, g, b)
        r, g, b = self.background_color_options[option]
        self.renderer.SetBackground(r,g,b)

    def add_volume_field(self, field_name, species_name):
        # maximum volume number is 4, only add if this limit is not reached
        if len(self.volume_list) < 4:
            if species_name == "":
                for volume in self.volume_list:
                    # do not add volume if already in list
                    if (volume.get_field_name() == field_name):
                        return False
                new_volume = Volume3D(
                    self.dataContainer.GetDomainField(field_name))
            else:
                for volume in self.volume_list:
                    # do not add volume if already in list
                    if ((volume.get_field_name() == field_name
                        and volume.get_species_name() == species_name)):
                        return False
                new_volume = Volume3D(
                    self.dataContainer.GetSpeciesField(species_name, field_name))
            # add volume to list
            self.volume_list.append(new_volume)
            self.update_cbars = True
            return True
        else:
            return False

    def remove_volume_from_name(self, field_name, species_name):
        for volume in self.volume_list:
            if ((volume.get_field_name() == field_name)
                and (volume.get_species_name() == species_name)):
                i = self.volume_list.index(volume)
                self.volume_list.remove(volume)
                if i < len(self.scalar_bar_widgets_list):
                    self.scalar_bar_widgets_list.pop(i)
                self.update_cbars = True
                return

    def remove_volume(self, volume):
        i = self.volume_list.index(volume)
        self.volume_list.remove(volume)
        if i < len(self.scalar_bar_widgets_list):
            self.scalar_bar_widgets_list.pop(i)
        self.update_cbars = True

    def get_volume_field(self, field_name, species_name):
        for volume in self.volume_list:
            if ((volume.name == field_name)
                and (volume.species_name == species_name)):
                return volume

    def create_volume(self, time_step):
        # Get data
        npdatauchar = list()
        vtk_volume_prop = vtk.vtkVolumeProperty()
        vtk_volume_prop.IndependentComponentsOn()
        vtk_volume_prop.SetInterpolationTypeToLinear()
        for i, volume in enumerate(self.volume_list):
            npdatauchar.append(volume.get_data(time_step, 200, 300, 0.5))
            vtk_volume_prop.SetColor(i,volume.vtk_color)
            vtk_volume_prop.SetScalarOpacity(i,volume.vtk_opacity)
            vtk_volume_prop.ShadeOff(i)
        npdatamulti = np.concatenate([aux[...,np.newaxis]
                                      for aux in npdatauchar], axis=3)
        axes = self.volume_list[0].get_axes(time_step)
        axes_spacing = self.volume_list[0].get_axes_spacing(time_step, 200,
                                                            300, 0.5)
        # Normalize spacing. Too small values lead to ghost volumes.
        max_sp = max(axes_spacing["x"], axes_spacing["y"], axes_spacing["z"])
        # Too big cells turn opaque, too small become transparent. 
        # max_cell_size normalizes the cell size
        max_cell_size = 0.1 
        norm_factor = max_cell_size/max_sp
        axes_spacing["x"] = axes_spacing["x"]*norm_factor
        axes_spacing["y"] = axes_spacing["y"]*norm_factor
        axes_spacing["z"] = axes_spacing["z"]*norm_factor
        # Put data in VTK format
        vtk_data_import = vtk.vtkImageImport()
        vtk_data_import.SetImportVoidPointer(npdatamulti)
        vtk_data_import.SetDataScalarTypeToUnsignedChar()
        vtk_data_import.SetNumberOfScalarComponents(len(self.volume_list))
        vtk_data_import.SetDataExtent(0, npdatamulti.shape[2]-1,
                                      0, npdatamulti.shape[1]-1,
                                      0, npdatamulti.shape[0]-1)
        vtk_data_import.SetWholeExtent(0, npdatamulti.shape[2]-1,
                                       0, npdatamulti.shape[1]-1,
                                       0, npdatamulti.shape[0]-1)
        vtk_data_import.SetDataSpacing(axes_spacing["x"],
                                       axes_spacing["y"],
                                       axes_spacing["z"])
        # data origin is also changed by the normalization
        vtk_data_import.SetDataOrigin(axes["x"][0]*norm_factor,
                                      axes["y"][0]*norm_factor,
                                      axes["z"][0]*norm_factor)
        vtk_data_import.Update()
        # Create the mapper
        vtk_volume_mapper = vtk.vtkGPUVolumeRayCastMapper()
        vtk_volume_mapper.SetInputConnection(vtk_data_import.GetOutputPort())
        vtk_volume_mapper.Update()
        # Add to volume
        self.vtk_volume.SetMapper(vtk_volume_mapper)
        self.vtk_volume.SetProperty(vtk_volume_prop)
        # Set visualization parameters
        self.set_render_quality(self.render_quality)
        self.set_color_level(self.volume_color_level)
        self.set_color_window(self.volume_color_window)
        # Add to render
        self.renderer.AddVolume(self.vtk_volume)
        self.renderer.ResetCamera()
        self.interactor.Render()
        #self.renderer.GetRenderWindow().Render()
        #self.interactor.Initialize()

    def create_colorbars(self, time_step, update_data=True, update_position=True):
        n_vol = len(self.volume_list)
        if n_vol > 0:
            min_x = 0.05
            max_x = 0.95
            min_y = 0.9
            max_y = 0.95
            pos1 = (min_x, min_y)
            pos2 = (max_x-min_x, max_y-min_y)
            sep = 0.025
            tot_height = max_y - min_y
            tot_width = max_x - min_x
            max_an = 10
            min_an = 3
            # test colorbar
            n_bar = len(self.scalar_bar_widgets_list)
            an = int(min_an + (max_an-min_an)/(2*n_vol))
            for i in np.arange(n_vol):
                if update_data:
                    # Get lookup table and set annotations
                    lut = self.volume_list[i].get_color_transfer_function()
                    lut.ResetAnnotations()
                    fld_n, fld_r = self.volume_list[i].get_norm_and_real_field_range(time_step, an)
                    m = np.max(np.abs(fld_r)) # get order of magnitude
                    ord = int(np.log10(m))
                    fld_r = fld_r/10**ord
                    for j in np.arange(an):
                        lut.SetAnnotation(fld_n[j], format(fld_r[j], '.2f'))
                    if ord != 0:
                        order_str = "10^" + str(ord) + " "
                    else:
                        order_str = ""
                    # Create colorbars
                    if i > n_bar-1:
                        scalar_bar = vtk.vtkScalarBarActor()
                        scalar_bar.SetOrientationToHorizontal()
                        scalar_bar.SetLookupTable(lut)
                        scalar_bar.SetTitle(self.volume_list[i].get_field_name()+ " ["
                                            + order_str
                                            + self.volume_list[i].get_field_units()
                                            + "]")
                        scalar_bar.SetTextPositionToPrecedeScalarBar()
                        scalar_bar.DrawTickLabelsOff()
                        scalar_bar.AnnotationTextScalingOn()
                        scalar_bar.GetAnnotationTextProperty().SetFontSize(8) 
                        scalar_bar_widget = vtk.vtkScalarBarWidget()
                        scalar_bar_widget.SetInteractor(self.interactor)
                        scalar_bar_widget.SetScalarBarActor(scalar_bar)
                        scalar_bar_widget.On()
                        self.scalar_bar_widgets_list.append(scalar_bar_widget)
                # Resize and position colorbars
                if update_position:
                    wid_w = (tot_width - (n_vol-1)*sep) / n_vol
                    y_1 = min_y
                    x_1 = min_x + i*(wid_w+sep)
                    y_2 = tot_height
                    x_2 = wid_w
                    self.scalar_bar_widgets_list[i].GetRepresentation().SetOrientation(0)
                    self.scalar_bar_widgets_list[i].GetRepresentation().GetPositionCoordinate().SetValue(x_1, y_1)
                    self.scalar_bar_widgets_list[i].GetRepresentation().GetPosition2Coordinate().SetValue(x_2, y_2)
            self.update_cbars = False
            #self.update_render()

    def remove_colorbars(self):
        for cbar in reversed(self.scalar_bar_widgets_list):
            self.scalar_bar_widgets_list.remove(cbar)

    def set_render_quality(self, str_value):
        self.render_quality = str_value
        mapper = self.vtk_volume.GetMapper()
        if mapper is not None:
            val = self.render_quality_options[str_value]
            if str_value == "Auto":
                mapper.SetAutoAdjustSampleDistances(1)
            else:
                mapper.SetAutoAdjustSampleDistances(0)
                mapper.SetSampleDistance(val)

    def get_render_quality_options(self):
        return [*self.render_quality_options]

    def get_current_render_quality(self):
        return self.render_quality

    def set_color_level(self, value):
        self.volume_color_level = value
        mapper = self.vtk_volume.GetMapper()
        if mapper is not None:
            mapper.SetFinalColorLevel(self.volume_color_level)

    def get_color_level(self):
        return self.volume_color_level

    def set_color_window(self, value):
        self.volume_color_window = value
        mapper = self.vtk_volume.GetMapper()
        if mapper is not None:
            mapper.SetFinalColorWindow(self.volume_color_window)

    def get_color_window(self):
        return self.volume_color_window

    def make_render(self, time_step):
        self.create_volume(time_step)
        #self.renderer.ResetCamera()
        #self.interactor.Render()
        if self.display_cbars:
            self.create_colorbars(time_step, update_position=self.update_cbars)
            self.interactor.Render()
        self.current_time_step = time_step

    def update_render(self):
        self.interactor.Render()

    def save_screenshot(self, path):
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(self.vtk_widget.GetRenderWindow())
        w2if.Update()
 
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(path + ".png")
        writer.SetInputData(w2if.GetOutput())
        writer.Write()


class Volume3D():
    def __init__(self, field3D):
        self.actor_type = "Volume"
        self.name = field3D.GetName()
        self.species_name = field3D.GetSpeciesName()
        self.field = field3D
        self.vtk_opacity = vtk.vtkPiecewiseFunction()
        self.vtk_color = vtk.vtkColorTransferFunction()
        self.cmap_handler = ColormapHandler()
        self.custom_cmap_range = False
        self.cmap_range_has_changed = False
        self.current_time_step = -1
        self.set_default_style()

    def set_default_style(self):
        default_op = "linear positive"
        self.set_opacity_from_presets(default_op)

        default_cmap = "brg"
        self.set_cmap_from_presets(default_cmap)

    def set_opacity_from_presets(self, op_name):
        if self.cmap_handler.opacity_exists(op_name):
            opacity = self.cmap_handler.get_opacity(op_name)
        else:
            avail_ops = self.cmap_handler.get_available_opacities()
            opacity = self.cmap_handler.get_opacity(avail_ops[0])
        fld_val, op_val = opacity.get_opacity()
        self.set_opacity(fld_val, op_val)

    def set_cmap_from_presets(self, cmap_name):
        if self.cmap_handler.cmap_exists(cmap_name):
            cmap = self.cmap_handler.get_cmap(cmap_name)
        else:
            avail_cmaps = self.cmap_handler.get_available_cmaps()
            cmap = self.cmap_handler.get_cmap(avail_cmaps[0])
        fld_val, r_val, g_val, b_val = cmap.get_cmap()
        self.set_cmap(fld_val, r_val, g_val, b_val)

    def get_optimized_opacity(self, time_step):
        nel = 11
        fld_data = self.get_data(time_step)
        hist, hist_edges = np.histogram(fld_data, bins=nel)
        hist = np.ma.log(hist).filled(0)
        fld_val = np.linspace(0, 255, nel)
        op_val = 1 - hist/hist.max()
        return fld_val, op_val

    def get_field_name(self):
        return self.field.GetName()

    def get_field_histogram(self, time_step, bins=64):
        fld_data = self.get_data(time_step)
        hist, hist_edges = np.histogram(fld_data, bins=bins)
        hist = np.ma.log(hist).filled(0)
        return hist/hist.max(), hist_edges

    def get_field_range(self, time_step, nels):
        self.load_field_data(time_step)
        return np.linspace(self.min_range, self.max_range, nels)

    def get_norm_and_real_field_range(self, time_step, nels):
        self.load_field_data(time_step)
        return (np.linspace(0, 255, nels),
                np.linspace(self.min_range, self.max_range, nels))

    def get_field_units(self):
        return self.field.GetDataISUnits()

    def get_species_name(self):
        return self.field.GetSpeciesName()

    def get_time_steps(self):
        return self.field.GetTimeSteps()

    def set_cmap(self, fld_val, r_val, g_val, b_val):
        # points = [x0, r0, g0, b0, x1, r1, g1, b1, ..., xN, rN, gN, bN]
        self.vtk_color.RemoveAllPoints()
        points = list(np.column_stack((fld_val, r_val, g_val, b_val)).flat)
        self.vtk_color.FillFromDataPointer(int(len(points)/4), points)

    def set_opacity(self, field_values, opacity_values):
        self.vtk_opacity.RemoveAllPoints()
        for i in np.arange(len(field_values)):
            self.vtk_opacity.AddPoint(field_values[i], opacity_values[i])

    def set_cmap_range(self, min, max):
        self.max_range = max
        self.min_range = min
        self.custom_cmap_range = True
        self.cmap_range_has_changed = True

    def get_cmap_values(self):
        fld_val = list()
        r_val = list()
        g_val = list()
        b_val = list()
        size = self.vtk_color.GetSize()
        for i in range(size):
            val = [1,1,1,1,1,1]
            self.vtk_color.GetNodeValue(i, val)
            fld_val.append(val[0])
            r_val.append(val[1])
            g_val.append(val[2])
            b_val.append(val[3])
        return (np.array(fld_val), np.array(r_val), np.array(g_val),
                np.array(b_val))

    def get_opacity_values(self):
        fld_values = list()
        op_values = list()
        size = self.vtk_opacity.GetSize()
        for i in range(size):
            val = [1,1,1,1]
            self.vtk_opacity.GetNodeValue(i, val)
            fld_values.append(val[0])
            op_values.append(val[1])
        return np.array(fld_values), np.array(op_values)

    def get_data(self, time_step, transv_el = None, lon_el = None, fraction = 1):
        self.load_field_data(time_step, transv_el, lon_el, fraction)
        max_value = self.max_range
        min_value = self.min_range
        norm_data = np.round(255 * (self.fieldData-min_value)/(max_value-min_value))
        norm_data[norm_data < 0] = 0
        norm_data[norm_data > 255] = 255
        # Change data from float to unsigned char
        npdatauchar = np.array(norm_data, dtype=np.uint8)
        return npdatauchar

    def load_field_data(self, time_step, transv_el = None, lon_el = None,
                        fraction = 1):
        if not self.is_data_loaded(time_step):
            if self.field.GetFieldDimension() == "3D":
                self.fieldData = self.field.GetAllFieldDataInOriginalUnits(time_step)
            if self.field.GetFieldDimension() == "2D":
                self.fieldData = self.field.Get3DFieldFrom2DSliceInOriginalUnits(
                    time_step, transv_el, lon_el, fraction)
            if not self.custom_cmap_range:
                self.max_range = np.amax(self.fieldData)
                self.min_range = np.amin(self.fieldData)
            else:
                self.cmap_range_has_changed = False
            self.current_time_step = time_step

    def is_data_loaded(self, time_step):
        return (self.current_time_step == time_step
                and not self.cmap_range_has_changed)

    def get_axes(self, time_step):
        axes = {}
        if self.field.GetFieldDimension() == "3D":
            axes["z"] = self.field.GetAxisDataInOriginalUnits("z", time_step)
        if self.field.GetFieldDimension() == "2D":
            axes["z"] = self.field.GetAxisDataInOriginalUnits("y", time_step)
        axes["y"] = self.field.GetAxisDataInOriginalUnits("y", time_step)
        axes["x"] = self.field.GetAxisDataInOriginalUnits("x", time_step)
        return axes

    def get_axes_spacing(self, time_step, transv_el = None, lon_el = None,
                       fraction = 1):
        # TODO: implement number of elements and fraction in 3D
        spacing = {}
        axes = self.get_axes(time_step)
        if self.field.GetFieldDimension() == "3D":
            spacing["x"] = np.abs(axes["x"][1]-axes["x"][0])
            spacing["y"] = np.abs(axes["y"][1]-axes["y"][0])
            spacing["z"] = np.abs(axes["z"][1]-axes["z"][0])
        if self.field.GetFieldDimension() == "2D":
            spacing["x"] = np.abs(axes["x"][-1]-axes["x"][0])/lon_el
            spacing["y"] = np.abs(axes["y"][-1]-axes["y"][0])/transv_el*fraction
            spacing["z"] = np.abs(axes["y"][-1]-axes["y"][0])/transv_el*fraction
        return spacing

    def get_color_transfer_function(self):
        return self.vtk_color


class ColormapHandler():
    """Defines a colormap handler as singleton"""
    cmap_instance = None
    
    def __init__(self, *args, **kwargs):
        if ColormapHandler.cmap_instance is None:
            ColormapHandler.cmap_instance = ColormapHandler.__ColormapHandler()

    def __getattr__(self, name):
        return getattr(self.cmap_instance, name)

    class __ColormapHandler():
        def __init__(self, *args, **kwargs):
            self.max_len = 50
            self.opacity_folder_path = resource_filename(
                'VisualPIC.Assets.Visualizer3D.Opacities', '')
            self.cmaps_folder_path = resource_filename(
                'VisualPIC.Assets.Visualizer3D.Colormaps', '')
            self.initialize_available_opacities()
            self.initialize_available_cmaps()
            return super().__init__(*args, **kwargs)

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
            op = Opacity("")
            op.name = "linear positive"
            op.fld_data = np.linspace(0, 255, n_points)
            op.op_data = np.linspace(0, 0.999, n_points)
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
                    return op.get_opacity()

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
    def __init__(self, file_path, *args, **kwargs):
        self.file_path = file_path
        self.name = None
        self.op_data = None
        self.fld_data = None
        return super().__init__(*args, **kwargs)

    def get_name(self):
        if self.name is None:
            file = self.get_file()
            self.name = file.attrs["opacity_name"]
        return self.name

    def get_opacity(self):
        if self.op_data is None:
            file = self.get_file()
            self.op_data = np.array(file["/opacity"])
            self.fld_data = np.array(file["/field"])
        return self.fld_data, self.op_data
        
    def get_file(self):
            file = H5File(self.file_path, "r")
            return file


class Colormap():
    def __init__(self, file_path, *args, **kwargs):
        self.file_path = file_path
        self.name = None
        self.r_data = None
        self.g_data = None
        self.b_data = None
        self.fld_data = None
        return super().__init__(*args, **kwargs)

    def get_name(self):
        if self.name is None:
            file = self.get_file()
            self.name = file.attrs["cmap_name"]
        return self.name

    def get_cmap(self):
        if self.fld_data is None:
            file = self.get_file()
            self.r_data = np.array(file["/r"])
            self.g_data = np.array(file["/g"])
            self.b_data = np.array(file["/b"])
            self.fld_data = np.array(file["/field"])
        return self.fld_data, self.r_data, self.g_data, self.b_data
        
    def get_file(self):
            file = H5File(self.file_path, "r")
            return file
