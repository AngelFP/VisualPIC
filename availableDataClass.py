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

from speciesClass import Species
from fieldClass import Field
import os
import h5py

class AvailableData:
    
    def __init__(self):
        
        # species fields
        self.availableSpecies = list()
        self.selectedSpecies = list()
        self.selectedSpeciesFieldName = None
        self.selectedSpeciesFields = list()
        
        # domain fields
        self.availableDomainFields = list()
        self.customDomainFields = list()
        self.selectedDomainField = None
        self.selectedField = None
        
        # raw fields
        self.availableRawSpecies = list()
        #self.selectedRawSpecies = list()
        #self.selectedSpeciesRawFields = list()

        self.numberOfTimeSteps = 0
        self.dataLocation = ""
        
    def AddSpecies(self, species):
        
        if isinstance(species, Species):
            addSpecies = True
            for avSpecies in self.availableSpecies:
                if avSpecies.GetName() == species.GetName():
                    addSpecies =  False
            if addSpecies:
                self.availableSpecies.append(species)
                
    def AddRawSpecies(self, species):
        
        if isinstance(species, Species):
            addSpecies = True
            for avSpecies in self.availableRawSpecies:
                if avSpecies.GetName() == species.GetName():
                    addSpecies =  False
            if addSpecies:
                self.availableRawSpecies.append(species)
            
    def AddSelectedSpecies(self, speciesName):
        
        for species in self.availableSpecies:
            if species.GetName() == speciesName:
                self.selectedSpecies.append(species)
         
    def RemoveSelectedSpecies(self, speciesName):
        
        for species in self.selectedSpecies:
            if species.GetName() == speciesName:
                self.selectedSpecies.remove(species)
    
    def AddFieldToSpecies(self, speciesName, field):
        
        for species in self.availableSpecies:
            if species.GetName() == speciesName:
                species.AddAvailableField(field)
                
    def AddFieldToRawSpecies(self, speciesName, field):
        
        for species in self.availableRawSpecies:
            if species.GetName() == speciesName:
                species.AddAvailableField(field)

    def SetSelectedSpecies(self, speciesList):
        if speciesList is list:
            self.selectedSpecies = speciesList;
    
    def SetSelectedSpeciesFields(self):
        self.selectedSpeciesFields.clear()
        for species in self.selectedSpecies:
            self.selectedSpeciesFields.append(species.GetField(self.selectedSpeciesFieldName))
            
    def SetSelectedSpeciesField(self, fieldName):
        self.selectedSpeciesFieldName = fieldName

	
    def AddDomainField(self,field):
        
        if isinstance(field, Field):
            self.availableDomainFields.append(field)
            
    def AddCustomField(self, field):
        
        if field is Field:
            self.customDomainFields.append(field)
    
    def GetAvailableSpecies(self):

        return self.availableSpecies
        
    def GetAvailableRawSpecies(self):

        return self.availableRawSpecies
        
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
        
    def GetCustomDomainFields(self):
        
        return self.customDomainFields
        
    def GetAvailableFieldsInSpecies(self, speciesName):
        
        for species in self.availableSpecies:
            if species.GetName() == speciesName:
                return species.GetAvailableFieldNamesList()
                
    def GetFolderPath(self):
        
        return self.dataLocation
    
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
    
    def SetDataFolderLocation(self, folderLocation):
        
        self.dataLocation = folderLocation
        
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
        
    # Data loading methods
    
    def LoadFolderData(self):
        
        self.ClearData()
        
        keyFolderNames = ["DENSITY", "FLD", "PHA", "RAW" ]
        
        #completeSubfolderList = list(os.walk(self.dataLocation))
        
        mainFolders = os.listdir(self.dataLocation)
        
        for folder in mainFolders:
            subDir = self.dataLocation + "/" + folder
            
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
                                self.AddFieldToSpecies(species, Field(fieldName, fieldLocation, totalTimeSteps, species))
                        
            elif folder == keyFolderNames[1]:
                domainFields = os.listdir(subDir)
                for field in domainFields:
                    if os.path.isdir(os.path.join(subDir, field)):
                        fieldLocation = subDir + "/" + field
                        fieldName = field
                        totalTimeSteps = len(os.listdir(fieldLocation))
                        self.AddDomainField(Field(fieldName, fieldLocation, totalTimeSteps))
            
            elif folder ==  keyFolderNames[2]:
                phaseFields = os.listdir(subDir)
                for field in phaseFields:
                    if os.path.isdir(os.path.join(subDir, field)):
                        speciesNames = os.listdir(subDir + "/" + field)
                        for species in speciesNames:
                            if os.path.isdir(os.path.join(subDir + "/" + field, species)):
                                self.AddSpecies(Species(species))
                                fieldLocation = subDir + "/" + field + "/" + species
                                fieldName = field
                                totalTimeSteps = len(os.listdir(fieldLocation))
                                self.AddFieldToSpecies(species, Field(fieldName, fieldLocation, totalTimeSteps, species))
            
            elif folder ==  keyFolderNames[3]:
                subDir = self.dataLocation + "/" + folder
                self.LoadRawFields(subDir)
                        
    def LoadRawFields(self, subDir):
        speciesNames = os.listdir(subDir)
        for species in speciesNames:
            if os.path.isdir(os.path.join(subDir, species)):
                self.AddRawSpecies(Species(species))
                fieldLocation = subDir + "/" + species
                totalTimeSteps = len(os.listdir(fieldLocation))
                
                file_path = fieldLocation + "/" + "RAW-" + species + "-000000.h5"
                file_content = h5py.File(file_path, 'r')
                for fieldName in list(file_content):
                    self.AddFieldToRawSpecies(species, Field(fieldName, fieldLocation, totalTimeSteps, species, True, fieldName))