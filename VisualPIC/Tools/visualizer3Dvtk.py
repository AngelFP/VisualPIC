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
            namesList.append({"fieldName":field.GetName(), "speciesName":field.GetSpeciesName()})
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
        self.vtkWidget = QVTKRenderWindowInteractor(parentWidget)
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0,0,0)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.interactor.Initialize()
        self.vtkCamera = self.renderer.GetActiveCamera()
        return self.vtkWidget

    def AddVolumeField(self, fieldName, speciesName):
        # maximum volume number is 4, only add if this limit is not reached
        if len(self.volumeList) < 4:
            if speciesName == "":
                for volume in self.volumeList:
                    # do not add volume if already in list
                    if (volume.GetFieldName() == fieldName):
                        return False
                new_volume = Volume3D(self.dataContainer.GetDomainField(fieldName))
            else:
                for volume in self.volumeList:
                    # do not add volume if already in list
                    if (volume.GetFieldName() == fieldName) and (volume.GetSpeciesName() == speciesName):
                        return False
                new_volume = Volume3D(self.dataContainer.GetSpeciesField(speciesName, fieldName))
            # add volume to list
            self.volumeList.append(new_volume)
            return True
        else:
            return False

    def RemoveVolumeFromName(self, fieldName, speciesName):
        for volumeField in self.volumeList:
            if (volumeField.GetFieldName() == fieldName) and (volumeField.GetSpeciesName() == speciesName):
                self.volumeList.remove(volumeField)
                return

    def RemoveVolume(self, volume):
        self.volumeList.remove(volume)

    def GetVolumeField(self, fieldName, speciesName):
        for volume in self.volumeList:
            if (volume.name == fieldName) and (volume.speciesName == speciesName):
                return volume

    def create_volume(self, timeStep):
        # Get data
        npdatauchar = list()
        volumeprop = vtk.vtkVolumeProperty()
        volumeprop.IndependentComponentsOn()
        volumeprop.SetInterpolationTypeToLinear()
        for i, volume in enumerate(self.volumeList):
            npdatauchar.append(volume.GetData(timeStep, 200, 300, 0.5)) # limit on elements only applies for 2d case
            volumeprop.SetColor(i,volume.color)
            volumeprop.SetScalarOpacity(i,volume.opacity)
            volumeprop.ShadeOff(i)
        npdatamulti = np.concatenate([aux[...,np.newaxis] for aux in npdatauchar], axis=3)
        axes = self.volumeList[0].GetAxes(timeStep)
        axesSpacing = self.volumeList[0].GetAxesSpacing(timeStep, 200, 300, 0.5) # limit on elements only applies for 2d case
        # Normalize spacing. Too small values lead to ghost volumes.
        max_sp = max(axesSpacing["x"], axesSpacing["y"], axesSpacing["z"])
        max_cell_size = 0.1 # too big cells turn opaque, too small become transparent
        norm_factor = max_cell_size/max_sp
        axesSpacing["x"] = axesSpacing["x"]*norm_factor
        axesSpacing["y"] = axesSpacing["y"]*norm_factor
        axesSpacing["z"] = axesSpacing["z"]*norm_factor
        # Put data in VTK format
        dataImport = vtk.vtkImageImport()
        dataImport.SetImportVoidPointer(npdatamulti)
        dataImport.SetDataScalarTypeToUnsignedChar()
        dataImport.SetNumberOfScalarComponents(len(self.volumeList))
        dataImport.SetDataExtent(0, npdatamulti.shape[2]-1, 0, npdatamulti.shape[1]-1, 0, npdatamulti.shape[0]-1)
        dataImport.SetWholeExtent(0, npdatamulti.shape[2]-1, 0, npdatamulti.shape[1]-1, 0, npdatamulti.shape[0]-1)
        dataImport.SetDataSpacing(axesSpacing["x"],axesSpacing["y"],axesSpacing["z"])
        dataImport.SetDataOrigin(axes["x"][0]*norm_factor,axes["y"][0]*norm_factor,axes["z"][0]*norm_factor) # data origin is changed by the normalization
        dataImport.Update()
        # Create the mapper
        volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
        volumeMapper.SetAutoAdjustSampleDistances(1)
        volumeMapper.SetInputConnection(dataImport.GetOutputPort())
        volumeMapper.Update()
        # Add to volume
        self.volume.SetMapper(volumeMapper)
        self.volume.SetProperty(volumeprop)
        # Add to render
        self.renderer.AddVolume(self.volume)
        self.renderer.ResetCamera()
        self.renderer.GetRenderWindow().Render()
        self.interactor.Initialize()

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
        self._set_default_style()

    def _set_default_style(self):
        default_op = "linear positive"
        self.set_opacity_from_presets(default_op)
        
        self.vtk_color.AddRGBPoint(0.0,0, 0, 1)
        self.vtk_color.AddRGBPoint(100, 1.000,0, 0)
        self.vtk_color.AddRGBPoint(255, 0, 1.0, 0)

    def set_opacity_from_presets(self, op_name):
        if self.cmap_handler.opacity_exists(op_name):
            opacity = self.cmap_handler.get_opacity(op_name)
        else:
            avail_ops = self.cmap_handler.get_available_opacities()
            opacity = self.cmap_handler.get_opacity(avail_ops[0])
        fld_val, op_val = opacity.get_opacity()
        self.set_opacity(fld_val, op_val)

    def GetFieldName(self):
        return self.field.GetName()

    def GetSpeciesName(self):
        return self.field.GetSpeciesName()

    def GetTimeSteps(self):
        return self.field.GetTimeSteps()

    def SetColorPoints(self, points):
        # points = [x0, r0, g0, b0, x1, r1, g1, b1, ..., xN, rN, gN, bN]
        self.vtk_color.RemoveAllPoints()
        self.vtk_color.FillFromDataPointer(int(len(points)/4), points)

    def set_opacity(self, field_values, opacity_values):
        self.vtk_opacity.RemoveAllPoints()
        for i in np.arange(len(field_values)):
            self.vtk_opacity.AddPoint(field_values[i], opacity_values[i])

    def SetCMapRangeFromCurrentTimeStep(self, timeStep):
        fieldData = self.field.GetAllFieldDataInOriginalUnits(timeStep)
        self.SetCMapRange(np.amin(fieldData), np.amax(fieldData))

    def SetCMapRange(self, min, max):
        self.maxRange = max
        self.minRange = min
        self.customCMapRange = True

    def GetOpacityValues(self):
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
        if self.field.GetFieldDimension() == "3D":
            fieldData = self.field.GetAllFieldDataInOriginalUnits(timeStep)
        if self.field.GetFieldDimension() == "2D":
            fieldData = self.field.Get3DFieldFrom2DSliceInOriginalUnits(timeStep, transvEl, longEl, fraction)
        if self.customCMapRange:
            maxvalue = self.maxRange
            minvalue = self.minRange
        else:
            maxvalue = np.amax(fieldData)
            minvalue = np.amin(fieldData)
        fieldData = np.round(255 * (fieldData-minvalue)/(maxvalue-minvalue))
        fieldData[fieldData < 0] = 0
        fieldData[fieldData > 255] = 255
        # Change data from float to unsigned char
        npdatauchar = np.array(fieldData, dtype=np.uint8)
        return npdatauchar

    def GetAxes(self, timeStep):
        axes = {}
        if self.field.GetFieldDimension() == "3D":
            axes["z"] = self.field.GetAxisDataInOriginalUnits("z", timeStep)
        if self.field.GetFieldDimension() == "2D":
            axes["z"] = self.field.GetAxisDataInOriginalUnits("y", timeStep)
        axes["y"] = self.field.GetAxisDataInOriginalUnits("y", timeStep)
        axes["x"] = self.field.GetAxisDataInOriginalUnits("x", timeStep)
        return axes

    def GetAxesSpacing(self, timeStep, transvEl = None, longEl = None, fraction = 1):
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
    class __ColormapHandler():
        def __init__(self, *args, **kwargs):
            self.max_len = 50
            self.opacity_folder_path = resource_filename(
                'VisualPIC.Assets.Visualizer3D.Opacities', '' )
            self.initialize_available_opacities()
            return super().__init__(*args, **kwargs)

        def initialize_available_opacities(self):
            self.default_opacities = list()
            self.other_opacities = list()
            folder_opacities = self.get_opacities_in_default_folder()
            if len(folder_opacities) > 0:
                self.default_opacities += self.get_opacities_in_default_folder()
            else:
                self.default_opacities.append(self.create_fallback_opacity())

        def get_opacities_in_default_folder(self):
            files_in_folder = os.listdir(self.opacity_folder_path)
            folder_opacities = list()
            for file in files_in_folder:
                if file.endswith('.h5'):
                    file_path = self.create_file_path(file, self.opacity_folder_path)
                    folder_opacities.append(Opacity(file_path))
            return folder_opacities

        def add_opacity_from_file(self, file_path):
            self.other_opacities.append(Opacity(file_path))

        def get_available_opacities(self):
            ops = list()
            for op in self.default_opacities+self.other_opacities:
                ops.append(op.get_name())
            return ops

        def get_opacity(self, op_name):
            for op in self.default_opacities+self.other_opacities:
                if op.get_name() == op_name:
                    return op

        def get_opacity_data(self, op_name):
            for op in self.default_opacities+self.other_opacities:
                if op.get_name() == op_name:
                    return op.get_opacity()

        def opacity_exists(self, op_name):
            for op in self.default_opacities+self.other_opacities:
                if op.get_name() == op_name:
                    return True
            return False

        def save_cmap(self, r, g, b):
            pass

        def save_opacity(self, name, field_values, opacity_values, folder_path):
            if ( field_values.min()>=0 and field_values.max()<=255
                and opacity_values.min()>=0 and opacity_values.max()<=1
                and len(field_values) == len(opacity_values)
                and len(opacity_values) <= self.max_len ):
                file_path = self.create_file_path(name, folder_path)
                # Create H5 file
                file = H5File(file_path,  "w")
                opacity_dataset = file.create_dataset(
                    "opacity", data = opacity_values )
                field_dataset = file.create_dataset("field", data = field_values)
                file.attrs["opacity_name"] = name
                file.close()
                # Add to available opacities
                opacity = Opacity(file_path)
                if os.path.normpath(folder_path) == self.opacity_folder_path:
                    self.default_opacities.append(opacity)
                else:
                    self.other_opacities.append(opacity)
                return True
            else:
                return False

        def create_file_path(self, file_name, folder_path):
            if not file_name.endswith('.h5'):
                file_name += ".h5"
                file_name = file_name.replace(' ', '_').lower()
            file_path = os.path.join(folder_path, file_name)
            return file_path

        def create_fallback_opacity(self):
            n_points = 11
            op = Opacity("")
            op.name = "linear positive"
            op.fld_data = np.linspace(0, 255, n_points)
            op.op_data = np.linspace(0, 0.999, n_points)
            return op

    cmap_instance = None

    def __init__(self, *args, **kwargs):
        if ColormapHandler.cmap_instance is None:
            ColormapHandler.cmap_instance = ColormapHandler.__ColormapHandler()

    def __getattr__(self, name):
        return getattr(self.cmap_instance, name)


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
