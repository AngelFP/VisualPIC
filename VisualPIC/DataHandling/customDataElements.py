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
    def __init__(self, standardName, dataContainer, hasNonISUnits = False, speciesName = ''):
        self.c = 299792458 #m/s
        self.e = 1.60217733 * 10**(-19) #C
        self.m_e = 9.1093897 * 10**(-31) #kg
        self.eps_0 = 8.854187817 * 10**(-12) #As/(Vm)
        self.dataContainer = dataContainer
        timeSteps = self._SetTimeSteps()
        return super().__init__(dataContainer.unitConverter, standardName, timeSteps, speciesName, hasNonISUnits)

    def _SetTimeSteps(self, dataContainer):
        raise NotImplementedError

"""
Custom Fields
"""
class CustomField(CustomDataElement):
    # List of necessary fields and simulation parameters.
    necessaryFields = {"2D":[],
                       "3D":[]}
    necessaryParameters = []
    fieldUnits = ""

    @classmethod
    def meetsRequirements(cls, dataContainer):
        return ((set(dataContainer.GetAvailableDomainFieldsNames()).issuperset(cls.necessaryFields[dataContainer.GetSimulationDimension()])) and (set(dataContainer.GetNamesOfAvailableParameters()).issuperset(cls.necessaryParameters)))

    def __init__(self, standardName, dataContainer, hasNonISUnits,  speciesName = ''):
        self._SetBaseFields(dataContainer)
        return super().__init__(standardName, dataContainer, hasNonISUnits, speciesName)

    def _SetBaseFields(self, dataContainer):
        dimension = dataContainer.GetSimulationDimension()
        self.fields = {}
        for FieldName in self.necessaryFields[dimension]:
            self.fields[FieldName] = dataContainer.GetDomainField(FieldName)

    def _SetTimeSteps(self):
        i = 0
        for FieldName, Field in self.fields.items():
            if i == 0:
                timeSteps = Field.GetTimeSteps()
            else:
                timeSteps = np.intersect1d(timeSteps, Field.GetTimeSteps())
        return timeSteps

    def GetPossibleAxisUnits(self):
        return self._unitConverter.GetPossibleAxisUnits(self)

    def GetDataOriginalUnits(self):
        return self.fieldUnits

    def GetTimeInOriginalUnits(self, timeStep):
        return list(self.fields.items())[0][1].GetTimeInOriginalUnits(timeStep)

    def GetTimeOriginalUnits(self):
        return list(self.fields.items())[0][1].GetTimeOriginalUnits()

    def GetFieldDimension(self):
        return list(self.fields.items())[0][1].GetFieldDimension()

    def GetAxisDataInOriginalUnits(self, timeStep):
        return list(self.fields.items())[0][1].GetAxisDataInOriginalUnits(timeStep) #dictionary
        
    def GetAxisOriginalUnits(self):
        return list(self.fields.items())[0][1].GetAxisOriginalUnits()


class TransverseWakefield(CustomField):
    # List of necessary fields and simulation parameters.
    necessaryFields = {"2D":["Ey", "Bx"],
                       "3D":["Ey", "Bx"]}
    necessaryParameters = []
    fieldUnits = "V/m"
    ISUnits = True

    def __init__(self, dataContainer, speciesName = ''):
        standardName = "Transverse Wakefield"
        super().__init__(standardName, dataContainer, not self.ISUnits, speciesName)

    def GetDataInOriginalUnits(self, timeStep):
        Ey = self.fields["Ey"].GetDataInISUnits(timeStep)
        Bx = self.fields["Bx"].GetDataInISUnits(timeStep)
        TranvsWF = Ey - self.c*Bx
        return TranvsWF

class LaserIntensityField(CustomField):
    # List of necessary fields and simulation parameters.
    necessaryFields = {"2D":["Ey", "Ez"],
                       "3D":["Ex", "Ey", "Ez"]}
    necessaryParameters = ["n_p", "lambda_l"]
    fieldUnits = "W/m^2"
    ISUnits = True

    def __init__(self, dataContainer, speciesName = ''):
        standardName = "Laser Intensity"
        super().__init__(standardName, dataContainer, not self.ISUnits, speciesName)

    def GetDataInOriginalUnits(self, timeStep):
        Ey = self.fields["Ey"].GetDataInISUnits(timeStep)
        Ez = self.fields["Ez"].GetDataInISUnits(timeStep)
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
    necessaryFields = {"2D":["Ey", "Ez"],
                       "3D":["Ex", "Ey", "Ez"]}
    necessaryParameters = ["n_p", "lambda_l"]
    fieldUnits = "m_e*c^2/e"
    ISUnits = True

    def __init__(self, dataContainer, speciesName = ''):
        standardName = "Normalized Vector Potential"
        super().__init__(standardName, dataContainer, not self.ISUnits, speciesName)

    def GetDataInOriginalUnits(self, timeStep):
        Ey = self.fields["Ey"].GetDataInISUnits(timeStep)
        Ez = self.fields["Ez"].GetDataInISUnits(timeStep)
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
    necessaryFields = {"2D":["Ey", "Bx"],
                       "3D":["Ey", "Bx"]}
    necessaryParameters = []
    fieldUnits = "V/m^2"
    ISUnits = True

    def __init__(self, dataContainer, speciesName = ''):
        standardName = "Transverse Wakefield Slope"
        super().__init__(standardName, dataContainer, not self.ISUnits, speciesName)

    def GetDataInOriginalUnits(self, timeStep):
        Ey = self.fields["Ey"].GetDataInISUnits( timeStep)
        Bx = self.fields["Bx"].GetDataInISUnits( timeStep)
        TranvsWF = Ey - self.c*Bx
        y = self.fields["Ey"].GetAxisInISUnits("y", timeStep)
        dy = abs(y[1]-y[0]) # distance between data points in y direction
        slope = np.gradient(TranvsWF, dy, axis=0)
        return slope

class CustomFieldCreator:
    customFields = [
        TransverseWakefield,
        TransverseWakefieldSlope,
        LaserIntensityField,
        NormalizedVectorPotential
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
    # List of necessary data sets and simulation parameters.
    necessaryDataSets = {"2D":[],
                       "3D":[]}
    necessaryParameters = []
    units = ""

    @classmethod
    def meetsRequirements(cls, dataContainer, speciesName):
        return ((set(dataContainer.GetSpecies(speciesName).GetRawDataSetsNamesList()).issuperset(cls.necessaryDataSets[dataContainer.GetSimulationDimension()])) and (set(dataContainer.GetNamesOfAvailableParameters()).issuperset(cls.necessaryParameters)))

    def __init__(self, standardName, dataContainer, hasNonISUnits, speciesName):
        self._SetBaseDataSets(dataContainer, speciesName)
        return super().__init__(standardName, dataContainer, hasNonISUnits, speciesName)

    def _SetBaseDataSets(self, dataContainer, speciesName):
        dimension = dataContainer.GetSimulationDimension()
        self.dataSets = {}
        for DataSetName in self.necessaryDataSets[dimension]:
            self.dataSets[DataSetName] = dataContainer.GetSpecies(speciesName).GetRawDataSet(DataSetName)

    def _SetTimeSteps(self):
        i = 0
        for DataSetName, DataSet in self.dataSets.items():
            if i == 0:
                timeSteps = DataSet.GetTimeSteps()
            else:
                timeSteps = np.intersect1d(timeSteps, DataSet.GetTimeSteps())
        return timeSteps

    def GetDataOriginalUnits(self):
        return self.units

    def GetTimeInOriginalUnits(self, timeStep):
        return list(self.dataSets.items())[0][1].GetTimeInOriginalUnits(timeStep)

    def GetTimeOriginalUnits(self):
        return list(self.dataSets.items())[0][1].GetTimeOriginalUnits()

class xPrimeDataSet(CustomRawDataSet):
    # List of necessary data sets and simulation parameters.
    necessaryDataSets = {"2D":["Px", "Pz"],
                       "3D":[]}
    necessaryParameters = []
    units = "rad"
    ISUnits = True

    def __init__(self, dataContainer, speciesName):
        standardName = "xP"
        return super().__init__(standardName, dataContainer, not self.ISUnits, speciesName)

    def GetDataInOriginalUnits(self, timeStep):
        Px = self.dataSets["Px"].GetDataInISUnits( timeStep)
        Pz = self.dataSets["Pz"].GetDataInISUnits( timeStep)
        xP = np.divide(Px, Pz)
        return xP

class yPrimeDataSet(CustomRawDataSet):
    # List of necessary data sets and simulation parameters.
    necessaryDataSets = {"2D":["Py", "Pz"],
                       "3D":[]}
    necessaryParameters = []
    units = "rad"
    ISUnits = True

    def __init__(self, dataContainer, speciesName):
        standardName = "yP"
        return super().__init__(standardName, dataContainer, not self.ISUnits, speciesName)

    def GetDataInOriginalUnits(self, timeStep):
        Py = self.dataSets["Py"].GetDataInISUnits( timeStep)
        Pz = self.dataSets["Pz"].GetDataInISUnits( timeStep)
        yP = np.divide(Py, Pz)
        return yP

    
class CustomRawDataSetCreator:
    customDataSets = [
        xPrimeDataSet,
        yPrimeDataSet
        ]
    @classmethod
    def GetCustomDataSets(cls, dataContainer, speciesName):
        dataSetList = list()
        for dataSet in cls.customDataSets:
            if dataSet.meetsRequirements(dataContainer, speciesName):
                dataSetList.append(dataSet(dataContainer, speciesName))
        return dataSetList