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
from scipy import interpolate as ip
import math
from VisualPIC.DataHandling.dataElement import DataElement


"""
Base Class for Custom Fields and Raw Data Sets
"""
class CustomDataElement(DataElement):
    # List of necessary fields and simulation parameters.
    necessaryData = {"2D":[],
                     "3D":[]}
    necessaryParameters = []
    units = ""
    ISUnits = True
    standardName = ""

    def __init__(self, dataContainer, speciesName = ''):
        self.c = 299792458 #m/s
        self.e = 1.60217733 * 10**(-19) #C
        self.m_e = 9.1093897 * 10**(-31) #kg
        self.eps_0 = 8.854187817 * 10**(-12) #As/(Vm)
        self.dataContainer = dataContainer
        self.dataStandardName = self.standardName
        self.speciesName = speciesName
        self.hasNonISUnits = not self.ISUnits
        self._SetBaseData()
        self._SetTimeSteps()
        

    def _SetTimeSteps(self):
        i = 0
        for DataName, DataElement in self.data.items():
            if i == 0:
                timeSteps = DataElement.GetTimeSteps()
            else:
                timeSteps = np.intersect1d(timeSteps, DataElement.GetTimeSteps())
        self.timeSteps = timeSteps

    def _SetBaseData(self):
        raise NotImplementedError

    def GetDataOriginalUnits(self):
        return self.units

    def GetTimeInOriginalUnits(self, timeStep):
        return list(self.data.items())[0][1].GetTimeInOriginalUnits(timeStep)

    def GetTimeOriginalUnits(self):
        return list(self.data.items())[0][1].GetTimeOriginalUnits()


"""
Custom Fields
"""
class CustomField(CustomDataElement):
    @classmethod
    def meetsRequirements(cls, dataContainer):
        return ((set(dataContainer.GetAvailableDomainFieldsNames()).issuperset(cls.necessaryData[dataContainer.GetSimulationDimension()])) and (set(dataContainer.GetNamesOfAvailableParameters()).issuperset(cls.necessaryParameters)))

    def _SetBaseData(self):
        dimension = self.dataContainer.GetSimulationDimension()
        self.data = {}
        for FieldName in self.necessaryData[dimension]:
            self.data[FieldName] = self.dataContainer.GetDomainField(FieldName)

    def GetFieldDimension(self):
        return list(self.data.items())[0][1].GetFieldDimension()

    def GetPossibleAxisUnits(self):
        return self._unitConverter.GetPossibleAxisUnits(self)

    def GetAxisDataInOriginalUnits(self, axis, timeStep):
        return list(self.data.items())[0][1].GetAxisDataInOriginalUnits(axis, timeStep)
        
    def GetAxisOriginalUnits(self):
        return list(self.data.items())[0][1].GetAxisOriginalUnits()

    """
    Get data in original units
    """
    def Get1DSliceInOriginalUnits(self, timeStep, slicePositionX, slicePositionY = None):
        fieldData = self.CalculateField(timeStep)
        if self.GetFieldDimension() == '2D':
            elementsX = fieldData.shape[-2]
            selectedRow = round(elementsX*(float(slicePositionX)/100))
            sliceData = fieldData[selectedRow]
        elif self.GetFieldDimension() == '3D':
            elementsX = fieldData.shape[-3]
            elementsY = fieldData.shape[-2]
            selectedX = round(elementsX*(float(slicePositionX)/100))
            selectedY = round(elementsY*(float(slicePositionY)/100))
            sliceData = fieldData[selectedX, selectedY]
        return sliceData

    def Get2DSliceInOriginalUnits(self, sliceAxis, slicePosition, timeStep):
        fieldData = self.CalculateField(timeStep)
        elementsX3 = fieldData.shape[-3]
        selectedRow = round(elementsX3*(float(slicePosition)/100))
        sliceData = fieldData[selectedRow]
        return sliceData

    def GetAllFieldDataInOriginalUnits(self, timeStep):
        return self.CalculateField(timeStep)

    def Get3DFieldFrom2DSliceInOriginalUnits(self, timeStep, transvEl, longEl):
        field2D = self.GetAllFieldDataInOriginalUnits(timeStep)
        nx = field2D.shape[0]
        field2D = field2D[int(nx/2):nx] # we get only half
        cilShape = field2D.shape
        Rin,Zin = np.mgrid[0:cilShape[0], 0:cilShape[1]] # cyl. coordinates of original data
        Zin = np.reshape(Zin, Zin.shape[0]*Zin.shape[1])
        Rin = np.reshape(Rin, Rin.shape[0]*Rin.shape[1])
        field2D = np.reshape(field2D, field2D.shape[0]*field2D.shape[1])
        transvSpacing = cilShape[0]*2/transvEl
        lonSpacing = cilShape[1]/longEl
        field3D = np.zeros((transvEl, transvEl, longEl))
        X, Y, Z = np.mgrid[0:cilShape[0]:transvSpacing,0:cilShape[0]:transvSpacing,0:cilShape[1]:lonSpacing] # cart. coordinates of 3D field
        Rout = np.sqrt(X**2 + Y**2)
        # Fill the field sector by sector (only the first has to be calculated. The rest are simlpy mirrored)
        field3D[int(transvEl/2):transvEl+1,int(transvEl/2):transvEl+1] = ip.griddata(np.column_stack((Rin,Zin)), field2D, (Rout, Z), method='nearest', fill_value = 0) # top right section when looking back from z to the x-y plane.
        field3D[0:int(transvEl/2),int(transvEl/2):transvEl+1] = np.flip(field3D[int(transvEl/2):transvEl+1,int(transvEl/2):transvEl+1], 0)
        field3D[0:int(transvEl/2),0:int(transvEl/2)] = np.flip(field3D[0:int(transvEl/2),int(transvEl/2):transvEl+1], 1)
        field3D[int(transvEl/2):transvEl+1,0:int(transvEl/2)] = np.flip(field3D[int(transvEl/2):transvEl+1,int(transvEl/2):transvEl+1], 1)
        return field3D
    
    """
    Get data in any units
    """
    def Get1DSlice(self, timeStep, units, slicePositionX, slicePositionY = None):
        fieldData = self.CalculateField(timeStep)
        if self.GetFieldDimension() == '2D':
            elementsX = fieldData.shape[-2]
            selectedRow = round(elementsX*(float(slicePositionX)/100))
            sliceData = fieldData[selectedRow]
        elif self.GetFieldDimension() == '3D':
            elementsX = fieldData.shape[-3]
            elementsY = fieldData.shape[-2]
            selectedX = round(elementsX*(float(slicePositionX)/100))
            selectedY = round(elementsY*(float(slicePositionY)/100))
            sliceData = fieldData[selectedX, selectedY]
        return self._unitConverter.GetDataInUnits(self, units, sliceData)

    def Get2DSlice(self, sliceAxis, slicePosition, timeStep, units):
        fieldData = self.CalculateField(timeStep)
        elementsX3 = fieldData.shape[-3]
        selectedRow = round(elementsX3*(float(slicePosition)/100))
        sliceData = fieldData[selectedRow]
        return self._unitConverter.GetDataInUnits(self, units, sliceData)

    def GetAllFieldData(self, timeStep, units):
        fieldData = self.CalculateField(timeStep)
        return self._unitConverter.GetDataInUnits(self, units, fieldData)

    """
    Get data in IS units
    """
    def Get1DSliceISUnits(self, timeStep, slicePositionX, slicePositionY = None):
        fieldData = self.CalculateField(timeStep)
        if self.GetFieldDimension() == '2D':
            elementsX = fieldData.shape[-2]
            selectedRow = round(elementsX*(float(slicePositionX)/100))
            sliceData = fieldData[selectedRow]
        elif self.GetFieldDimension() == '3D':
            elementsX = fieldData.shape[-3]
            elementsY = fieldData.shape[-2]
            selectedX = round(elementsX*(float(slicePositionX)/100))
            selectedY = round(elementsY*(float(slicePositionY)/100))
            sliceData = fieldData[selectedX, selectedY]
        return self._unitConverter.GetDataInISUnits(self, sliceData)

    def Get2DSliceISUnits(self, sliceAxis, slicePosition, timeStep):
        fieldData = self.CalculateField(timeStep)
        elementsX3 = fieldData.shape[-3]
        selectedRow = round(elementsX3*(float(slicePosition)/100))
        sliceData = fieldData[selectedRow]
        return self._unitConverter.GetDataInISUnits(self, sliceData)

    def GetAllFieldDataISUnits(self, timeStep):
        fieldData = self.CalculateField(timeStep)
        return self._unitConverter.GetDataInISUnits(self, fieldData)

    def CalculateField(self, timeStep):
        raise NotImplementedError


class TransverseWakefield(CustomField):
    # List of necessary fields and simulation parameters.
    necessaryData = {"2D":["Ey", "Bx"],
                     "3D":["Ey", "Bx"]}
    necessaryParameters = []
    units = "V/m"
    ISUnits = True
    standardName = "Transverse Wakefield"

    def CalculateField(self, timeStep):
        Ey = self.data["Ey"].GetAllFieldDataISUnits(timeStep)
        Bx = self.data["Bx"].GetAllFieldDataISUnits(timeStep)
        TranvsWF = Ey - self.c*Bx
        return TranvsWF


class LaserIntensityField(CustomField):
    # List of necessary fields and simulation parameters.
    necessaryData = {"2D":["Ey", "Ez"],
                     "3D":["Ex", "Ey", "Ez"]}
    necessaryParameters = ["n_p", "lambda_l"]
    units = "W/m^2"
    ISUnits = True
    standardName = "Laser Intensity"

    def CalculateField(self, timeStep):
        Ey = self.data["Ey"].GetAllFieldDataISUnits(timeStep)
        Ez = self.data["Ez"].GetAllFieldDataISUnits(timeStep)
        n_p = self.dataContainer.GetSimulationParameter("n_p") * 1e24
        w_p = math.sqrt(n_p * (self.e)**2 / (self.m_e * self.eps_0)) #plasma freq (1/s)
        lambda_l = self.dataContainer.GetSimulationParameter("lambda_l") * 1e-9 # laser wavelength (m)
        w_l = 2 * math.pi * self.c / lambda_l # laser angular frequency (rad/sec)
        n = math.sqrt(1-(w_p/w_l)**2) # index of refraction
        E2 = np.square(Ez) + np.square(Ey) # square of electric field modulus
        Intensity = self.c*self.eps_0*n/2*E2
        return Intensity


class NormalizedVectorPotential(CustomField):
    # List of necessary fields and simulation parameters.
    necessaryData = {"2D":["Ey", "Ez"],
                     "3D":["Ex", "Ey", "Ez"]}
    necessaryParameters = ["n_p", "lambda_l"]
    units = "m_e*c^2/e"
    ISUnits = True
    standardName = "Normalized Vector Potential"

    def CalculateField(self, timeStep):
        Ey = self.data["Ey"].GetAllFieldDataISUnits(timeStep)
        Ez = self.data["Ez"].GetAllFieldDataISUnits(timeStep)
        n_p = self.dataContainer.GetSimulationParameter("n_p") * 1e24
        w_p = math.sqrt(n_p * (self.e)**2 / (self.m_e * self.eps_0)) #plasma freq (1/s)
        lambda_l = self.dataContainer.GetSimulationParameter("lambda_l") * 1e-9 # laser wavelength (m)
        w_l = 2 * math.pi * self.c / lambda_l # laser angular frequency (rad/sec)
        n = math.sqrt(1-(w_p/w_l)**2) # index of refraction
        E2 = np.square(Ez) + np.square(Ey) # square of electric field modulus
        Intensity = self.c*self.eps_0*n/2*E2
        a = np.sqrt(7.3e-11 * lambda_l**2 * Intensity) # normalized vector potential
        return a


class TransverseWakefieldSlope(CustomField):
    # List of necessary fields and simulation parameters.
    necessaryData = {"2D":["Ey", "Bx"],
                     "3D":["Ey", "Bx"]}
    necessaryParameters = []
    units = "V/m^2"
    ISUnits = True
    standardName = "Transverse Wakefield Slope"

    def CalculateField(self, timeStep):
        Ey = self.data["Ey"].GetAllFieldDataISUnits( timeStep)
        Bx = self.data["Bx"].GetAllFieldDataISUnits( timeStep)
        TranvsWF = Ey - self.c*Bx
        y = self.data["Ey"].GetAxisInISUnits("y", timeStep)
        dy = abs(y[1]-y[0]) # distance between data points in y direction
        slope = np.gradient(TranvsWF, dy, axis=0)
        return slope


class BxSlope(CustomField):
    # List of necessary fields and simulation parameters.
    necessaryData = {"2D":["Bx"],
                     "3D":["Bx"]}
    necessaryParameters = []
    units = "T/m"
    ISUnits = True
    standardName = "Bx Slope"

    def CalculateField(self, timeStep):
        Bx = self.data["Bx"].GetAllFieldDataISUnits( timeStep)
        y = self.data["Bx"].GetAxisInISUnits("y", timeStep)
        dy = abs(y[1]-y[0]) # distance between data points in y direction
        slope = np.gradient(Bx, dy, axis=0)
        return slope


class CustomFieldCreator:
    customFields = [
        TransverseWakefield,
        TransverseWakefieldSlope,
        LaserIntensityField,
        NormalizedVectorPotential,
        BxSlope
        ]
    @classmethod
    def GetCustomFields(cls, dataContainer):
        fieldList = list()
        for Field in cls.customFields:
            if Field.meetsRequirements(dataContainer):
                fieldList.append(Field(dataContainer))
        return fieldList


"""
Custom Raw Data Sets
"""
class CustomRawDataSet(CustomDataElement):
    @classmethod
    def meetsRequirements(cls, dataContainer, speciesName):
        return ((set(dataContainer.GetSpecies(speciesName).GetRawDataSetsNamesList()).issuperset(cls.necessaryData[dataContainer.GetSimulationDimension()])) and (set(dataContainer.GetNamesOfAvailableParameters()).issuperset(cls.necessaryParameters)))

    def _SetBaseData(self):
        dimension = self.dataContainer.GetSimulationDimension()
        self.data = {}
        for DataSetName in self.necessaryData[dimension]:
            self.data[DataSetName] = self.dataContainer.GetSpecies(self.speciesName).GetRawDataSet(DataSetName)


class xPrimeDataSet(CustomRawDataSet):
    # List of necessary data sets and simulation parameters.
    necessaryData = {"2D":["Px", "Pz"],
                     "3D":["Px", "Pz"]}
    necessaryParameters = []
    units = "rad"
    ISUnits = True
    standardName = "xP"

    def GetDataInOriginalUnits(self, timeStep):
        Px = self.data["Px"].GetDataInISUnits( timeStep)
        Pz = self.data["Pz"].GetDataInISUnits( timeStep)
        xP = np.divide(Px, Pz)
        return xP


class yPrimeDataSet(CustomRawDataSet):
    # List of necessary data sets and simulation parameters.
    necessaryData = {"2D":["Py", "Pz"],
                     "3D":["Py", "Pz"]}
    necessaryParameters = []
    units = "rad"
    ISUnits = True
    standardName = "yP"

    def GetDataInOriginalUnits(self, timeStep):
        Py = self.data["Py"].GetDataInISUnits( timeStep)
        Pz = self.data["Pz"].GetDataInISUnits( timeStep)
        yP = np.divide(Py, Pz)
        return yP

class deltaZPrimeDataSet(CustomRawDataSet):
    # List of necessary data sets and simulation parameters.
    necessaryData = {"2D":["z"],
                     "3D":["z"]}
    necessaryParameters = []
    units = "m"
    ISUnits = True
    standardName = "Δz"

    def GetDataInOriginalUnits(self, timeStep):
        z = self.data["z"].GetDataInISUnits( timeStep)
        meanZ = np.average(z)
        dZ = z-meanZ
        return dZ

class forwardMomentumVariationDataSet(CustomRawDataSet):
    # List of necessary data sets and simulation parameters.
    necessaryData = {"2D":["Pz"],
                     "3D":["Pz"]}
    necessaryParameters = []
    units = "rad"
    ISUnits = True
    standardName = "ΔPz/Pz"

    def GetDataInOriginalUnits(self, timeStep):
        Pz = self.data["Pz"].GetDataInISUnits( timeStep)
        meanPz = np.average(Pz)
        dPz = np.divide(Pz-meanPz, meanPz)
        return dPz

    
class CustomRawDataSetCreator:
    customDataSets = [
        xPrimeDataSet,
        yPrimeDataSet,
        deltaZPrimeDataSet,
        forwardMomentumVariationDataSet
        ]
    @classmethod
    def GetCustomDataSets(cls, dataContainer, speciesName):
        dataSetList = list()
        for dataSet in cls.customDataSets:
            if dataSet.meetsRequirements(dataContainer, speciesName):
                dataSetList.append(dataSet(dataContainer, speciesName))
        return dataSetList