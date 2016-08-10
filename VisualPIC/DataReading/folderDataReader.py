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

import os
import h5py

from VisualPIC.DataReading.species import Species
from VisualPIC.DataReading.rawDataSet import RawDataSet
from VisualPIC.DataReading.field import Field


class FolderDataReader:
    """Scans the simulation folder and creates all the necessary species, fields and rawDataSets objects"""
    def __init__(self):
        self.__dataLocation = ""
        self.__availableSpecies = list()
        self.__availableFields = list()
        self.CreateCodeDictionaries()
    
    def CreateCodeDictionaries(self):
        self.__codeName = {"MS":"Osiris",
                           "Something":"HiPACE"}
        self.__loadDataFrom = {"Osiris": self.LoadOsirisData,
                               "HiPACE": self.LoadHiPaceData}
    def SetDataLocation(self, dataLocation):
        self.__dataLocation = dataLocation

    def GetDataLocation(self):
        return self.__dataLocation

    """
    Data managing. Methods for adding the detected species, fields...
    """
    def AddSpecies(self, species):
        addSpecies = True
        # the species will not be added if it already exists
        for avSpecies in self.__availableSpecies:
            if avSpecies.GetName() == species.GetName():
                addSpecies =  False
        if addSpecies:
            self.__availableSpecies.append(species)

    def AddFieldToSpecies(self, speciesName, field):
        for species in self.__availableSpecies:
            if species.GetName() == speciesName:
                species.AddAvailableField(field)

    def AddRawDataToSpecies(self, speciesName, dataSet):
        for species in self.__availableSpecies:
            if species.GetName() == speciesName:
                species.AddRawDataSet(dataSet)

    def AddDomainField(self,field):
        self.__availableFields.append(field)

    """
    Main data loader. It will automatically call the specific loader for a particular simulation code
    """
    def LoadData(self):
        self.__loadDataFrom[self.DetectSimulationCodeName()]()
        return self.__availableSpecies, self.__availableFields

    def DetectSimulationCodeName(self):
        dataFolderName = os.path.basename(self.__dataLocation)
        return self.__codeName[dataFolderName]

    """
    Specific data loaders
    """
    def LoadOsirisData(self):
        """Osiris Loader"""
        keyFolderNames = ["DENSITY", "FLD", "PHA", "RAW" ]
        mainFolders = os.listdir(self.__dataLocation)
        for folder in mainFolders:
            subDir = self.__dataLocation + "/" + folder
            if folder == keyFolderNames[0]:
                speciesNames = os.listdir(subDir)
                for species in speciesNames:
                    if os.path.isdir(os.path.join(subDir, species)):
                        self.AddSpecies(Species(species))
                        speciesFields = os.listdir(subDir + "/" + species)
                        for field in speciesFields:
                            if os.path.isdir(os.path.join(subDir + "/" + species, field)):
                                fieldLocation = subDir + "/" + species + "/" + field
                                fieldName = field
                                totalTimeSteps = len(os.listdir(fieldLocation))
                                self.AddFieldToSpecies(species, Field(fieldName, fieldLocation, totalTimeSteps, species, simulationCode = self.__codeName))
            elif folder == keyFolderNames[1]:
                domainFields = os.listdir(subDir)
                for field in domainFields:
                    if os.path.isdir(os.path.join(subDir, field)):
                        fieldLocation = subDir + "/" + field
                        fieldName = field
                        totalTimeSteps = len(os.listdir(fieldLocation))
                        self.AddDomainField(Field(fieldName, fieldLocation, totalTimeSteps, simulationCode = self.__codeName))
            #elif folder ==  keyFolderNames[2]:
            #    phaseFields = os.listdir(subDir)
            #    for field in phaseFields:
            #        if os.path.isdir(os.path.join(subDir, field)):
            #            speciesNames = os.listdir(subDir + "/" + field)
            #            for species in speciesNames:
            #                if os.path.isdir(os.path.join(subDir + "/" + field, species)):
            #                    self.AddSpecies(Species(species))
            #                    fieldLocation = subDir + "/" + field + "/" + species
            #                    fieldName = field
            #                    totalTimeSteps = len(os.listdir(fieldLocation))
            #                    self.AddFieldToSpecies(species, Field(fieldName, fieldLocation, totalTimeSteps, species, simulationCode = self.__codeName))
            elif folder ==  keyFolderNames[3]:
                subDir = self.__dataLocation + "/" + folder
                speciesNames = os.listdir(subDir)
                for species in speciesNames:
                    if os.path.isdir(os.path.join(subDir, species)):
                        self.AddSpecies(Species(species))
                        dataSetLocation = subDir + "/" + species
                        totalTimeSteps = len(os.listdir(dataSetLocation))
                        file_path = dataSetLocation + "/" + "RAW-" + species + "-000000.h5"
                        file_content = h5py.File(file_path, 'r')
                        for dataSetName in list(file_content):
                            self.AddRawDataToSpecies(species, RawDataSet(dataSetName, dataSetLocation, totalTimeSteps, species, dataSetName, simulationCode = self.__codeName))

    def LoadHiPaceData(self):
        """HiPACE loader"""
        raise NotImplementedError
