# -*- coding: utf-8 -*-

#Copyright 2016-2017 Angel Ferran Pousa
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

import numpy as np
import vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class VolumeVTK():
    def __init__(self, field3D):
        self.actorType = "Volume"
        self.name = field3D.GetName()
        self.speciesName = field3D.GetSpeciesName()
        self.field = field3D
        self.opacity = vtk.vtkPiecewiseFunction()
        self.color = vtk.vtkColorTransferFunction()
        self._SetDefaultStyle()

    def _SetDefaultStyle(self):
        self.opacity.AddPoint(0, 0.1)
        self.opacity.AddPoint(0.5*255, 0.1)
        self.opacity.AddPoint(255, 0.1)
        
        self.color.AddRGBPoint(0.0,0, 0, 1)
        self.color.AddRGBPoint(100, 1.000,0, 0)
        self.color.AddRGBPoint(255, 0, 1.0, 0)

    def SetColorPoints(self, points):
        # points = [x0, r0, g0, b0, x1, r1, g1, b1, ..., xN, rN, gN, bN]
        self.color.RemoveAllPoints()
        self.color.FillFromDataPointer(int(len(points)/4), points)
        
    def SetOpacityPoints(self, points):
        self.opacity.RemoveAllPoints()
        self.opacity.FillFromDataPointer(int(len(points)/2), points)

    def ChangeStyle(self):
        self.opacity.RemoveAllPoints()
        self.color.RemoveAllPoints()
        
        self.opacity.AddPoint(0, 0.1)
        self.opacity.AddPoint(0.5*255, 0.1)
        self.opacity.AddPoint(255, 0.1)
        
        self.color.AddRGBPoint(0.0, 1, 0, 0)
        self.color.AddRGBPoint(100, 1.000,0, 0)
        self.color.AddRGBPoint(255, 1, 00, 0)

    def GetData(self, timeStep):
        fieldData = np.absolute(self.field.GetAllFieldDataInOriginalUnits(timeStep))
        maxvalue = np.amax(fieldData)

        den1 = 255.0/maxvalue
        fieldData = np.round(den1 * fieldData)

        # Change data from float to unsigned char
        npdatauchar = np.array(fieldData, dtype=np.uint8)
        return npdatauchar

    def GetAxes(self, timeStep):
        axes = {}
        axes["z"] = self.field.GetAxisDataInOriginalUnits("x", timeStep)
        axes["y"] = self.field.GetAxisDataInOriginalUnits("y", timeStep)
        axes["x"] = self.field.GetAxisDataInOriginalUnits("z", timeStep)
        return axes

    def GetAxesSpacing(self, timeStep):
        spacing = {}
        axesz = self.field.GetAxisDataInOriginalUnits("x", timeStep)
        axesy = self.field.GetAxisDataInOriginalUnits("y", timeStep)
        axesx = self.field.GetAxisDataInOriginalUnits("z", timeStep)
        spacing["x"] = np.abs(axesx[1]-axesx[0])
        spacing["y"] = np.abs(axesy[1]-axesy[0])
        spacing["z"] = np.abs(axesz[1]-axesz[0])
        return spacing

class Visualizer3Dvtk():
    def __init__(self, dataContainer):
        self.dataContainer = dataContainer
        self.volumeList = list()

    def GetVTKWidget(self, parentWidget):
        self.vtkWidget = QVTKRenderWindowInteractor(parentWidget)
        self.renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        return self.vtkWidget

    def AddVolumeField(self, fieldName, speciesName = None):
        if speciesName == None:
            pass
        else:
            self.volumeList.append(VolumeVTK(self.dataContainer.GetSpeciesField(speciesName, fieldName)))

    def GetVolumeField(self, fieldName, speciesName):
        for volume in self.volumeList:
            if (volume.name == fieldName) and (volume.speciesName == speciesName):
                return volume

    def _CreateVolume(self, timeStep):
        npdatauchar = list()
        volumeprop = vtk.vtkVolumeProperty()
        volumeprop.IndependentComponentsOn()
        volumeprop.SetInterpolationTypeToLinear()
        for i, volume in enumerate(self.volumeList):
            npdatauchar.append(volume.GetData(timeStep))
            volumeprop.SetColor(i,volume.color)
            volumeprop.SetScalarOpacity(i,volume.opacity)
            volumeprop.ShadeOff(i)
        npdatamulti = np.concatenate([aux[...,np.newaxis] for aux in npdatauchar], axis=3)
        axes = self.volumeList[0].GetAxes(timeStep)
        axesSpacing = self.volumeList[0].GetAxesSpacing(timeStep)

        dataImport = vtk.vtkImageImport()
        dataImport.SetImportVoidPointer(npdatamulti)
        dataImport.SetDataScalarTypeToUnsignedChar()
        dataImport.SetNumberOfScalarComponents(len(self.volumeList))
        # The following two functions describe how the data is stored
        # and the dimensions of the array it is stored in.
        dataImport.SetDataExtent(0, npdatamulti.shape[2]-1, 0, npdatamulti.shape[1]-1, 0, npdatamulti.shape[0]-1)
        dataImport.SetWholeExtent(0, npdatamulti.shape[2]-1, 0, npdatamulti.shape[1]-1, 0, npdatamulti.shape[0]-1)
        dataImport.SetDataSpacing(axesSpacing["z"],axesSpacing["y"],axesSpacing["x"])
        dataImport.SetDataOrigin(axes["z"][0],axes["y"][0],axes["x"][0])
        dataImport.Update()

        # Set the mapper
        mapper = vtk.vtkGPUVolumeRayCastMapper()
        mapper.SetAutoAdjustSampleDistances(1)
        mapper.SetInputConnection(dataImport.GetOutputPort())

        volume = vtk.vtkVolume()
        volume.SetMapper(mapper)
        volume.SetProperty(volumeprop)

        return volume

    def MakeRender(self, timeStep):
        self.renderer.AddVolume(self._CreateVolume(timeStep))
        self.renderer.ResetCamera()
        self.interactor.Initialize()

    def UpdateRender(self):
        self.interactor.Render()


