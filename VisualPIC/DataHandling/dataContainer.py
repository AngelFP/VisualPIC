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

from VisualPIC.DataReading.folderDataReader import FolderDataReader


class DataContainer:
    
    def __init__(self):
        self.__folderDataReader = FolderDataReader()
        # species (may contain fields and raw data)
        self.__availableSpecies = list()
        self.__selectedSpecies = list()
        self.__selectedSpeciesFieldName = None
        self.__selectedSpeciesFields = list()
        # domain fields
        self.__availableDomainFields = list()
        self.__selectedDomainField = None
        self.__numberOfTimeSteps = 0
    
    def LoadData(self):
        self.__availableSpecies, self.__availableDomainFields = self.__folderDataReader.LoadData()

    def SetDataFolderLocation(self, folderLocation):
        self.__folderDataReader.SetDataLocation(str(folderLocation))
                
    def AddSelectedSpecies(self, speciesName):
        for species in self.__availableSpecies:
            if species.GetName() == speciesName:
                self.__selectedSpecies.append(species)
         
    def RemoveSelectedSpecies(self, speciesName):
        for species in self.__selectedSpecies:
            if species.GetName() == speciesName:
                self.__selectedSpecies.remove(species)

    def SetSelectedSpecies(self, speciesList):
        if speciesList is list:
            self.__selectedSpecies = speciesList;
    
    def SetSelectedSpeciesFields(self):
        self.__selectedSpeciesFields[:] = []
        for species in self.__selectedSpecies:
            self.__selectedSpeciesFields.append(species.GetField(self.__selectedSpeciesFieldName))
            self.__numberOfTimeSteps = species.GetField(self.__selectedSpeciesFieldName).GetTotalTimeSteps()
            
    def SetSelectedSpeciesField(self, fieldName):
        self.__selectedSpeciesFieldName = fieldName
    
    def GetAvailableSpecies(self):
        return self.__availableSpecies
        
    def GetSpeciesWithRawData(self):
        speciesList = list()
        for species in self.__availableSpecies:
            if species.HasRawData():
                speciesList.append(species)
        return speciesList
        
    def GetAvailableSpeciesNames(self):
        namesList = list()
        for species in self.__availableSpecies:
            namesList.append(species.GetName())
        return namesList

    def GetSelectedSpecies(self):
        return self.__selectedSpecies  
        
    def GetAvailableDomainFields(self):
        return self.__availableDomainFields
        
    def GetAvailableDomainFieldsNames(self):
        namesList = list()
        for field in self.__availableDomainFields:
            namesList.append(field.GetName())
        return namesList
        
    def GetAvailableFieldsInSpecies(self, speciesName):
        for species in self.__availableSpecies:
            if species.GetName() == speciesName:
                return species.GetAvailableFieldNamesList()
                
    def GetDomainField(self, fieldName):
        for field in self.__availableDomainFields:
            if field.GetName() == fieldName:
                return field
                
    def GetSpeciesField(self, speciesName, fieldName):
        for species in self.__availableSpecies:
            if species.GetName() == speciesName:
                return species.GetField(fieldName)
                
    def GetFolderPath(self):
        return self.__folderDataReader.GetDataLocation()
    
    def SetNumberOfTimeSteps(self, number):
        if isinstance(number, int):
            self.__numberOfTimeSteps = number;
            
    def GetNumberOfTimeSteps(self):
        return self.__numberOfTimeSteps
        
    def SetSelectedDomainField(self, fieldName):
        for field in self.__availableDomainFields:
            if field.GetName() == fieldName:
                self.__selectedDomainField = field
                self.__numberOfTimeSteps = self.__selectedDomainField.GetTotalTimeSteps()
    
    def GetSelectedDomainField(self):
        # return a list to keep consistency with GetSelectedSpeciesFields()
        fldList = list()
        fldList.append(self.__selectedDomainField)
        return fldList;
            
    def GetSelectedDomainFieldName(self):
        return self.__selectedDomainField.GetName();

    def GetSelectedSpeciesFields(self):
        return self.__selectedSpeciesFields
        
    def GetCommonlyAvailableFields(self):
        commonlyAvailableFields = list()
        fieldsToRemove = list()
        i = 0
        for species in self.__selectedSpecies:
            if i == 0:
                commonlyAvailableFields = species.GetAvailableFieldNamesList()
            else:
                speciesFields =  species.GetAvailableFieldNamesList()
                for field in commonlyAvailableFields:
                    if field not in speciesFields:
                        fieldsToRemove.append(field)
            i+=1
        for field in fieldsToRemove:
            commonlyAvailableFields.remove(field)
        return commonlyAvailableFields

    def ClearData(self):
        self.__availableSpecies = list()
        self.__availableDomainFields = list()
        self.__selectedSpecies = list()
        self.__selectedDomainField = None
        self.__selectedSpeciesFieldName = None
        self.__numberOfTimeSteps = 0