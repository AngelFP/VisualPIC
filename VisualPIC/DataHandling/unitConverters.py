# -*- coding: utf-8 -*-

#Copyright 2016 Ángel Ferran Pousa
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

import sys
import math
import codecs
import numpy as np


class UnitConverterSelector:
    unitConverters = {"Osiris": OsirisUnitConverter,
                   "HiPACE": HiPACEUnitConverter
                   }
    @classmethod
    def GetUnitConverter(cls, simulationCode):
        return cls.unitConverters[simulationCode]


class GeneralUnitConverter:
    def __init__(self):
        self.c = 299792458 #m/s
        self.e = 1.60217733 * 10**(-19) #C
        self.m_e = 9.1093897 * 10**(-31) #kg
        self.eps_0 = 8.854187817 * 10**(-12) #As/(Vm)
        self.hasNonISUnits = False
        self.normalizationFactorIsSet = False
        self.normalizationFactor = None
        #special units (with non ascii characters)
        if sys.version_info[0] < 3:
            self.um = u"μm"
        else:
            self.um = "μm"

    def GetPossibleDataUnits(self, dataElement):
        dataISUnits = self.GetDataISUnits(dataElement)
        originalUnits = list()
        allOtherUnits = list()
        if self.hasNonISUnits:
            originalUnits.append(dataElement.GetDataUnits())
            if self.normalizationFactorIsSet:
                allOtherUnits = self._GetAllOtherDataUnitsOptions(dataISUnits)
        else:
            allOtherUnits = self._GetAllOtherDataUnitsOptions(dataISUnits)
        allUnits = originalUnits + allOtherUnits
        return allUnits

    def _GetAllOtherDataUnitsOptions(self, dataISUnits):
        if dataISUnits == "V/m":
            return ["V/m", "GV/m"]
        elif dataISUnits == "T":
            return ["T", "V/m"]
        elif dataISUnits == "C/m^2":
            return ["C/m^2"] #, "n/n_0"]

    def GetAxisUnitsOptions(self, field):
        originalUnits = list()
        allOtherUnits = list()
        if self.hasNonISUnits:
            originalUnits.append(dataElement.GetAxisUnits()["x"])
            if self.normalizationFactorIsSet:
                allOtherUnits = self._GetAllOtherAxisUnitsOptions()
        else:
            allOtherUnits = self._GetAllOtherAxisUnitsOptions()
        allUnits = originalUnits + allOtherUnits
        return allUnits

    def _GetAllOtherAxisUnitsOptions(self):
        return ["m", self.um]

    def GetDataInUnits(self, dataElement, units, timeStep):
        if self.hasNonISUnits:
            if units == dataElement.GetDataUnits():
                return self._GetDataInOriginalUnits(dataElement, timeStep)
        if units == self.GetDataISUnits(dataElement):
            return self.GetDataInISUnits(dataElement, timeStep)
        else:
            dataInISUnits = self.GetDataInISUnits(dataElement, timeStep)
            dataISUnits = self.GetDataISUnits(dataElement)
            if dataISUnits == "V/m":
                if units == "GV/m":
                    return dataInISUnits * 1e-9
            elif dataISUnits == "C/m^2":
                pass
            elif dataISUnits == "T":
                if units == "V/m":
                    return dataInISUnits * self.c

    def GetAxisInUnits(self, axis, dataElement, units, timeStep):
        if self.hasNonISUnits:
            if units == dataElement.GetAxisUnits():
                return self._GetAxisDataInOriginalUnits(axis, dataElement, timeStep)
        if units == "m":
            return self.GetAxisInSIUnits(axis, dataElement, timeStep)
        else:
            axisDataInISUnits = self.GetAxisInSIUnits(axis, dataElement, timeStep)
            if units == self.um:
                return axisDataInISUnits * 1e6

    """
    To implement by children classes
    """
    def SetNormalizationFactor(self, value):
        raise NotImplementedError

    def GetDataISUnits(self, dataElement):
        raise NotImplementedError

    def GetDataInISUnits(self, dataElement, timeStep):
        raise NotImplementedError

    def _GetDataInOriginalUnits(self, dataElement, timeStep):
        raise NotImplementedError

    def GetAxisInSIUnits(self, axis, dataElement, timeStep):
        raise NotImplementedError

    def _GetAxisDataInOriginalUnits(self, axis, dataElement, timeStep):
        raise NotImplementedError

class OsirisUnitConverter(GeneralUnitConverter):
    def __init__(self):
        super(OsirisUnitConverter, self).__init__()
        self.hasNonISUnits = True
        
    def SetNormalizationFactor(self, value):
        """ In OSIRIS the normalization factor is the plasma density and it's given in units of 10^18 cm^-3 """
        self.normalizationFactor = value * 1e24
        self.normalizationFactorIsSet = True
        self.w_p = math.sqrt(self.n_p * (self.e)**2 / (self.m_e * self.eps_0)) #plasma freq (1/s)
        self.s_d = self.c / self.w_p  #skin depth (m)
        self.E0 = self.c * self.m_e * self.w_p / self.e # cold non-relativistic field in V/m
    
    def GetDataISUnits(self, dataElement):
        """ Returns the IS units of the data (only the units, not the data!).
            The purpose of this is to identify"""
        dataElementName = dataElement.GetName()
        if "e1" in dataElementName or "e2" in dataElementName or "e3" in dataElementName:
            return "V/m"
        elif "b1" in dataElementName or "b2" in dataElementName or "b3" in dataElementName:
            return "T"
        elif "charge" in fieldName:
            return "C/m^2"
        elif "x1" == dataElementName or "x2" == dataElementName or "x3" == dataElementName:
            return "m"
        elif "p1" == dataElementName or "p2" == dataElementName or "p3" == dataElementName:
            return "kg*m/s"
        elif "ene" == dataElementName:
            return "J"
        elif "q" == dataElementName:
            return "C"
                
    def GetDataInISUnits(self, dataElement, timeStep):
        dataElementName = dataElement.GetName()
        data = self._GetDataInOriginalUnits(dataElement, timeStep)
        if "e1" in dataElementName or "e2" in dataElementName or "e3" in dataElementName:
            return data*self.E0 # V/m
        elif "b1" in dataElementName or "b2" in dataElementName or "b3" in dataElementName:
            return data*self.E0/self.c # T
        elif "charge" in fieldName:
            return data * self.e * (self.w_p / self.c)**2 # C/m^2
        elif "x1" == dataElementName or "x2" == dataElementName or "x3" == dataElementName:
            return data*self.s_d # m
        elif "p1" == dataElementName or "p2" == dataElementName or "p3" == dataElementName:
            return data*self.m_e*self.c # kg*m/s
        elif "ene" == dataElementName:
            return data*self.m_e*self.c**2 # J
        elif "q" == dataElementName:
            return data*self.e # C

    def _GetDataInOriginalUnits(self, dataElement, timeStep):
        return dataElement.GetData(timeStep)

    def GetAxisInSIUnits(self, axis, dataElement, timeStep):
        axisData = self._GetAxisDataInOriginalUnits(axis, dataElement, timeStep)
        return axisData* self.c / self.w_p

    def _GetAxisDataInOriginalUnits(self, axis, dataElement, timeStep):
        return dataElement.GetAxisData(timeStep)[axis]

class HiPACEUnitConverter(GeneralUnitConverter):
    def __init__(self):
        super(HiPACEUnitConverter, self).__init__()
        self.hasNonISUnits = True
        

        
        
        