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
        self.folderDataReader = FolderDataReader()

        # species (may contain fields and raw data)
        self.availableSpecies = list()
        self.selectedSpecies = list()
        self.selectedSpeciesFieldName = None
        self.selectedSpeciesFields = list()
        
        # domain fields
        self.availableDomainFields = list()
        self.customDomainFields = list()
        self.selectedDomainField = None
        self.selectedField = None

        self.numberOfTimeSteps = 0
        self.dataLocation = ""
    
    def SetDataFolderLocation(self, folderLocation):
        self.folderDataReader.SetDataLocation(str(folderLocation))
                
    def AddSelectedSpecies(self, speciesName):
        for species in self.availableSpecies:
            if species.GetName() == speciesName:
                self.selectedSpecies.append(species)
         
    def RemoveSelectedSpecies(self, speciesName):
        for species in self.selectedSpecies:
            if species.GetName() == speciesName:
                self.selectedSpecies.remove(species)

    def SetSelectedSpecies(self, speciesList):
        if speciesList is list:
            self.selectedSpecies = speciesList;
    
    def SetSelectedSpeciesFields(self):
        self.selectedSpeciesFields[:] = []
        for species in self.selectedSpecies:
            self.selectedSpeciesFields.append(species.GetField(self.selectedSpeciesFieldName))
            self.numberOfTimeSteps = species.GetField(self.selectedSpeciesFieldName).GetTotalTimeSteps()
            
    def SetSelectedSpeciesField(self, fieldName):
        self.selectedSpeciesFieldName = fieldName
    
    def GetAvailableSpecies(self):
        return self.availableSpecies
        
    def GetSpeciesWithRawData(self):
        speciesList = list()
        for species in self.availableSpecies:
            if species.HasRawData():
                speciesList.append(species)
        return speciesList
        
    def GetAvailableSpeciesNames(self):
        namesList = list()
        for species in self.availableSpecies:
            namesList.append(species.GetName())
        return namesList

    def GetSelectedSpecies(self):
        return self.selectedSpecies  
        
    def GetAvailableDomainFields(self):
        return self.availableDomainFields
        
    def GetAvailableDomainFieldsNames(self):
        namesList = list()
        for field in self.availableDomainFields:
            namesList.append(field.GetName())
        return namesList
        
    def GetAvailableFieldsInSpecies(self, speciesName):
        for species in self.availableSpecies:
            if species.GetName() == speciesName:
                return species.GetAvailableFieldNamesList()
                
    def GetDomainField(self, fieldName):
        for field in self.availableDomainFields:
            if field.GetName() == fieldName:
                return field
                
    def GetSpeciesField(self, speciesName, fieldName):
        for species in self.availableSpecies:
            if species.GetName() == speciesName:
                return species.GetField(fieldName)
                
    def GetFolderPath(self):
        return self.folderDataReader.GetDataLocation()
    
    def SetNumberOfTimeSteps(self, number):
        if isinstance(number, int):
            self.numberOfTimeSteps = number;
            
    def GetNumberOfTimeSteps(self):
        return self.numberOfTimeSteps
        
    def SetSelectedDomainField(self, fieldName):
        for field in self.availableDomainFields:
            if field.GetName() == fieldName:
                self.selectedDomainField = field
                self.numberOfTimeSteps = self.selectedDomainField.GetTotalTimeSteps()
    
    def GetSelectedDomainField(self):
        # return a list to keep consistency with GetSelectedSpeciesFields()
        fldList = list()
        fldList.append(self.selectedDomainField)
        return fldList;
            
    def GetSelectedDomainFieldName(self):
        return self.selectedDomainField.GetName();

    def GetSelectedSpeciesFields(self):
        return self.selectedSpeciesFields
        
    def GetCommonlyAvailableFields(self):
        commonlyAvailableFields = list()
        fieldsToRemove = list()
        i = 0
        for species in self.selectedSpecies:
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
        self.availableSpecies = list()
        self.availableDomainFields = list()
        self.customDomainFields = list()
        self.selectedSpecies = list()
        self.selectedDomainField = None
        self.selectedSpeciesFieldName = None
        self.numberOfTimeSteps = 0