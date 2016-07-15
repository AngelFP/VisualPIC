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

import h5py

class Field:
    
    def __init__(self, name, location, totalTimeSteps, speciesName="", isRaw = False, internalName = ""):
        
        self.name = name
        self.location = location
        self.speciesName = speciesName
        self.totalTimeSteps = totalTimeSteps
        self.isRaw = isRaw
        self.internalName = internalName
        # si es raw se cargara de una forma y si no, de otra
        
        
    def LoadData(self, timeStep):
            
        if self.isRaw:
            fileName = "RAW-"
            
        else:
            fileName = self.name + "-"
            
        if self.speciesName != "":
            fileName += self.speciesName + "-"
        
        fileName += str(timeStep).zfill(6)
            
        ending = ".h5"
        
        file_path = self.location + "/" + fileName + ending

        file_content = h5py.File(file_path, 'r')
        
        self.LoadFieldData(file_content)

        self.LoadDimensions(file_content)
        
        self.LoadUnits(file_content)
        
        file_content.close()
        
    def LoadFieldData(self,file_content):
        
        if not self.isRaw:
            self.internalName = "/" + list(file_content.keys())[1]
        
        self.fieldData = file_content[self.internalName][()] #the [()] ending means we get all the data as an array, otherwise we only get some chunks (more efficient, but its not an array, and thus we cant transpose it) 
        
    def LoadDimensions(self, file_content):
        
        self.xMin = file_content.attrs['XMIN']
        self.xMax = file_content.attrs['XMAX']
        
    def LoadUnits(self, file_content):
        self.x1Units = str(list(file_content['/AXIS/AXIS1'].attrs["UNITS"])[0])
        self.x2Units = str(list(file_content['/AXIS/AXIS2'].attrs["UNITS"])[0])
        self.fieldUnits = str(list(file_content[self.internalName].attrs["UNITS"])[0])
        
        
    def GetExtent(self):
        axisExtent = [self.xMin[0],self.xMax[0], self.xMin[1],self.xMax[1]]
        return axisExtent
        
    def GetFieldValues(self):
        
        return self.fieldData
        
    def GetUnits(self):
        return self.x1Units, self.x2Units, self.fieldUnits
        
    def GetPlotData(self, timeStep):
        
        self.LoadData(timeStep)
        
        return self.GetFieldValues(), self.GetExtent(), self.GetUnits()
        
    def GetName(self):
        return self.name
        
    def GetTotalTimeSteps(self):
        
        return self.totalTimeSteps
        
    def GetSpeciesName(self):
        return self.speciesName
        