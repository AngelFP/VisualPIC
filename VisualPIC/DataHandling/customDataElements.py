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
from VisualPIC.DataHandling.dataElement import DataElement
from VisualPIC.DataHandling.unitConverters import UnitConverterSelector


class CustomDataElement(DataElement):
    def __init__(self, standardName, dataContainer, unitConverter, speciesName = ''):
        self.c = 299792458 #m/s
        self.e = 1.60217733 * 10**(-19) #C
        self.m_e = 9.1093897 * 10**(-31) #kg
        self.eps_0 = 8.854187817 * 10**(-12) #As/(Vm)
        self.dataContainer = dataContainer
        self.unitConverter = unitConverter
        timeSteps = self._SetTimeSteps()
        return super().__init__(standardName, timeSteps, speciesName, False)

    def _SetTimeSteps(self, dataContainer):
        raise NotImplementedError


class CustomField(CustomDataElement):
    def __init__(self, standardName, dataContainer, unitConverter, speciesName = ''):
        self._SetBaseFields(dataContainer)
        return super().__init__(standardName, dataContainer, unitConverter, speciesName)

    def _SetBaseFields(self, dataContainer):
        raise NotImplementedError


class TransverseWakefield(CustomField):
    def __init__(self, dataContainer, unitConverter, speciesName = ''):
        standardName = "Transverse Wakefield"
        super().__init__(standardName, dataContainer, unitConverter, speciesName)

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
    def __init__(self, dataContainer, unitConverter, speciesName = ''):
        standardName = "Laser Intensity"
        super().__init__(standardName, dataContainer, unitConverter, speciesName)

    def _SetBaseFields(self, dataContainer):
        self.fields = {
            "Ey": dataContainer.GetDomainField("Ey"),
            "Ex": dataContainer.GetDomainField("Ex")}

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
        Ex = self.unitConverter.GetDataInISUnits( self.fields["Ex"], timeStep)
        w_p = self.unitConverter.w_p
        Intensity = Ey - self.c*Bx
        return Intensity

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

class CustomFieldCreator:
    customFields = {
        "TransverseWakefield": TransverseWakefield
        }
    @classmethod
    def GetCustomFields(cls, dataContainer, unitConverter):
        fieldList = list()
        for FieldKey in cls.customFields:
            fieldList.append(cls.customFields[FieldKey](dataContainer, unitConverter))
        return fieldList