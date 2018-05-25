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


class Volume3D():
    def __init__(self, field3D):
        self.actorType = "Volume"
        self.name = field3D.GetName()
        self.speciesName = field3D.GetSpeciesName()
        self.field = field3D
        self.opacity = vtk.vtkPiecewiseFunction()
        self.color = vtk.vtkColorTransferFunction()
        self.vtk_volume = vtk.vtkVolume()
        self.cmap_handler = ColormapHandler()
        self.customCMapRange = False
        self._SetDefaultStyle()

    def _SetDefaultStyle(self):
        self._set_default_opacity()
        
        self.color.AddRGBPoint(0.0,0, 0, 1)
        self.color.AddRGBPoint(100, 1.000,0, 0)
        self.color.AddRGBPoint(255, 0, 1.0, 0)

    def _set_default_opacity(self):
        default_op = "linear positive"
        name, fld_val, op_val = self.cmap_handler.read_opacity(default_op)
        self.SetOpacityValues(fld_val, op_val)

    def GetFieldName(self):
        return self.field.GetName()

    def GetSpeciesName(self):
        return self.field.GetSpeciesName()

    def GetTimeSteps(self):
        return self.field.GetTimeSteps()

    def SetColorPoints(self, points):
        # points = [x0, r0, g0, b0, x1, r1, g1, b1, ..., xN, rN, gN, bN]
        self.color.RemoveAllPoints()
        self.color.FillFromDataPointer(int(len(points)/4), points)
        
    def SetOpacityPoints(self, points):
        self.opacity.RemoveAllPoints()
        self.opacity.FillFromDataPointer(int(len(points)/2), points)

    def SetOpacityValue(self, index, valueX, valueY):
        self.opacity.SetNodeValue(index, [valueX, valueY, 0.5, 0.0])

    def SetOpacityValues(self, field_values, opacity_values):
        self.opacity.RemoveAllPoints()
        for i in np.arange(len(field_values)):
            self.opacity.AddPoint(field_values[i], opacity_values[i])
            #self.SetOpacityValue(i, point[0], point[1])

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
        size = self.opacity.GetSize()
        for i in range(size):
            val = [1,1,1,1]
            self.opacity.GetNodeValue(i, val)
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


class ColormapHandler():
    """Defines a colormap handler as singleton"""
    class __ColormapHandler():
        def __init__(self, *args, **kwargs):
            self.max_len = 50
            self.opacity_folder_path = resource_filename(
                'VisualPIC.Assets.Visualizer3D.Opacities', '' )
            return super().__init__(*args, **kwargs)

        def get_available_opacities(self):
            files_in_folder = os.listdir(self.opacity_folder_path)
            h5_files = list()
            avail_op = list()
            for file in files_in_folder:
                if file.endswith('.h5'):
                    h5_files.append(file)
            for file in h5_files:
                avail_op.append(self.read_data_name(file, self.opacity_folder_path))
            print(avail_op)

        def save_cmap(self, r, g, b):
            pass

        def save_opacity(self, field_values, opacity_values, name, folder_path):
            if ( field_values.min()>=0 and field_values.max()<=255
                and opacity_values.min()>=0 and opacity_values.max()<=1
                and len(field_values) == len(opacity_values)
                and len(opacity_values) <= self.max_len ):
                file = self.get_h5_file_to_write(name, folder_path)
                opacity_dataset = file.create_dataset(
                    "opacity", data = opacity_values )
                field_dataset = file.create_dataset("field", data = field_values)
                file.attrs["opacity_name"] = name
                file.close()
                return True
            else:
                return False

        def read_data_name(self, file_name, folder_path=None):
            if folder_path == None:
                folder_path = self.opacity_folder_path
            file = self.get_h5_file_to_read(file_name, folder_path)
            name = file.attrs["opacity_name"]
            return name

        def read_opacity(self, file_name, folder_path=None):
            if folder_path == None:
                folder_path = self.opacity_folder_path
            try:
                file = self.get_h5_file_to_read(file_name, folder_path)
                name = file.attrs["opacity_name"]
                opacity_data = np.array(file["/opacity"])
                field_data = np.array(file["/field"])
            except:
                print('File not found, returning fallback opacity.')
                name, field_data, opacity_data = self.create_fallback_opacity()
            return name, field_data, opacity_data

        def get_h5_file_to_write(self, file_name, folder_path):
            file = H5File(self.create_file_path(file_name, folder_path),  "w")
            return file

        def get_h5_file_to_read(self, file_name, folder_path):
            file = H5File(self.create_file_path(file_name, folder_path), "r")
            return file

        def create_file_path(self, file_name, folder_path):
            if not file_name.endswith('.h5'):
                file_name += ".h5"
            file_path = os.path.join(
                folder_path, file_name.replace(' ', '_').lower() )
            return file_path

        def create_fallback_opacity(self):
            name = "linear positive"
            n_points = 11
            field_values = np.linspace(0, 255, n_points)
            opacity_values = np.linspace(0, 1, n_points)
            opacity_values[-1] = opacity_values[-1] - 1e-3
            return name, field_values, opacity_values

    cmap_instance = None

    def __init__(self, *args, **kwargs):
        if ColormapHandler.cmap_instance == None:
            ColormapHandler.cmap_instance = ColormapHandler.__ColormapHandler()

    def __getattr__(self, name):
        return getattr(self.cmap_instance, name)
