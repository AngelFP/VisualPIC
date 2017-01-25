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

    def GetPossibleAxisUnits(self):
        return self._unitConverter.GetPossibleAxisUnits(self)

    def GetFieldDimension(self):
        return list(self.data.items())[0][1].GetFieldDimension()

    def GetAxisDataInOriginalUnits(self, axis, timeStep):
        return list(self.data.items())[0][1].GetAxisDataInOriginalUnits(axis, timeStep)
        
    def GetAxisOriginalUnits(self):
        return list(self.data.items())[0][1].GetAxisOriginalUnits()


class TransverseWakefield(CustomField):
    # List of necessary fields and simulation parameters.
    necessaryData = {"2D":["Ey", "Bx"],
                     "3D":["Ey", "Bx"]}
    necessaryParameters = []
    units = "V/m"
    ISUnits = True
    standardName = "Transverse Wakefield"

    def GetDataInOriginalUnits(self, timeStep):
        Ey = self.data["Ey"].GetDataInISUnits(timeStep)
        Bx = self.data["Bx"].GetDataInISUnits(timeStep)
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

    def GetDataInOriginalUnits(self, timeStep):
        Ey = self.data["Ey"].GetDataInISUnits(timeStep)
        Ez = self.data["Ez"].GetDataInISUnits(timeStep)
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

    def GetDataInOriginalUnits(self, timeStep):
        Ey = self.data["Ey"].GetDataInISUnits(timeStep)
        Ez = self.data["Ez"].GetDataInISUnits(timeStep)
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

    def GetDataInOriginalUnits(self, timeStep):
        Ey = self.data["Ey"].GetDataInISUnits( timeStep)
        Bx = self.data["Bx"].GetDataInISUnits( timeStep)
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

    def GetDataInOriginalUnits(self, timeStep):
        Bx = self.data["Bx"].GetDataInISUnits( timeStep)
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
                     "3D":[]}
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
                     "3D":[]}
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