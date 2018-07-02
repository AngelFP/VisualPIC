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


import math
import numpy as np


class GeneralUnitConverter(object):
    def __init__(self, simulationParams):
        self.c = 299792458 #m/s
        self.e = 1.60217733 * 10**(-19) #C
        self.m_e = 9.1093897 * 10**(-31) #kg
        self.eps_0 = 8.854187817 * 10**(-12) #As/(Vm)
        self.normalizationFactor = None
        self.SetSimulationParameters(simulationParams)

    def SetSimulationParameters(self, params):
        self._simulationParameters = params

    """
    Possible units
    """
    def GetPossibleDataUnits(self, dataElement):
        dataISUnits = self.GetDataISUnits(dataElement)
        originalUnits = list()
        allOtherUnits = list()
        originalUnits.append(dataElement.GetDataOriginalUnits())
        allOtherUnits = self._GetAllOtherDataUnitsOptions(dataISUnits)
        allUnits = list(set(list(set(originalUnits).union([dataISUnits]))).union(allOtherUnits))
        return allUnits

    def _GetAllOtherDataUnitsOptions(self, dataISUnits):
        if dataISUnits == "V/m":
            return ["V/m", "GV/m", "T"]
        if dataISUnits == "V/m^2":
            return ["V/m^2", "GV/m^2", "T/m", "MT/m"]
        elif dataISUnits == "T":
            return ["T", "V/m"]
        elif dataISUnits == "C/m^2":
            return ["C/m^2"] #, "n/n_0"]
        elif dataISUnits == "m":
            return ["m", "mm", "μm"]
        elif dataISUnits == "kg*m/s":
            return ["kg*m/s", "MeV/c"]
        elif dataISUnits == "J":
            return ["J", "MeV"]
        elif dataISUnits == "rad":
            return ["rad", "mrad"]
        elif dataISUnits == "s":
            return ["s", "fs"]
        else:
            return list()

    def GetPossibleTimeUnits(self, dataElement):
        dataISUnits = "s"
        originalUnits = list()
        allOtherUnits = list()
        originalUnits.append(dataElement.GetTimeOriginalUnits())
        allOtherUnits = self._GetAllOtherTimeUnitsOptions()
        allUnits = list(set(originalUnits).union(allOtherUnits))
        return allUnits

    def _GetAllOtherTimeUnitsOptions(self):
        return ["s", "fs"]

    def GetPossibleAxisUnits(self, dataElement):
        originalUnits = list()
        allOtherUnits = list()
        allOtherUnits = self._GetAllOtherAxisUnitsOptions()
        originalUnits.append(dataElement.GetAxisOriginalUnits()["x"])
        allUnits = list(set(originalUnits).union(allOtherUnits))
        return allUnits

    def _GetAllOtherAxisUnitsOptions(self):
        return ["m", "mm", "μm"]

    """
    Unit conversion
    """
    def GetDataInUnits(self, dataElement, units, data):
        if units == dataElement.GetDataOriginalUnits():
            return data
        elif units == self.GetDataISUnits(dataElement):
            return self.GetDataInISUnits(dataElement, data)
        else:
            dataInISUnits = self.GetDataInISUnits(dataElement, data)
            dataISUnits = self.GetDataISUnits(dataElement)
            return self._MakeConversion(units, dataISUnits, dataInISUnits)

    def GetDataInISUnits(self, dataElement, data):
        if not dataElement.hasNonISUnits:
            return data
        else:
            return self.ConvertToISUnits(dataElement, data)

    def _MakeConversion(self, units, dataISUnits, dataInISUnits):
        if dataISUnits == "V/m":
            if units == "GV/m":
                return dataInISUnits * 1e-9
            elif units == "T":
                return dataInISUnits / self.c
        elif dataISUnits == "V/m^2":
            if units == "GV/m^2":
                return dataInISUnits * 1e-9
            elif units == "T/m":
                return dataInISUnits / self.c
            elif units == "MT/m":
                return dataInISUnits / self.c * 1e-6
        elif dataISUnits == "C/m^2":
            pass
        elif dataISUnits == "T":
            if units == "V/m":
                return dataInISUnits * self.c
        elif dataISUnits == "m":
            if units == "μm":
                return dataInISUnits * 1e6
            elif units == "mm":
                return dataInISUnits * 1e3
        elif dataISUnits == "kg*m/s":
            if units == "MeV/c":
                return dataInISUnits / self.e * self.c * 1e-6
        elif dataISUnits == "J":
            if units == "MeV":
                return dataInISUnits / self.e * 1e-6
        elif dataISUnits == "rad":
            if units == "mrad":
                return dataInISUnits * 1e3
        elif dataISUnits == "s":
            if units == "fs":
                return dataInISUnits * 1e15

    def GetTimeInUnits(self, dataElement, units, timeStep):
        if dataElement.hasNonISUnits:
            if units == dataElement.GetTimeOriginalUnits():
                return dataElement.GetTimeInOriginalUnits(timeStep)
        if units == "s":
            return self.GetTimeInISUnits(dataElement, timeStep)
        else:
            timeInISUnits = self.GetTimeInISUnits(dataElement, timeStep)
            if units == "fs":
                return timeInISUnits * 1e15

    def GetAxisInUnits(self, axis, dataElement, units, timeStep):
        if units == dataElement.GetAxisOriginalUnits()[axis]:
                return dataElement.GetAxisDataInOriginalUnits(axis, timeStep)
        if units == "m":
            return self.GetAxisInISUnits(axis, dataElement, timeStep)
        else:
            axisDataInISUnits = self.GetAxisInISUnits(axis, dataElement, timeStep)
            if units == "μm":
                return axisDataInISUnits * 1e6
            elif units == "mm":
                return axisDataInISUnits * 1e3

    def GetDataISUnits(self, dataElement):
        """ Returns the IS units of the data (only the units, not the data!).
            The purpose of this is to identify"""
        if not dataElement.hasNonISUnits:
            return dataElement.GetDataOriginalUnits()
        else:
            dataElementName = dataElement.GetName()
            if dataElementName == "Ex" or dataElementName == "Ey" or dataElementName == "Ez":
                return "V/m"
            elif dataElementName == "Bx" or dataElementName == "By" or dataElementName == "Bz":
                return "T"
            elif dataElementName == "Charge density":
                return "C/m^2"
            elif dataElementName == "x" or dataElementName == "y" or dataElementName == "z":
                return "m"
            elif dataElementName == "Px" or dataElementName == "Py" or dataElementName == "Pz":
                return "kg*m/s"
            elif dataElementName == "Energy":
                return "J"
            elif dataElementName == "Charge":
                return "C"
            elif dataElementName == "Time":
                return "s"

    """
    To implement by children classes
    """
    def SetNormalizationFactor(self, value):
        raise NotImplementedError

    def GetAxisInISUnits(self, axis, dataElement, timeStep):
        raise NotImplementedError

    def GetTimeInISUnits(self, dataElement, timeStep):
        raise NotImplementedError

    def GetGridSizeInISUnits(self, dataElement):
        raise NotImplementedError

class OsirisUnitConverter(GeneralUnitConverter):
    def __init__(self, simulationParams):
        super(OsirisUnitConverter, self).__init__(simulationParams)

    def _SetNormalizationFactor(self, value):
        """ In OSIRIS the normalization factor is the plasma density and it's given in units of 10^18 cm^-3 """
        self.normalizationFactor = value * 1e24
        self.w_p = math.sqrt(self.normalizationFactor * (self.e)**2 / (self.m_e * self.eps_0)) #plasma freq (1/s)
        self.s_d = self.c / self.w_p  #skin depth (m)
        self.E0 = self.c * self.m_e * self.w_p / self.e # cold non-relativistic field in V/m

    def SetSimulationParameters(self, params):
        super().SetSimulationParameters(params)
        self._SetNormalizationFactor(params["n_p"])

    def ConvertToISUnits(self, dataElement, data):
        dataElementName = dataElement.GetName()
        if dataElementName == "Ex" or dataElementName == "Ey" or dataElementName == "Ez":
            return data*self.E0 # V/m
        elif dataElementName == "Bx" or dataElementName == "By" or dataElementName == "Bz":
            return data*self.E0/self.c # T
        elif dataElementName == "Charge density":
            return data * self.e * (self.w_p / self.c)**2 # C/m^2
        elif dataElementName == "x" or dataElementName == "y" or dataElementName == "z":
            return data*self.s_d # m
        elif dataElementName == "Px" or dataElementName == "Py" or dataElementName == "Pz":
            return data*self.m_e*self.c # kg*m/s
        elif dataElementName == "Energy":
            return data*self.m_e*self.c**2 # J
        elif dataElementName == "Charge":
            cell_size = self.GetCellSizeInISUnits(dataElement)
            cell_vol = np.prod(cell_size)
            return data*self.e*cell_vol*self.normalizationFactor # C
        elif dataElementName == "Time":
            return data/self.w_p # s

    def GetTimeInISUnits(self, dataElement, timeStep):
        time = dataElement.GetTimeInOriginalUnits(timeStep)
        return time / self.w_p

    def GetAxisInISUnits(self, axis, dataElement, timeStep):
        axisData = dataElement.GetAxisDataInOriginalUnits(axis, timeStep)
        return axisData* self.c / self.w_p

    def GetCellSizeInISUnits(self, dataElement):
        original_cell_size = dataElement.GetSimulationCellSizeInOriginalUnits()
        return original_cell_size * self.c / self.w_p


class HiPACEUnitConverter(GeneralUnitConverter):
    def __init__(self, simulationParams):
        super(HiPACEUnitConverter, self).__init__(simulationParams)

    def _SetNormalizationFactor(self, value):
        """ In HiPACE the normalization factor is the plasma density and it's given in units of 10^18 cm^-3 """
        self.normalizationFactor = value * 1e24
        self.w_p = math.sqrt(self.normalizationFactor * (self.e)**2 / (self.m_e * self.eps_0)) #plasma freq (1/s)
        self.s_d = self.c / self.w_p  #skin depth (m)
        self.E0 = self.c * self.m_e * self.w_p / self.e # cold non-relativistic field in V/m

    def SetSimulationParameters(self, params):
        super().SetSimulationParameters(params)
        self._SetNormalizationFactor(params["n_p"])

    def ConvertToISUnits(self, dataElement):
        dataElementName = dataElement.GetName()
        if dataElementName == "Ex" or dataElementName == "Ey" or dataElementName == "Ez":
            return data*self.E0 # V/m
        elif dataElementName == "Bx" or dataElementName == "By" or dataElementName == "Bz":
            return data*self.E0/self.c # T
        elif dataElementName == "Charge density":
            return data * self.e * (self.w_p / self.c)**2 # C/m^2
        elif dataElementName == "x" or dataElementName == "y" or dataElementName == "z":
            return data*self.s_d # m
        elif dataElementName == "Px" or dataElementName == "Py" or dataElementName == "Pz":
            return data*self.m_e*self.c # kg*m/s
        elif dataElementName == "Energy":
            return data*self.m_e*self.c**2 # J
        elif dataElementName == "Charge":
            return data*self.e # C
        elif dataElementName == "Time":
            return data/self.w_p # s

    def GetTimeInISUnits(self, dataElement, timeStep):
        time = dataElement.GetTimeInOriginalUnits(timeStep)
        return time / self.w_p
    
    def GetAxisInISUnits(self, axis, dataElement, timeStep):
        axisData = dataElement.GetAxisDataInOriginalUnits(axis, timeStep)
        return axisData* self.c / self.w_p

    def GetGridSizeInISUnits(self, dataElement):
        original_grid_size = dataElement.GetSimulationCellSizeInOriginalUnits()
        return original_grid_size * self.c / self.w_p


class OpenPMDUnitConverter(GeneralUnitConverter):
    def __init__(self, simulationParams):
        super(OpenPMDUnitConverter, self).__init__(simulationParams)

    def _SetNormalizationFactor(self, value):
        # This function is kept for compatibility with VisualPIC
        # but is not needed for openPMD, since the data is returned in SI
        pass

    def SetSimulationParameters(self, params):
        super().SetSimulationParameters(params)
        self._SetNormalizationFactor(None)

    def ConvertToISUnits(self, dataElement, data):
        data_name = dataElement.GetName()
        if data_name in ["x", "y", "z"]:
            return data * 1e-6
        elif data_name in ["Px", "Py", "Pz"]:
            return data * self.m_e * self.c # kg*m/s
        return data

    def GetTimeInISUnits(self, dataElement, timeStep):
        time = dataElement.GetTimeInOriginalUnits(timeStep)
        return time

    def GetAxisInISUnits(self, axis, dataElement, timeStep):
        axisData = dataElement.GetAxisDataInOriginalUnits(axis, timeStep)
        return axisData


class UnitConverterSelector:
    unitConverters = {
        "Osiris": OsirisUnitConverter,
        "HiPACE": HiPACEUnitConverter,
        "openPMD": OpenPMDUnitConverter
        }
    @classmethod
    def GetUnitConverter(cls, simulationParams):
        return cls.unitConverters[simulationParams["SimulationCode"]](simulationParams)
