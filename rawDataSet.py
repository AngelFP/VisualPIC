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

class RawDataSet:
    
    def __init__(self, name, location, totalTimeSteps, speciesName, internalName = ""):
        
        self.name = name
        self.location = location
        self.speciesName = speciesName
        self.totalTimeSteps = totalTimeSteps
        self.internalName = internalName
        self.LoadBasicData()
        
    def LoadBasicData(self):
        fileName = "RAW-" + self.speciesName + "-" + str(0).zfill(6)
            
        ending = ".h5"
        
        file_path = self.location + "/" + fileName + ending

        file_content = h5py.File(file_path, 'r')
        
        self.LoadUnits(file_content)
        
        file_content.close()
        
    def LoadData(self, timeStep):
            
            
        fileName = "RAW-" + self.speciesName + "-" + str(timeStep).zfill(6)
            
        ending = ".h5"
        
        file_path = self.location + "/" + fileName + ending

        file_content = h5py.File(file_path, 'r')
        
        self.LoadRawData(file_content)
        
        self.LoadUnits(file_content)
        
        file_content.close()
        
    def LoadRawData(self,file_content):
        
        self.rawData = file_content[self.internalName][()] #the [()] ending means we get all the data as an array, otherwise we only get some chunks (more efficient, but its not an array, and thus we cant transpose it) 

        
    def LoadUnits(self, file_content):
        self.dataUnits = str(list(file_content[self.internalName].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")
        
    def GetNormalizedUnits(self):
        return self.dataUnits
        
    def GetRawData(self):
        return self.rawData
        
        
    def GetUnits(self):
        return self.dataUnits
        
    def GetPlotData(self, timeStep):
        
        self.LoadData(timeStep)
        
        return self.GetRawData(), self.GetUnits()
        
    def GetName(self):
        return self.name
        
    def GetTotalTimeSteps(self):
        
        return self.totalTimeSteps
        
    def GetSpeciesName(self):
        return self.speciesName
        