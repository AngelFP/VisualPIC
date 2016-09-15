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
    """Contains all the fields and rawDataSets available on the simulation folder"""
    def __init__(self):
        self._folderDataReader = FolderDataReader(self)
        self._simulationCode = ""
        # species (may contain fields and raw data)
        self._availableSpecies = list()
        self._selectedSpecies = list()
        self._selectedSpeciesFieldName = None
        self._selectedSpeciesFields = list()
        # domain fields
        self._availableDomainFields = list()
        self._selectedDomainField = None
    
    def LoadData(self):
        self._folderDataReader.LoadData()

    def SetDataFolderLocation(self, folderLocation):
        self._folderDataReader.SetDataLocation(str(folderLocation))

    def GetSimulationCodeName(self):
        return self._simulationCode
                
    def AddSelectedSpecies(self, speciesName):
        for species in self._availableSpecies:
            if species.GetName() == speciesName:
                self._selectedSpecies.append(species)
         
    def RemoveSelectedSpecies(self, speciesName):
        for species in self._selectedSpecies:
            if species.GetName() == speciesName:
                self._selectedSpecies.remove(species)

    def SetSelectedSpecies(self, speciesList):
        if speciesList is list:
            self._selectedSpecies = speciesList;
    
    def SetSelectedSpeciesFields(self):
        self._selectedSpeciesFields[:] = []
        for species in self._selectedSpecies:
            self._selectedSpeciesFields.append(species.GetField(self._selectedSpeciesFieldName))
            
    def SetSelectedSpeciesField(self, fieldName):
        self._selectedSpeciesFieldName = fieldName
    
    def GetAvailableSpecies(self):
        return self._availableSpecies
        
    def GetSpeciesWithRawData(self):
        speciesList = list()
        for species in self._availableSpecies:
            if species.HasRawData():
                speciesList.append(species)
        return speciesList

    def GetSpeciesWithTrackingData(self):
        speciesList = list()
        for species in self._availableSpecies:
            if species.HasRawDataTags():
                speciesList.append(species)
        return speciesList
        
    def GetAvailableSpeciesNames(self):
        namesList = list()
        for species in self._availableSpecies:
            namesList.append(species.GetName())
        return namesList

    def GetSelectedSpecies(self):
        return self._selectedSpecies  
        
    def GetAvailableDomainFields(self):
        return self._availableDomainFields
        
    def GetAvailableDomainFieldsNames(self):
        namesList = list()
        for field in self._availableDomainFields:
            namesList.append(field.GetName())
        return namesList
        
    def GetAvailableFieldsInSpecies(self, speciesName):
        for species in self._availableSpecies:
            if species.GetName() == speciesName:
                return species.GetAvailableFieldNamesList()
                
    def GetDomainField(self, fieldName):
        for field in self._availableDomainFields:
            if field.GetName() == fieldName:
                return field
                
    def GetSpeciesField(self, speciesName, fieldName):
        for species in self._availableSpecies:
            if species.GetName() == speciesName:
                return species.GetField(fieldName)
    
    def GetSpeciesRawDataSet(self, speciesName, dataSetName):
        for species in self._availableSpecies:
            if species.GetName() == speciesName:
                return species.GetRawDataSet(dataSetName)
                
    def GetFolderPath(self):
        return self._folderDataReader.GetDataLocation()
        
    def SetSelectedDomainField(self, fieldName):
        for field in self._availableDomainFields:
            if field.GetName() == fieldName:
                self._selectedDomainField = field
    
    def GetSelectedDomainField(self):
        # return a list to keep consistency with GetSelectedSpeciesFields()
        fldList = list()
        fldList.append(self._selectedDomainField)
        return fldList;
            
    def GetSelectedDomainFieldName(self):
        return self._selectedDomainField.GetName();

    def GetSelectedSpeciesFields(self):
        return self._selectedSpeciesFields
        
    def GetCommonlyAvailableFields(self):
        commonlyAvailableFields = list()
        fieldsToRemove = list()
        i = 0
        for species in self._selectedSpecies:
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
        self._availableSpecies = list()
        self._availableDomainFields = list()
        self._selectedSpecies = list()
        self._selectedDomainField = None
        self._selectedSpeciesFieldName = None