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
import numpy as np
from h5py import File as H5File
import vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from pkg_resources import resource_listdir, resource_filename


class Visualizer3Dvtk():
    def __init__(self, dataContainer):
        self.dataContainer = dataContainer
        self._GetAvailable3DFields()
        self.volumeList = list()
        self.volume = vtk.vtkVolume()
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

    def _GetAvailable3DFields(self):
        self.availableFields = list()
        speciesList = self.dataContainer.GetAvailableSpecies()
        domainFields = self.dataContainer.GetAvailableDomainFields()
        for species in speciesList:
            for field in species.GetAvailableFields():
                #if field.GetFieldDimension() == "3D":
                self.availableFields.append(field)
        for field in domainFields:
            #if field.GetFieldDimension() == "3D":
            self.availableFields.append(field)

    def GetListOfAvailable3DFields(self):
        namesList = list()
        for field in self.availableFields:
            namesList.append({"fieldName":field.GetName(),
                              "speciesName":field.GetSpeciesName()})
        return namesList

    def GetTimeSteps(self):
        i = 0
        timeSteps = np.array([0])
        for volume in self.volumeList:
            if i == 0:
                timeSteps = volume.GetTimeSteps()
            else :
                timeSteps = np.intersect1d(timeSteps, volume.GetTimeSteps())
            i+=1
        return timeSteps

    def GetVTKWidget(self, parentWidget):
        # create widget and references to renderer and interactor
        self.vtkWidget = QVTKRenderWindowInteractor(parentWidget)
        self.renderer = vtk.vtkRenderer()
        self.set_renderer_background(self.background_color)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.interactor.Initialize()
        self.vtkCamera = self.renderer.GetActiveCamera()
        # add widgets
        self.add_axes_widget()
        self.add_visualpic_logo()
        # set default interaction style
        self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
        return self.vtkWidget

    def add_axes_widget(self):
        self.vtk_axes = vtk.vtkAxesActor()
        self.vtk_axes.SetXAxisLabelText("Z")
        self.vtk_axes.SetZAxisLabelText("X")
        self.vtk_orientation_marker = vtk.vtkOrientationMarkerWidget()
        self.vtk_orientation_marker.SetOutlineColor(1, 1, 1)
        self.vtk_orientation_marker.SetOrientationMarker(self.vtk_axes)
        self.vtk_orientation_marker.SetInteractor(self.interactor)
        self.vtk_orientation_marker.SetViewport(0.0, 0.0, 0.2, 0.2)
        self.set_axes_widget_visibility(self.display_axes)
        self.set_axes_widget_interactive(self.axes_interactive)

    def add_visualpic_logo(self):
        self.vtk_image_data = vtk.vtkImageData()
        self.logo_path = resource_filename(
                'VisualPIC.Icons', 'logo_horizontal.png' )
        self.vtk_png_reader = vtk.vtkPNGReader()
        self.vtk_png_reader.SetFileName(self.logo_path)
        self.vtk_png_reader.Update()
        self.vtk_image_data = self.vtk_png_reader.GetOutput()
        self.vtk_logo_representation = vtk.vtkLogoRepresentation()
        self.vtk_logo_representation.SetImage(self.vtk_image_data)
        self.vtk_logo_representation.SetPosition(0.79, 0.89)
        self.vtk_logo_representation.SetPosition2(.2, .1)
        self.vtk_logo_representation.GetImageProperty().SetOpacity(1)
        self.vtk_logo_widget = vtk.vtkLogoWidget()
        self.vtk_logo_widget.SetInteractor(self.interactor)
        self.vtk_logo_widget.SetRepresentation(self.vtk_logo_representation)
        self.set_logo_widget_visibility(self.display_logo)

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

    def AddVolumeField(self, fieldName, speciesName):
        # maximum volume number is 4, only add if this limit is not reached
        if len(self.volumeList) < 4:
            if speciesName == "":
                for volume in self.volumeList:
                    # do not add volume if already in list
                    if (volume.GetFieldName() == fieldName):
                        return False
                new_volume = Volume3D(
                    self.dataContainer.GetDomainField(fieldName))
            else:
                for volume in self.volumeList:
                    # do not add volume if already in list
                    if ((volume.GetFieldName() == fieldName
                        and volume.GetSpeciesName() == speciesName)):
                        return False
                new_volume = Volume3D(
                    self.dataContainer.GetSpeciesField(speciesName, fieldName))
            # add volume to list
            self.volumeList.append(new_volume)
            return True
        else:
            return False

    def RemoveVolumeFromName(self, fieldName, speciesName):
        for volumeField in self.volumeList:
            if ((volumeField.GetFieldName() == fieldName)
                and (volumeField.GetSpeciesName() == speciesName)):
                self.volumeList.remove(volumeField)
                return

    def RemoveVolume(self, volume):
        self.volumeList.remove(volume)

    def GetVolumeField(self, fieldName, speciesName):
        for volume in self.volumeList:
            if ((volume.name == fieldName)
                and (volume.speciesName == speciesName)):
                return volume

    def create_volume(self, timeStep):
        # Get data
        npdatauchar = list()
        volumeprop = vtk.vtkVolumeProperty()
        volumeprop.IndependentComponentsOn()
        volumeprop.SetInterpolationTypeToLinear()
        for i, volume in enumerate(self.volumeList):
            npdatauchar.append(volume.GetData(timeStep, 200, 300, 0.5))
            volumeprop.SetColor(i,volume.vtk_color)
            volumeprop.SetScalarOpacity(i,volume.vtk_opacity)
            volumeprop.ShadeOff(i)
        npdatamulti = np.concatenate([aux[...,np.newaxis]
                                      for aux in npdatauchar], axis=3)
        axes = self.volumeList[0].GetAxes(timeStep)
        axesSpacing = self.volumeList[0].GetAxesSpacing(timeStep, 200, 300,
                                                        0.5)
        # Normalize spacing. Too small values lead to ghost volumes.
        max_sp = max(axesSpacing["x"], axesSpacing["y"], axesSpacing["z"])
        # Too big cells turn opaque, too small become transparent. 
        # max_cell_size normalizes the cell size
        max_cell_size = 0.1 
        norm_factor = max_cell_size/max_sp
        axesSpacing["x"] = axesSpacing["x"]*norm_factor
        axesSpacing["y"] = axesSpacing["y"]*norm_factor
        axesSpacing["z"] = axesSpacing["z"]*norm_factor
        # Put data in VTK format
        dataImport = vtk.vtkImageImport()
        dataImport.SetImportVoidPointer(npdatamulti)
        dataImport.SetDataScalarTypeToUnsignedChar()
        dataImport.SetNumberOfScalarComponents(len(self.volumeList))
        dataImport.SetDataExtent(0, npdatamulti.shape[2]-1,
                                 0, npdatamulti.shape[1]-1,
                                 0, npdatamulti.shape[0]-1)
        dataImport.SetWholeExtent(0, npdatamulti.shape[2]-1,
                                  0, npdatamulti.shape[1]-1,
                                  0, npdatamulti.shape[0]-1)
        dataImport.SetDataSpacing(axesSpacing["x"],
                                  axesSpacing["y"],
                                  axesSpacing["z"])
        # data origin is also changed by the normalization
        dataImport.SetDataOrigin(axes["x"][0]*norm_factor,
                                 axes["y"][0]*norm_factor,
                                 axes["z"][0]*norm_factor)
        dataImport.Update()
        # Create the mapper
        volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
        volumeMapper.SetInputConnection(dataImport.GetOutputPort())
        volumeMapper.Update()
        # Add to volume
        self.volume.SetMapper(volumeMapper)
        self.volume.SetProperty(volumeprop)
        # Set visualization parameters
        self.set_render_quality(self.render_quality)
        self.set_color_level(self.volume_color_level)
        self.set_color_window(self.volume_color_window)
        # Add to render
        self.renderer.AddVolume(self.volume)
        self.renderer.ResetCamera()
        self.renderer.GetRenderWindow().Render()
        self.interactor.Initialize()

    def set_render_quality(self, str_value):
        self.render_quality = str_value
        mapper = self.volume.GetMapper()
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
        mapper = self.volume.GetMapper()
        if mapper is not None:
            mapper.SetFinalColorLevel(self.volume_color_level)

    def get_color_level(self):
        return self.volume_color_level

    def set_color_window(self, value):
        self.volume_color_window = value
        mapper = self.volume.GetMapper()
        if mapper is not None:
            mapper.SetFinalColorWindow(self.volume_color_window)

    def get_color_window(self):
        return self.volume_color_window

    def MakeRender(self, timeStep):
        self.create_volume(timeStep)
        #self.CreateVolume(timeStep)

    def UpdateRender(self):
        self.interactor.Render()

    def SaveScreenshot(self, path):
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(self.vtkWidget.GetRenderWindow())
        w2if.Update()
 
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(path + ".png")
        writer.SetInputData(w2if.GetOutput())
        writer.Write()


class Volume3D():
    def __init__(self, field3D):
        self.actorType = "Volume"
        self.name = field3D.GetName()
        self.speciesName = field3D.GetSpeciesName()
        self.field = field3D
        self.vtk_opacity = vtk.vtkPiecewiseFunction()
        self.vtk_color = vtk.vtkColorTransferFunction()
        self.vtk_volume = vtk.vtkVolume()
        self.cmap_handler = ColormapHandler()
        self.customCMapRange = False
        self.cmap_range_has_changed = False
        self.current_time_step = -1
        self._set_default_style()

    def _set_default_style(self):
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

    def GetFieldName(self):
        return self.field.GetName()

    def get_field_histogram(self, time_step, bins = 64):
        fld_data = self.GetData(time_step)
        hist, hist_edges = np.histogram(fld_data, bins=bins)
        hist = np.log(hist)
        return hist/hist.max(), hist_edges

    def get_field_range(self, time_step, nels):
        self.load_field_data(time_step)
        return np.linspace(self.minRange, self.maxRange, nels)

    def get_field_units(self):
        return self.field.GetDataISUnits()

    def GetSpeciesName(self):
        return self.field.GetSpeciesName()

    def GetTimeSteps(self):
        return self.field.GetTimeSteps()

    def SetColorPoints(self, points):
        # points = [x0, r0, g0, b0, x1, r1, g1, b1, ..., xN, rN, gN, bN]
        self.vtk_color.RemoveAllPoints()
        self.vtk_color.FillFromDataPointer(int(len(points)/4), points)

    def set_cmap(self, fld_val, r_val, g_val, b_val):
        self.vtk_color.RemoveAllPoints()
        points = list(np.column_stack((fld_val, r_val, g_val, b_val)).flat)
        self.vtk_color.FillFromDataPointer(int(len(points)/4), points)

    def set_opacity(self, field_values, opacity_values):
        self.vtk_opacity.RemoveAllPoints()
        for i in np.arange(len(field_values)):
            self.vtk_opacity.AddPoint(field_values[i], opacity_values[i])

    def SetCMapRange(self, min, max):
        self.maxRange = max
        self.minRange = min
        self.customCMapRange = True
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

    def GetData(self, timeStep, transvEl = None, longEl = None, fraction = 1):
        self.load_field_data(timeStep, transvEl, longEl, fraction)
        maxvalue = self.maxRange
        minvalue = self.minRange
        norm_data = np.round(255 * (self.fieldData-minvalue)/(maxvalue-minvalue))
        norm_data[norm_data < 0] = 0
        norm_data[norm_data > 255] = 255
        # Change data from float to unsigned char
        npdatauchar = np.array(norm_data, dtype=np.uint8)
        return npdatauchar

    def load_field_data(self, time_step, transvEl = None, longEl = None,
                        fraction = 1):
        if not self.is_data_loaded(time_step):
            if self.field.GetFieldDimension() == "3D":
                self.fieldData = self.field.GetAllFieldDataInOriginalUnits(time_step)
            if self.field.GetFieldDimension() == "2D":
                self.fieldData = self.field.Get3DFieldFrom2DSliceInOriginalUnits(
                    time_step, transvEl, longEl, fraction)
            if not self.customCMapRange:
                self.maxRange = np.amax(self.fieldData)
                self.minRange = np.amin(self.fieldData)
            else:
                self.cmap_range_has_changed = False
            self.current_time_step = time_step

    def is_data_loaded(self, time_step):
        return (self.current_time_step == time_step
                and not self.cmap_range_has_changed)

    def GetAxes(self, timeStep):
        axes = {}
        if self.field.GetFieldDimension() == "3D":
            axes["z"] = self.field.GetAxisDataInOriginalUnits("z", timeStep)
        if self.field.GetFieldDimension() == "2D":
            axes["z"] = self.field.GetAxisDataInOriginalUnits("y", timeStep)
        axes["y"] = self.field.GetAxisDataInOriginalUnits("y", timeStep)
        axes["x"] = self.field.GetAxisDataInOriginalUnits("x", timeStep)
        return axes

    def GetAxesSpacing(self, timeStep, transvEl = None, longEl = None,
                       fraction = 1):
        # TODO: implement number of elements and fraction in 3D
        spacing = {}
        axes = self.GetAxes(timeStep)
        if self.field.GetFieldDimension() == "3D":
            spacing["x"] = np.abs(axes["x"][1]-axes["x"][0])
            spacing["y"] = np.abs(axes["y"][1]-axes["y"][0])
            spacing["z"] = np.abs(axes["z"][1]-axes["z"][0])
        if self.field.GetFieldDimension() == "2D":
            spacing["x"] = np.abs(axes["x"][-1]-axes["x"][0])/longEl
            spacing["y"] = np.abs(axes["y"][-1]-axes["y"][0])/transvEl*fraction
            spacing["z"] = np.abs(axes["y"][-1]-axes["y"][0])/transvEl*fraction
        return spacing


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
                'VisualPIC.Assets.Visualizer3D.Opacities', '' )
            self.cmaps_folder_path = resource_filename(
                'VisualPIC.Assets.Visualizer3D.Colormaps', '' )
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
            for op in self.default_opacities+self.other_opacities:
                ops.append(op.get_name())
            return ops
        
        def opacity_exists(self, op_name):
            for op in self.default_opacities+self.other_opacities:
                if op.get_name() == op_name:
                    return True
            return False

        def get_opacity(self, op_name):
            for op in self.default_opacities+self.other_opacities:
                if op.get_name() == op_name:
                    return op

        def get_opacity_data(self, op_name):
            for op in self.default_opacities+self.other_opacities:
                if op.get_name() == op_name:
                    return op.get_opacity()

        def save_opacity(self, name, field_values, opacity_values,
                         folder_path):
            if (field_values.min()>=0 and field_values.max()<=255
                and opacity_values.min()>=0 and opacity_values.max()<=1
                and len(field_values) == len(opacity_values)
                and len(opacity_values) <= self.max_len):
                file_path = self.create_file_path(name, folder_path)
                # Create H5 file
                file = H5File(file_path,  "w")
                opacity_dataset = file.create_dataset(
                    "opacity", data = opacity_values )
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
            r_1 = np.linspace(0, 1, (n_points+1)/2)
            r_2 = np.linspace(1, 0, (n_points+1)/2)
            cmap.r_data = np.append(np.delete(r_1, -1), r_2)
            cmap.g_data = np.linspace(0, 1, n_points)
            cmap.b_data = np.linspace(1, 0, n_points)
            return cmap

        def get_available_cmaps(self):
            cmaps = list()
            for cmap in self.default_cmaps+self.other_cmaps:
                cmaps.append(cmap.get_name())
            return cmaps
        
        def cmap_exists(self, cmap_name):
            for cmap in self.default_cmaps+self.other_cmaps:
                if cmap.get_name() == cmap_name:
                    return True
            return False

        def get_cmap(self, cmap_name):
            for cmap in self.default_cmaps+self.other_cmaps:
                if cmap.get_name() == cmap_name:
                    return cmap

        def get_cmap_data(self, cmap_name):
            for cmap in self.default_cmaps+self.other_cmaps:
                if cmap.get_name() == cmap_name:
                    return cmap.get_cmap()

        def save_cmap(self, name, fld_val, r_val, g_val, b_val, folder_path):
            if (fld_val.min()>=0 and fld_val.max()<=255
                and r_val.min()>=0 and r_val.max()<=255
                and g_val.min()>=0 and g_val.max()<=255
                and b_val.min()>=0 and b_val.max()<=255
                and len(fld_val) == len(r_val) == len(g_val) == len(b_val)
                and len(fld_val) <= self.max_len):
                file_path = self.create_file_path(name, folder_path)
                # Create H5 file
                file = H5File(file_path,  "w")
                r_dataset = file.create_dataset("r", data = r_val)
                g_dataset = file.create_dataset("g", data = g_val)
                b_dataset = file.create_dataset("b", data = b_val)
                fld_dataset = file.create_dataset("field", data = fld_val)
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
