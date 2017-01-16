# -*- coding: utf-8 -*-

#Copyright 2016 Angel Ferran Pousa
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
from VisualPIC.DataHandling.unitConverters import UnitConverterSelector


class CustomDataElement(DataElement):
    def __init__(self, standardName, dataContainer, speciesName = ''):
        self.c = 299792458 #m/s
        self.e = 1.60217733 * 10**(-19) #C
        self.m_e = 9.1093897 * 10**(-31) #kg
        self.eps_0 = 8.854187817 * 10**(-12) #As/(Vm)
        self.dataContainer = dataContainer
        self.unitConverter = dataContainer.unitConverter
        timeSteps = self._SetTimeSteps()
        return super().__init__(standardName, timeSteps, speciesName, False)

    def _SetTimeSteps(self, dataContainer):
        raise NotImplementedError


class CustomField(CustomDataElement):
    # List of necessary fields and simulation parameters.
    necessaryFields = {"2D":[],
                       "3D":[]}
    necessaryParameters = []

    @classmethod
    def meetsRequirements(cls, dataContainer):
        if (set(dataContainer.GetAvailableDomainFieldsNames()).issuperset(cls.necessaryFields[dataContainer.GetSimulationDimension()])) and (set(dataContainer.GetNamesOfAvailableParameters()).issuperset(cls.necessaryParameters)):
            return True
        else:
            return False

    def __init__(self, standardName, dataContainer, speciesName = ''):
        self._SetBaseFields(dataContainer)
        return super().__init__(standardName, dataContainer, speciesName)

    def _SetBaseFields(self, dataContainer):
        raise NotImplementedError


class TransverseWakefield(CustomField):
    # List of necessary fields and simulation parameters.
    necessaryFields = {"2D":["Ey", "Bx"],
                       "3D":["Ey", "Bx"]}
    necessaryParameters = []

    def __init__(self, dataContainer, speciesName = ''):
        standardName = "Transverse Wakefield"
        super().__init__(standardName, dataContainer, speciesName)

    def _SetBaseFields(self, dataContainer):
        self.fields = {
            "Ey": dataContainer.GetDomainField("Ey"),
            "Bx": dataContainer.GetDomainField("Bx")}

    def _SetTimeSteps(self):
        i = 0
        for FieldName, Field in self.fields.items():
            if i == 0:
                timeSteps = Field.GetTimeSteps()
            else:
                timeSteps = np.intersect1d(timeSteps, Field.GetTimeSteps())
        return timeSteps

    def GetData(self, timeStep):
        Ey = self.unitConverter.GetDataInISUnits( self.fields["Ey"], timeStep)
        Bx = self.unitConverter.GetDataInISUnits( self.fields["Bx"], timeStep)
        TranvsWF = Ey - self.c*Bx
        return TranvsWF

    def GetDataUnits(self):
        return "V/m"

    def GetTime(self, timeStep):
        return self.fields["Ey"].GetTime(timeStep)

    def GetTimeUnits(self):
        return self.fields["Ey"].GetTimeUnits()

    def GetFieldDimension(self):
        return self.fields["Ey"].GetFieldDimension()

    def GetAxisData(self, timeStep):
        return self.fields["Ey"].GetAxisData(timeStep) #dictionary
        
    def GetAxisUnits(self):
        return self.fields["Ey"].GetAxisUnits()

class LaserIntensityField(CustomField):
    # List of necessary fields and simulation parameters.
    necessaryFields = {"2D":["Ey", "Ez"],
                       "3D":["Ex", "Ey", "Ez"]}
    necessaryParameters = ["n_p", "lambda_l"]

    def __init__(self, dataContainer, speciesName = ''):
        standardName = "Laser Intensity"
        super().__init__(standardName, dataContainer, speciesName)

    def _SetBaseFields(self, dataContainer):
        self.fields = {
            "Ey": dataContainer.GetDomainField("Ey"),
            "Ez": dataContainer.GetDomainField("Ez")}

    def _SetTimeSteps(self):
        i = 0
        for FieldName, Field in self.fields.items():
            if i == 0:
                timeSteps = Field.GetTimeSteps()
            else:
                timeSteps = np.intersect1d(timeSteps, Field.GetTimeSteps())
        return timeSteps

    def GetData(self, timeStep):
        Ey = self.unitConverter.GetDataInISUnits( self.fields["Ey"], timeStep)
        Ez = self.unitConverter.GetDataInISUnits( self.fields["Ez"], timeStep)
        n_p = self.dataContainer.GetSimulationParameter("n_p") * 1e24
        w_p = math.sqrt(n_p * (self.e)**2 / (self.m_e * self.eps_0)) #plasma freq (1/s)
        lambda_l = self.dataContainer.GetSimulationParameter("lambda_l") * 1e-9 # laser wavelength (m)
        w_l = 2 * math.pi * self.c / lambda_l # laser angular frequency (rad/sec)
        n = math.sqrt(1-(w_p/w_l)**2) # index of refraction
        E2 = np.square(Ez) + np.square(Ey) # square of electric field modulus
        Intensity = self.c*self.eps_0*n/2*E2
        return Intensity

    def GetDataUnits(self):
        return "W/m^2"

    def GetTime(self, timeStep):
        return self.fields["Ey"].GetTime(timeStep)

    def GetTimeUnits(self):
        return self.fields["Ey"].GetTimeUnits()

    def GetFieldDimension(self):
        return self.fields["Ey"].GetFieldDimension()

    def GetAxisData(self, timeStep):
        return self.fields["Ey"].GetAxisData(timeStep) #dictionary
        
    def GetAxisUnits(self):
        return self.fields["Ey"].GetAxisUnits()


class NormalizedVectorPotential(CustomField):
    # List of necessary fields and simulation parameters.
    necessaryFields = {"2D":["Ey", "Ez"],
                       "3D":["Ex", "Ey", "Ez"]}
    necessaryParameters = ["n_p", "lambda_l"]

    def __init__(self, dataContainer, speciesName = ''):
        standardName = "Normalized Vector Potential"
        super().__init__(standardName, dataContainer, speciesName)

    def _SetBaseFields(self, dataContainer):
        self.fields = {
            "Ey": dataContainer.GetDomainField("Ey"),
            "Ez": dataContainer.GetDomainField("Ez")}

    def _SetTimeSteps(self):
        i = 0
        for FieldName, Field in self.fields.items():
            if i == 0:
                timeSteps = Field.GetTimeSteps()
            else:
                timeSteps = np.intersect1d(timeSteps, Field.GetTimeSteps())
        return timeSteps

    def GetData(self, timeStep):
        Ey = self.unitConverter.GetDataInISUnits( self.fields["Ey"], timeStep)
        Ez = self.unitConverter.GetDataInISUnits( self.fields["Ez"], timeStep)
        n_p = self.dataContainer.GetSimulationParameter("n_p") * 1e24
        w_p = math.sqrt(n_p * (self.e)**2 / (self.m_e * self.eps_0)) #plasma freq (1/s)
        lambda_l = self.dataContainer.GetSimulationParameter("lambda_l") * 1e-9 # laser wavelength (m)
        w_l = 2 * math.pi * self.c / lambda_l # laser angular frequency (rad/sec)
        n = math.sqrt(1-(w_p/w_l)**2) # index of refraction
        E2 = np.square(Ez) + np.square(Ey) # square of electric field modulus
        Intensity = self.c*self.eps_0*n/2*E2
        a = np.sqrt(7.3e-11 * lambda_l**2 * Intensity) # normalized vector potential
        return a

    def GetDataUnits(self):
        return "m_e*c^2/e"

    def GetTime(self, timeStep):
        return self.fields["Ey"].GetTime(timeStep)

    def GetTimeUnits(self):
        return self.fields["Ey"].GetTimeUnits()

    def GetFieldDimension(self):
        return self.fields["Ey"].GetFieldDimension()

    def GetAxisData(self, timeStep):
        return self.fields["Ey"].GetAxisData(timeStep) #dictionary
        
    def GetAxisUnits(self):
        return self.fields["Ey"].GetAxisUnits()

class CustomFieldCreator:
    customFields = [
        TransverseWakefield,
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

# TODO: Add custom field filters, so that only the custom fields for which there exists the necessary data are loaded.