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


import abc
from h5py import File as H5File
import numpy as np

from VisualPIC.DataReading.dataReader import DataReader

# Try to import openPMD-viewer (required for openPMD data)
try:
    from opmd_viewer import OpenPMDTimeSeries
    from opmd_viewer.openpmd_timeseries.data_reader.utilities \
        import get_shape as openpmd_get_shape
    from opmd_viewer.openpmd_timeseries.data_reader.field_reader \
        import find_dataset as openpmd_find_dataset
    openpmd_installed = True
except ImportError:
    openpmd_installed = False


class FieldReaderBase(DataReader):
    """Parent class for all FieldReaders"""
    __metaclass__  = abc.ABCMeta
    def __init__(self, location, speciesName, dataName, firstTimeStep):
        DataReader.__init__(self, location, speciesName, dataName)
        self.internalName = ""
        self.fieldDimension = ""
        self.firstTimeStep = firstTimeStep
        self.matrixShape = []
        self.axisUnits = {}
        self.axisData = {}
        self.currentTimeStep = {"Slice-1D":-1, "Slice-2D":-1, "AllData":-1}
        self.data = {"Slice-1D":[], "Slice-2D":[], "AllData":[]}
        self.currentSliceAxis = {"Slice-1D":-1, "Slice-2D":-1}
        self.currentSlicePosition = {"Slice-1D":-1, "Slice-2D":-1}
        self._ReadBasicData()

    def Get1DSlice(self, timeStep, slicePositionX, slicePositionY = None):
        if (timeStep != self.currentTimeStep["Slice-1D"]) or ((slicePositionX, slicePositionY) != self.currentSlicePosition["Slice-1D"]):
            self.currentTimeStep["Slice-1D"] = timeStep
            self.currentSlicePosition["Slice-1D"] = (slicePositionX, slicePositionY)
            self.data["Slice-1D"] = self._Read1DSlice(timeStep, slicePositionX, slicePositionY)
        return self.data["Slice-1D"]

    def Get2DSlice(self, sliceAxis, slicePosition, timeStep):
        if (timeStep != self.currentTimeStep["Slice-2D"]) or (slicePosition != self.currentSlicePosition["Slice-2D"]) or (sliceAxis != self.currentSliceAxis["Slice-2D"]):
            self.currentTimeStep["Slice-2D"] = timeStep
            self.currentSlicePosition["Slice-2D"] = slicePosition
            self.currentSliceAxis["Slice-2D"] = sliceAxis
            self.data["Slice-2D"] = self._Read2DSlice(sliceAxis, slicePosition, timeStep)
        return self.data["Slice-2D"]

    def GetAllFieldData(self, timeStep):
        if timeStep != self.currentTimeStep["AllData"]:
            self.currentTimeStep["AllData"] = timeStep
            self.data["AllData"] = self._ReadAllFieldData(timeStep)
        return self.data["AllData"]

    def GetTime(self, timeStep):
        self._ReadTime(timeStep)
        return self.currentTime

    def GetTimeUnits(self):
        if self.timeUnits == "":
            self._ReadUnits()
        return self.timeUnits

    def GetDataUnits(self):
        if self.dataUnits == "":
            self._ReadUnits()
        return self.dataUnits

    def GetAxisData(self, timeStep):
        self.axisData = self._ReadAxisData(timeStep)
        return self.axisData

    def GetAxisUnits(self):
        if self.dataUnits == "":
            self._ReadUnits()
        return self.axisUnits

    @abc.abstractmethod
    def _ReadBasicData(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _GetMatrixShape(self, file_content):
        raise NotImplementedError

    @abc.abstractmethod
    def _ReadInternalName(self, file_content):
        raise NotImplementedError

    @abc.abstractmethod
    def _DetermineFieldDimension(self, file_content):
        raise NotImplementedError

    @abc.abstractmethod
    def _Read1DSlice(self, timeStep, slicePositionX, slicePositionY = None):
        raise NotImplementedError

    @abc.abstractmethod
    def _Read2DSlice(self, sliceAxis, slicePosition, timeStep):
        raise NotImplementedError

    @abc.abstractmethod
    def _ReadAllFieldData(self, timeStep):
        raise NotImplementedError

    @abc.abstractmethod
    def _ReadAxisData(self, timeStep):
        raise NotImplementedError

    @abc.abstractmethod
    def _ReadTime(self, timeStep):
        raise NotImplementedError


class OsirisFieldReader(FieldReaderBase):
    def __init__(self, location, speciesName, dataName, firstTimeStep):
        FieldReaderBase.__init__(self, location, speciesName, dataName, firstTimeStep)

    def _ReadBasicData(self):
        file_content = self._OpenFile(self.firstTimeStep)
        self._ReadInternalName(file_content)
        self._DetermineFieldDimension(file_content)
        self._GetMatrixShape(file_content)
        self._ReadSimulationProperties(file_content)
        file_content.close()

    def _GetMatrixShape(self, file_content):
        self.matrixShape = file_content.get(self.internalName).shape

    def _ReadInternalName(self, file_content):
        self.internalName = list(file_content.keys())[1]

    def _DetermineFieldDimension(self, file_content):
        if '/AXIS/AXIS3' in file_content:
            self.fieldDimension = "3D"
        else:
            self.fieldDimension = "2D"

    def _Read1DSlice(self, timeStep, slicePositionX, slicePositionY = None):
        # TODO: add support for 3D fields
        file_content = self._OpenFile(timeStep)
        fieldData = file_content[self.internalName]
        if self.fieldDimension == '2D':
            elementsX = self.matrixShape[-2]
            selectedRow = round(elementsX*(float(slicePositionX)/100))
            sliceData = np.array(fieldData[selectedRow])
        elif self.fieldDimension == '3D':
            elementsX = self.matrixShape[-3]
            elementsY = self.matrixShape[-2]
            selectedX = round(elementsX*(float(slicePositionX)/100))
            selectedY = round(elementsY*(float(slicePositionY)/100))
            sliceData = np.array(fieldData[selectedX, selectedY])
        file_content.close()
        return sliceData

    def _Read2DSlice(self, sliceAxis, slicePosition, timeStep):
        file_content = self._OpenFile(timeStep)
        fieldData = file_content[self.internalName]
        elementsX3 = self.matrixShape[-3] # number of elements in the transverse direction
        selectedRow = round(elementsX3*(float(slicePosition)/100))
        sliceData = np.array(fieldData[selectedRow])
        file_content.close()
        return sliceData

    def _ReadAllFieldData(self, timeStep):
        file_content = self._OpenFile(timeStep)
        fieldData = np.array(file_content[self.internalName])
        file_content.close()
        return fieldData

    def _ReadAxisData(self, timeStep):
        file_content = self._OpenFile(timeStep)
        elementsX = self.matrixShape[-1] # number of elements in the longitudinal z direction
        elementsY = self.matrixShape[-2] # number of elements in the transverse y direction
        axisData = {}
        axisData["x"] = np.linspace(file_content.attrs['XMIN'][0], file_content.attrs['XMAX'][0], elementsX)
        axisData["y"] = np.linspace(file_content.attrs['XMIN'][1], file_content.attrs['XMAX'][1], elementsY)
        if self.fieldDimension == "3D":
            elementsZ = self.matrixShape[-3] # number of elements in the transverse x direction
            axisData["z"] = np.linspace(file_content.attrs['XMIN'][2], file_content.attrs['XMAX'][2], elementsZ)
        file_content.close()
        return axisData

    def _ReadTime(self, timeStep):
        file_content = self._OpenFile(timeStep)
        self.currentTime = file_content.attrs["TIME"][0]
        file_content.close()

    def _ReadUnits(self):
        file_content = self._OpenFile(self.firstTimeStep)
        self.axisUnits["x"] = str(list(file_content['/AXIS/AXIS1'].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")
        self.axisUnits["y"] = str(list(file_content['/AXIS/AXIS2'].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")
        self.dataUnits = str(list(file_content[self.internalName].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")
        self.timeUnits = str(file_content.attrs["TIME UNITS"][0])[2:-1].replace("\\\\","\\")
        file_content.close()

    def _ReadSimulationProperties(self, file_content):
        self.grid_resolution = np.array(file_content.attrs['NX'])
        self.grid_size = np.array(file_content.attrs['XMAX']) - np.array(file_content.attrs['XMIN'])
        self.grid_units = str(list(file_content['/AXIS/AXIS1'].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")

    def _OpenFile(self, timeStep):
        fileName = self.dataName + "-"
        if self.speciesName != "":
            fileName += self.speciesName + "-"
        fileName += str(timeStep).zfill(6)
        ending = ".h5"
        file_path = self.location + "/" + fileName + ending
        file_content = H5File(file_path, 'r')
        return file_content


class HiPACEFieldReader(FieldReaderBase):
    def __init__(self, location, speciesName, dataName, firstTimeStep):
        FieldReaderBase.__init__(self, location, speciesName, dataName, firstTimeStep)

    def _ReadBasicData(self):
        file_content = self._OpenFile(self.firstTimeStep)
        self._ReadInternalName(file_content)
        self._DetermineFieldDimension(file_content)
        self._GetMatrixShape(file_content)
        #self._ReadSimulationProperties(file_content)
        file_content.close()

    def _GetMatrixShape(self, file_content):
        self.matrixShape = file_content.get(self.internalName).shape

    def _ReadInternalName(self, file_content):
        self.internalName = list(file_content.keys())[0]

    def _DetermineFieldDimension(self, file_content):
        self.fieldDimension = "3D"

    def _Read1DSlice(self, timeStep, slicePositionX, slicePositionY = None):
        # TODO: add support for 3D fields
        file_content = self._OpenFile(timeStep)
        fieldData = file_content[self.internalName]
        if self.fieldDimension == '2D':
            elementsX = self.matrixShape[-2]
            selectedRow = round(elementsX*(float(slicePositionX)/100))
            sliceData = np.array(fieldData[selectedRow])
        elif self.fieldDimension == '3D':
            elementsX = self.matrixShape[-3]
            elementsY = self.matrixShape[-2]
            selectedX = round(elementsX*(float(slicePositionX)/100))
            selectedY = round(elementsY*(float(slicePositionY)/100))
            sliceData = np.array(fieldData[selectedX, selectedY])
        file_content.close()
        return sliceData

    def _Read2DSlice(self, sliceAxis, slicePosition, timeStep):
        file_content = self._OpenFile(timeStep)
        fieldData = file_content[self.internalName]
        elementsX3 = self.matrixShape[2] # number of elements in the transverse direction
        selectedRow = round(elementsX3*(float(slicePosition)/100))
        sliceData = np.array(fieldData[:,:,selectedRow]).T
        file_content.close()
        return sliceData

    def _ReadAllFieldData(self, timeStep):
        file_content = self._OpenFile(timeStep)
        fieldData = np.array(file_content[self.internalName])
        file_content.close()
        return fieldData

    def _ReadAxisData(self, timeStep):
        file_content = self._OpenFile(timeStep)
        elementsX = self.matrixShape[-1] # number of elements in the longitudinal z direction
        elementsY = self.matrixShape[-2] # number of elements in the transverse y direction
        axisData = {}
        axisData["x"] = np.linspace(file_content.attrs['XMIN'][0], file_content.attrs['XMAX'][0], elementsX)
        axisData["y"] = np.linspace(file_content.attrs['XMIN'][1], file_content.attrs['XMAX'][1], elementsY)
        if self.fieldDimension == "3D":
            elementsZ = self.matrixShape[-3] # number of elements in the transverse x direction
            axisData["z"] = np.linspace(file_content.attrs['XMIN'][2], file_content.attrs['XMAX'][2], elementsZ)
        file_content.close()
        return axisData

    def _ReadTime(self, timeStep):
        file_content = self._OpenFile(timeStep)
        self.currentTime = file_content.attrs["TIME"][0]
        file_content.close()

    def _ReadUnits(self):
        # No units information is currently stored by HiPACE
        if self.speciesName != "":
            self.dataUnits = 'e \omega_p^3/ c^3'
        elif self.dataName == 'Ez':
            self.dataUnits = 'm_e c \omega_p e^{-1}'
        else:
            self.dataUnits = 'unknown'
        self.timeUnits = '1/ \omega_p'
        self.axisUnits["x"] = 'c/ \omega_p'
        self.axisUnits["y"] = 'c/ \omega_p'
        self.axisUnits["z"] = 'c/ \omega_p'

    def _ReadSimulationProperties(self, file_content):
        self.grid_resolution = np.array(file_content.attrs['NX'])
        self.grid_size = np.array(file_content.attrs['XMAX']) - np.array(file_content.attrs['XMIN'])
        self.grid_units = str(list(file_content['/AXIS/AXIS1'].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")

    def _OpenFile(self, timeStep):
        if self.speciesName != "":
            fileName = 'density_' + self.speciesName #+ '_' + self.dataName
        else:
            fileName = 'field_' + self.dataName

        fileName += '_' + str(timeStep).zfill(6) + '.0'
        ending = ".h5"
        file_path = self.location + "/" + fileName + ending
        file_content = H5File(file_path, 'r')
        return file_content


class OpenPMDFieldReader(FieldReaderBase):
    def __init__(self, location, speciesName, dataName, firstTimeStep ):
        # First check whether openPMD is installed
        if not openpmd_installed:
            raise RunTimeError("You need to install openPMD-viewer, e.g. with:\n"
                "pip install openPMD-viewer")
        # Store an openPMD timeseries object
        # (Its API is used in order to conveniently extract data from the file)
        self.openpmd_ts = OpenPMDTimeSeries( location, check_all_files=False )
        self.openpmd_dataName = dataName
        # Initialize the instance
        FieldReaderBase.__init__(self, location, speciesName, dataName, firstTimeStep)

    def _ReadBasicData(self):
        file_content = self._OpenFile(self.firstTimeStep)
        self._ReadInternalName(file_content)
        self._DetermineFieldDimension(file_content)
        self._GetMatrixShape(file_content)
        self._ReadSimulationProperties(file_content)
        file_content.close()

    def _GetMatrixShape(self, file_content):
        _, dataset = openpmd_find_dataset( file_content, self.internalName )
        self.matrixShape = openpmd_get_shape( dataset )

    def _ReadInternalName(self, file_content):
        self.internalName = self.openpmd_dataName

    def _DetermineFieldDimension(self, file_content):
        # Find the name of the field ; vector fields like E are encoded as "E/x"
        fieldname = self.internalName.split("/")[0]
        geometry = self.openpmd_ts.fields_metadata[fieldname]['geometry']
        if geometry == '3dcartesian':
            self.fieldDimension = "3D"
        elif geometry == '2dcartesian':
            self.fieldDimension = "2D"
        else:
            raise ValueError("Unsupported geometry: %s" %geometry)

    def _Read1DSlice(self, timeStep, slicePositionX, slicePositionY = None):
        # Find the name of the field ; vector fields like E are encoded as "E/x"
        field_and_coord = self.internalName.split("/")
        if self.fieldDimension == '2D':
            fieldData, _ = self.openpmd_ts.get_field(
                                *field_and_coord, iteration=timeStep )
            elementsX = self.matrixShape[-2]
            selectedRow = round(elementsX*(float(slicePositionX)/100))
            sliceData = np.array(fieldData[selectedRow])
        elif self.fieldDimension == '3D':
            # Slice first along X
            fieldData = self._Read2DSlice( None, slicePositionX, timeStep )
            # Then slice along Y
            elementsY = self.matrixShape[-2]
            selectedY = round(elementsY*(float(slicePositionY)/100))
            sliceData = np.array(fieldData[selectedY])
        return sliceData

    def _Read2DSlice(self, sliceAxis, slicePosition, timeStep):
        # Find the name of the field ; vector fields like E are encoded as "E/x"
        field_and_coord = self.internalName.split("/")
        # Convert the `slicePosition` from a 0-to-100 number to -1 to 1
        slicing = -1. + 2*slicePosition/100.
        # Extract the slice
        sliceData, _ = self.openpmd_ts.get_field(
                *field_and_coord, iteration=timeStep,
                slicing_dir="x", slicing=slicing )
        return sliceData

    def _ReadAllFieldData(self, timeStep):
        # Find the name of the field ; vector fields like E are encoded as "E/x"
        field_and_coord = self.internalName.split("/")
        fieldData, _ = self.openpmd_ts.get_field(
                        *field_and_coord, iteration=timeStep, slicing=None )
        return fieldData

    def _ReadAxisData(self, timeStep):
        # Find the name of the field ; vector fields like E are encoded as "E/x"
        field_and_coord = self.internalName.split("/")
        # Note: the code below has very bad performance because
        # it automatically reads the field data, just to extract the metadata
        # TODO: improve in the future
        _, field_meta_data = self.openpmd_ts.get_field( *field_and_coord,
                                    iteration=timeStep, slicing=None )
        # Construct the `axisData` from the object `field_meta_data`
        axisData = {}
        axisData["x"] = getattr( field_meta_data, "z" )
        axisData["y"] = getattr( field_meta_data, "x" )
        if self.fieldDimension == "3D":
            axisData["z"] = getattr( field_meta_data, "y" )
        return axisData

    def _ReadTime(self, timeStep):
        # The line below sets the attribute `_current_i` of openpmd_ts
        self.openpmd_ts._find_output( None, timeStep )
        # This sets the corresponding time
        self.currentTime = self.openpmd_ts.t[ self.openpmd_ts._current_i ]

    def _ReadUnits(self):
        file_content = self._OpenFile(self.firstTimeStep)
        # OpenPMD data always provide conversion to SI units
        self.axisUnits["x"] = "m"
        self.axisUnits["y"] = "m"
        self.axisUnits["z"] = "m"
        self.timeUnits = "t"
        self.dataUnits = "arb.u." # TODO find the exact unit; needs navigation in file
        file_content.close()

    def _ReadSimulationProperties(self, file_content):
        # TODO: add the proper resolution
        self.grid_resolution = None
        self.grid_size = None
        self.grid_units = "m"

    def _OpenFile(self, timeStep):
        # The line below sets the attribute `_current_i` of openpmd_ts
        self.openpmd_ts._find_output( None, timeStep )
        # This finds the full path to the corresponding file
        fileName = self.openpmd_ts.h5_files[ self.openpmd_ts._current_i ]
        file_content = H5File(fileName, 'r')
        return file_content
