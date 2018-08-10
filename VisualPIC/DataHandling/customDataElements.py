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

import numpy as np
from scipy import interpolate as ip
from scipy.constants import c, e, m_e, epsilon_0
import math
from VisualPIC.DataHandling.dataElement import DataElement


"""
Base Class for Custom Fields and Raw Data Sets
"""
class CustomDataElement(DataElement):
    # List of necessary fields and simulation parameters.
    necessaryData = {"2D": [],
                     "3D": [],
                     "thetaMode": []}
    necessaryParameters = []
    units = ""
    ISUnits = True
    standardName = ""

    def __init__(self, dataContainer, speciesName = ''):
        self.dataContainer = dataContainer
        self.dataStandardName = self.standardName
        self.speciesName = speciesName
        self.hasNonISUnits = not self.ISUnits
        self.set_base_data()
        self._SetTimeSteps()

    def _SetTimeSteps(self):
        i = 0
        for DataName, DataElement in self.data.items():
            if i == 0:
                timeSteps = DataElement.GetTimeSteps()
            else:
                timeSteps = np.intersect1d(timeSteps,
                                           DataElement.GetTimeSteps())
        self.timeSteps = timeSteps

    def set_base_data(self):
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
    def meets_requirements(cls, dataContainer):
        "Checks whether the required data and parameters are available"
        if dataContainer.GetSimulationDimension() in cls.necessaryData:
            data_requirements_met = set(
                dataContainer.GetAvailableDomainFieldsNames()).issuperset(
                    cls.necessaryData[dataContainer.GetSimulationDimension()])
            parameter_requirements_met = set(
                dataContainer.GetNamesOfAvailableParameters()).issuperset(
                    cls.necessaryParameters)
            return data_requirements_met and parameter_requirements_met
        else:
            return False

    def set_base_data(self):
        dimension = self.dataContainer.GetSimulationDimension()
        self.data = {}
        for field_name in self.necessaryData[dimension]:
            self.data[field_name] = self.dataContainer.GetDomainField(
                field_name)

    def GetFieldDimension(self):
        return list(self.data.items())[0][1].GetFieldDimension()

    def GetPossibleAxisUnits(self):
        return self._unitConverter.GetPossibleAxisUnits(self)

    def GetAxisDataInOriginalUnits(self, axis, timeStep):
        return list(self.data.items())[0][1].GetAxisDataInOriginalUnits(
            axis, timeStep)
        
    def GetAxisOriginalUnits(self):
        return list(self.data.items())[0][1].GetAxisOriginalUnits()

    """
    Get data in original units
    """
    def Get1DSliceInOriginalUnits(self, timeStep, slicePositionX,
                                  slicePositionY = None):
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

    def Get3DFieldFrom2DSliceInOriginalUnits(self, timeStep, transvEl, longEl,
                                             fraction):
        """
        fraction: used to define the range of data we want to visualize in the 
        transverse direction.
            - fraction = 1 -> get all the data
            - fraction = 0.5 -> get only from x=0 to x=x_max*0.5
        """
        field2D = self.GetAllFieldDataInOriginalUnits(timeStep)
        nx = field2D.shape[0]
        # we get only half of the field data
        field2D = field2D[int(nx/2):int(nx/2+nx/2*fraction)]
        cilShape = field2D.shape
        # cyl. coordinates of original data
        Rin,Zin = np.mgrid[0:cilShape[0], 0:cilShape[1]] 
        Zin = np.reshape(Zin, Zin.shape[0]*Zin.shape[1])
        Rin = np.reshape(Rin, Rin.shape[0]*Rin.shape[1])
        field2D = np.reshape(field2D, field2D.shape[0]*field2D.shape[1])
        transvSpacing = cilShape[0]*2/transvEl
        lonSpacing = cilShape[1]/longEl
        field3D = np.zeros((transvEl, transvEl, longEl))
        # cart. coordinates of 3D field
        X, Y, Z = np.mgrid[0:cilShape[0]:transvSpacing,
                           0:cilShape[0]:transvSpacing,
                           0:cilShape[1]:lonSpacing] 
        Rout = np.sqrt(X**2 + Y**2)
        # Fill the field sector by sector
        # (only the first has to be calculated. The rest are simlpy mirrored)
        # Start with top right section (when looking back from z to the
        # x-y plane).
        field3D[int(transvEl/2):transvEl + 1, int(transvEl/2):transvEl + 1] = (
            ip.griddata(np.column_stack((Rin,Zin)),
                        field2D,
                        (Rout, Z),
                        method='nearest',
                        fill_value = 0))
        # Now perform the mirroring
        field3D[0:int(transvEl/2), int(transvEl/2):transvEl + 1] = (
            np.flip(field3D[int(transvEl/2):transvEl + 1,
                            int(transvEl/2):transvEl + 1],0))
        field3D[0:int(transvEl/2), 0:int(transvEl/2)] = (
            np.flip(field3D[0:int(transvEl/2),
                            int(transvEl/2):transvEl + 1], 1))
        field3D[int(transvEl/2):transvEl + 1, 0:int(transvEl/2)] = (
            np.flip(field3D[int(transvEl/2):transvEl + 1,
                            int(transvEl/2):transvEl+1], 1))
        return field3D
    
    """
    Get data in any units
    """
    def Get1DSlice(self, timeStep, units, slicePositionX,
                   slicePositionY = None):
        fieldData = self.CalculateField(timeStep)
        if self.GetFieldDimension() in ['2D', 'thetaMode']:
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
        if self.GetFieldDimension() == "thetaMode":
            sliceData = fieldData
        else:
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
    def Get1DSliceISUnits(self, timeStep, slicePositionX,
                          slicePositionY = None):
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


class TransverseWakefieldX(CustomField):
    # List of necessary fields and simulation parameters.
    necessaryData = {"2D": ["Ex", "By"],
                     "3D": ["Ex", "By"],
                     "thetaMode": ["Ex", "By"]}
    necessaryParameters = []
    units = "V/m"
    ISUnits = True
    standardName = "Wx"

    def CalculateField(self, timeStep):
        Ex = self.data["Ex"].GetAllFieldDataISUnits(timeStep)
        By = self.data["By"].GetAllFieldDataISUnits(timeStep)
        Wx = Ex - c*By
        return Wx


class TransverseWakefieldY(CustomField):
    # List of necessary fields and simulation parameters.
    necessaryData = {"2D": ["Ey", "Bx"],
                     "3D": ["Ey", "Bx"],
                     "thetaMode": ["Ey", "Bx"]}
    necessaryParameters = []
    units = "V/m"
    ISUnits = True
    standardName = "Wy"

    def CalculateField(self, timeStep):
        Ey = self.data["Ey"].GetAllFieldDataISUnits(timeStep)
        Bx = self.data["Bx"].GetAllFieldDataISUnits(timeStep)
        Wy = Ey + c*Bx
        return Wy


class LaserIntensityField(CustomField):
    # TODO: Implement correcly in 2D 
    # (information about polarization plane is required).
    necessaryData = {"2D": ["Ex", "Ez"],
                     "3D": ["Ex", "Ey", "Ez"],
                     "thetaMode": ["Er", "Ez"]}
    necessaryParameters = []
    units = "W/m^2"
    ISUnits = True
    standardName = "I"

    def CalculateField(self, timeStep):
        if self.GetFieldDimension() == 'thetaMode':
            Er = self.data["Er"].GetAllFieldDataISUnits(timeStep)
            Ez = self.data["Ez"].GetAllFieldDataISUnits(timeStep)
            E2 = np.square(Ez) + np.square(Er)
        else:
            Ex = self.data["Ex"].GetAllFieldDataISUnits(timeStep)
            Ez = self.data["Ez"].GetAllFieldDataISUnits(timeStep)
            if self.GetFieldDimension() == '3D':
                Ey = self.data["Ey"].GetAllFieldDataISUnits(timeStep)
                E2 = np.square(Ez) + np.square(Ey) + np.square(Ex)
            if self.GetFieldDimension() == '2D':
                E2 = np.square(Ez) + np.square(Ex)
        # Assume index of refraction equal to 1
        intensity = c*epsilon_0/2*E2 
        return intensity


class NormalizedVectorPotential(CustomField):
    necessaryData = {"2D": ["Ex", "Ez"],
                     "3D": ["Ex", "Ey", "Ez"],
                     "thetaMode": ["Er", "Ez"]}
    necessaryParameters = ["n_p", "lambda_l"]
    units = "m_e*c^2/e"
    ISUnits = True
    standardName = "a"

    def CalculateField(self, timeStep):
        if self.GetFieldDimension() == 'thetaMode':
            Er = self.data["Er"].GetAllFieldDataISUnits(timeStep)
            Ez = self.data["Ez"].GetAllFieldDataISUnits(timeStep)
            E2 = np.square(Ez) + np.square(Er)
        else:
            Ex = self.data["Ex"].GetAllFieldDataISUnits(timeStep)
            Ez = self.data["Ez"].GetAllFieldDataISUnits(timeStep)
            if self.GetFieldDimension() == '3D':
                Ey = self.data["Ey"].GetAllFieldDataISUnits(timeStep)
                E2 = np.square(Ez) + np.square(Ey) + np.square(Ex)
            if self.GetFieldDimension() == '2D':
                E2 = np.square(Ez) + np.square(Ex)
        # Assume index of refraction equal to 1
        intensity = c*epsilon_0/2*E2 
        # laser wavelength (m)
        lambda_l = self.dataContainer.GetSimulationParameter("lambda_l") * 1e-9
        # normalized vector potential
        a = np.sqrt(7.3e-11 * lambda_l**2 * intensity) 
        return a


class TransverseWakefieldSlopeX(CustomField):
    # List of necessary fields and simulation parameters.
    necessaryData = {"2D": ["Ex", "By"],
                     "3D": ["Ex", "By"],
                     "thetaMode": ["Ex", "By"]}
    necessaryParameters = []
    units = "V/m^2"
    ISUnits = True
    standardName = "dx Wx"

    def CalculateField(self, timeStep):
        Ex = self.data["Ex"].GetAllFieldDataISUnits(timeStep)
        By = self.data["By"].GetAllFieldDataISUnits(timeStep)
        Wx = Ex - c*By
        if self.GetFieldDimension() == 'thetaMode':
            x = self.data["Ex"].GetAxisInISUnits("r", timeStep)
        else:
            x = self.data["Ex"].GetAxisInISUnits("x", timeStep)
        dx = abs(x[1]-x[0]) # distance between data points in y direction
        
        if self.GetFieldDimension() in ['2D', 'thetaMode']:
            slope = np.gradient(Wx, dx, axis=0)
        elif self.GetFieldDimension() == '3D':
            slope = np.gradient(Wx, dx, axis=1)
        return slope


class TransverseWakefieldSlopeY(CustomField):
    # List of necessary fields and simulation parameters.
    necessaryData = {"2D": ["Ey", "Bx"],
                     "3D": ["Ey", "Bx"],
                     "thetaMode": ["Ey", "Bx"]}
    necessaryParameters = []
    units = "V/m^2"
    ISUnits = True
    standardName = "dy Wy"

    def CalculateField(self, timeStep):
        Ey = self.data["Ey"].GetAllFieldDataISUnits( timeStep)
        Bx = self.data["Bx"].GetAllFieldDataISUnits( timeStep)
        Wy = Ey + c*Bx
        if self.GetFieldDimension() == 'thetaMode':
            y = self.data["Ey"].GetAxisInISUnits("r", timeStep)
        else:
            y = self.data["Ey"].GetAxisInISUnits("y", timeStep)
        dy = abs(y[1]-y[0]) # distance between data points in y direction
        
        if self.GetFieldDimension() in ['2D', 'thetaMode']:
            slope = np.gradient(Wy, dy, axis=0)
        elif self.GetFieldDimension() == '3D':
            slope = np.gradient(Wy, dy, axis=1)
        return slope


class EzSlope(CustomField):
    necessaryData = {"2D": ["Ez"],
                     "3D": ["Ez"],
                     "thetaMode": ["Ez"]}
    necessaryParameters = []
    units = "V/m^2"
    ISUnits = True
    standardName = "dz Ez"

    def CalculateField(self, timeStep):
        Ez = self.data["Ez"].GetAllFieldDataISUnits( timeStep)
        z = self.data["Ez"].GetAxisInISUnits("z", timeStep)
        dz = abs(z[1]-z[0]) # distance between data points in z direction
        if (self.GetFieldDimension() == '2D'
            or self.GetFieldDimension() == 'thetaMode'):
            slope = np.gradient(Ez, dz, axis=1)
        elif self.GetFieldDimension() == '3D':
            slope = np.gradient(Ez, dz, axis=2)
        return slope


class CustomFieldCreator:
    customFields = [
        TransverseWakefieldX,
        TransverseWakefieldY,
        TransverseWakefieldSlopeX,
        TransverseWakefieldSlopeY,
        LaserIntensityField,
        NormalizedVectorPotential,
        EzSlope
        ]
    @classmethod
    def GetCustomFields(cls, dataContainer):
        fieldList = list()
        for Field in cls.customFields:
            if Field.meets_requirements(dataContainer):
                fieldList.append(Field(dataContainer))
        return fieldList


"""
Custom Raw Data Sets
"""
class CustomRawDataSet(CustomDataElement):
    @classmethod
    def meets_requirements(cls, dataContainer, speciesName):
        "Checks whether the required data and parameters are available"
        if dataContainer.GetSimulationDimension() in cls.necessaryData:
            data_requirements_met = set(
                dataContainer.GetSpecies(
                    speciesName).GetRawDataSetsNamesList()).issuperset(
                        cls.necessaryData[
                            dataContainer.GetSimulationDimension()])
            parameter_requirements_met = set(
                dataContainer.GetNamesOfAvailableParameters()).issuperset(
                    cls.necessaryParameters)
            return data_requirements_met and parameter_requirements_met
        else:
            return False

    def set_base_data(self):
        dimension = self.dataContainer.GetSimulationDimension()
        self.data = {}
        for data_name in self.necessaryData[dimension]:
            self.data[data_name] = self.dataContainer.GetSpecies(
                self.speciesName).GetRawDataSet(data_name)

    """
    Get data in original units (to be implemented in each subclass)
    """
    def GetDataInOriginalUnits(self, timeStep):
        raise NotImplementedError

    """
    Get data in any units
    """
    def GetDataInUnits(self, units, timeStep):
        return self._unitConverter.GetDataInUnits(
            self, units, self.GetDataInOriginalUnits(timeStep))

    """
    Get data in IS units
    """
    def GetDataInISUnits(self, timeStep):
        return self._unitConverter.GetDataInISUnits(
            self, self.GetDataInOriginalUnits(timeStep))


class xPrimeDataSet(CustomRawDataSet):
    # List of necessary data sets and simulation parameters.
    necessaryData = {"2D": ["Px", "Pz"],
                     "3D": ["Px", "Pz"],
                     "thetaMode": ["Px", "Pz"]}
    necessaryParameters = []
    units = "rad"
    ISUnits = True
    standardName = "x'"

    def GetDataInOriginalUnits(self, timeStep):
        Px = self.data["Px"].GetDataInISUnits( timeStep)
        Pz = self.data["Pz"].GetDataInISUnits( timeStep)
        xP = np.divide(Px, Pz)
        return xP


class yPrimeDataSet(CustomRawDataSet):
    # List of necessary data sets and simulation parameters.
    necessaryData = {"2D": ["Py", "Pz"],
                     "3D": ["Py", "Pz"],
                     "thetaMode": ["Py", "Pz"]}
    necessaryParameters = []
    units = "rad"
    ISUnits = True
    standardName = "y'"

    def GetDataInOriginalUnits(self, timeStep):
        Py = self.data["Py"].GetDataInISUnits( timeStep)
        Pz = self.data["Pz"].GetDataInISUnits( timeStep)
        yP = np.divide(Py, Pz)
        return yP


class deltaZPrimeDataSet(CustomRawDataSet):
    # List of necessary data sets and simulation parameters.
    necessaryData = {"2D": ["z", "Charge"],
                     "3D": ["z", "Charge"],
                     "thetaMode": ["z", "Charge"]}
    necessaryParameters = []
    units = "m"
    ISUnits = True
    standardName = "Δz"

    def GetDataInOriginalUnits(self, timeStep):
        z = self.data["z"].GetDataInISUnits( timeStep)
        q = self.data["Charge"].GetDataInISUnits( timeStep)
        meanZ = np.average(z, weights=q)
        dZ = z-meanZ
        return dZ


class forwardMomentumVariationDataSet(CustomRawDataSet):
    # List of necessary data sets and simulation parameters.
    necessaryData = {"2D": ["Pz", "Charge"],
                     "3D": ["Pz", "Charge"],
                     "thetaMode": ["Pz", "Charge"]}
    necessaryParameters = []
    units = "rad"
    ISUnits = True
    standardName = "ΔPz/Pz"

    def GetDataInOriginalUnits(self, timeStep):
        Pz = self.data["Pz"].GetDataInISUnits(timeStep)
        q = self.data["Charge"].GetDataInISUnits(timeStep)
        meanPz = np.average(Pz, weights=q)
        dPz = np.divide(Pz - meanPz, meanPz)
        return dPz


class SpeedOfLightCoordinate(CustomRawDataSet):
    # List of necessary data sets and simulation parameters.
    necessaryData = {"2D": ["z"],
                     "3D": ["z"],
                     "thetaMode": ["z"]}
    necessaryParameters = []
    units = "m"
    ISUnits = True
    standardName = "xi"

    def GetDataInOriginalUnits(self, timeStep):
        z = self.data["z"].GetDataInISUnits(timeStep)
        t = self.data["z"].GetTimeInUnits("s", timeStep)
        xi = z - 299792458*t
        return xi


#class BeamComovingCoordinate(CustomRawDataSet):
#    # List of necessary data sets and simulation parameters.
#    necessaryData = {"2D": ["z"],
#                     "3D": ["z"],
#                     "thetaMode": ["z"]}
#    necessaryParameters = []
#    units = "m"
#    ISUnits = True
#    standardName = "xi_beam"

#    def GetDataInOriginalUnits(self, timeStep):
#        z = self.data["z"].GetDataInISUnits(timeStep)
#        xi_b = z - min(z)
#        return xi_b


#class UncorrelatedEnergyVariationDataSet(CustomRawDataSet):
#    # List of necessary data sets and simulation parameters.
#    necessaryData = {"2D": ["Pz", "Py", "z", "Charge"],
#                     "3D": ["Pz", "Py", "Pz", "z", "Charge"],
#                     "thetaMode": ["Pz", "Py", "Pz", "z", "Charge"]}
#    necessaryParameters = []
#    units = "."
#    ISUnits = True
#    standardName = "UncEneSp"

#    def GetDataInOriginalUnits(self, timeStep):
#        Pz = self.data["Pz"].GetDataInOriginalUnits(timeStep)
#        Py = self.data["Py"].GetDataInOriginalUnits(timeStep)
#        z = self.data["z"].GetDataInOriginalUnits(timeStep)
#        q = self.data["Charge"].GetDataInOriginalUnits(timeStep)
#        gamma = np.sqrt(Pz**2 + Py**2)
#        mean_gamma = np.average(gamma, weights=np.abs(q))
#        rel_gamma_spread = (gamma-mean_gamma)/mean_gamma
#        dz = z - np.average(z, weights=q)
#        p = np.polyfit(dz, rel_gamma_spread, 1, w=q)
#        slope = p[0]
#        unc_gamma_spread = rel_gamma_spread - slope*dz
#        return unc_gamma_spread
 
    
class CustomRawDataSetCreator:
    customDataSets = [
        xPrimeDataSet,
        yPrimeDataSet,
        deltaZPrimeDataSet,
        forwardMomentumVariationDataSet,
        SpeedOfLightCoordinate,
        ]
    @classmethod
    def GetCustomDataSets(cls, dataContainer, speciesName):
        dataSetList = list()
        for dataSet in cls.customDataSets:
            if dataSet.meets_requirements(dataContainer, speciesName):
                dataSetList.append(dataSet(dataContainer, speciesName))
        return dataSetList
