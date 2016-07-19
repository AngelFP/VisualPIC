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

import math
import numpy as np

class OsirisUnitConverter:
    def __init__(self):
        self.c = 299792458 #m/s
        self.e = 1.60217733 * 10**(-19) #C
        self.m_e = 9.1093897 * 10**(-31) #kg
        self.eps_0 = 8.854187817 * 10**(-12) #As/(Vm)
        self.useNormUnits = False
    
    def allowNormUnits(self, value)  :
        self.useNormUnits = value
        
        
    def setPlasmaDensity(self, dens):
        #[dens] = 10^18 cm^-3
        self.n_p = dens * 1e24
        self.w_p = math.sqrt(self.n_p * (self.e)**2 / (self.m_e * self.eps_0)) #plasma freq (1/s)
        self.k_p = self.c / self.w_p  #skin depth (m)
        self.E0 = self.c * self.m_e * self.w_p / self.e # cold non-relativistic field in V/m
        
    def getFieldUnitsOptions(self, field):
        fieldName = field.GetName()
        speciesName = field.GetSpeciesName()
        if self.useNormUnits:
            if speciesName == "":
                if "e1" in fieldName or "e2" in fieldName or "e3" in fieldName:
                    return ["Norm", "V/m", "GV/m"]
                else:
                    return ["Norm"]
            elif "charge" in fieldName:
                return ["Norm", "C/m^2", "n/n_0"]
            else:
                return ["Norm"]
        else:
            return ["Norm"]
            
    def getFieldInUnits(self, fieldName, fieldData, units):
        
        if "e1" in fieldName or "e2" in fieldName or "e3" in fieldName:
            if units == "Norm":
                pass
            elif units == "V/m":
                fieldData *= self.E0
            elif units == "GV/m":
                fieldData *= self.E0 *1e-9
            else:
                pass
                
        elif "charge" in fieldName:
            if units == "Norm":
                pass
            elif units == "C/m^2":
                fieldData *= self.e * (self.w_p / self.c)**2
            elif units == "n/n_0":
                fieldData = abs(fieldData)
            else:
                pass
        else:
            pass  
    
    def getAxisUnitsOptions(self):
        if self.useNormUnits:
            return  ["Norm", "m", "μm"]    
        else:
            return ["Norm"]
            
    def getAxisInUnits(self, extent, units):
        if units == "Norm":
            pass
        elif units == "m":
            extent *= self.c / self.w_p 
        elif units == "μm":
            extent *= 1e6 * self.c / self.w_p 
            
    def GetPlotDataInUnits(self, timeStep, field, fieldUnits, axisUnits):
        fieldName = field.GetName()
        data = field.GetPlotData(timeStep)
        fieldData = data[0]
        extent = np.array(data[1])
        units = list(data[2])
        
        self.getFieldInUnits(fieldName, fieldData, fieldUnits)
        self.getAxisInUnits(extent, axisUnits)
        if axisUnits != "Norm":
            units[0] = axisUnits
            units[1] = axisUnits
        else:
            units[0] = units[0][2:-1].replace("\\\\","\\")
            units[1] = units[1][2:-1].replace("\\\\","\\")
        if fieldUnits != "Norm":
            units[2] = fieldUnits
        else:
            units[2] = units[2][2:-1].replace("\\\\","\\")
        return fieldData, extent, units
        
        
        