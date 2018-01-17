# -*- coding: utf-8 -*-

#Copyright 2016-2017 Angel Ferran Pousa, DESY
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
from h5py import File as H5File
import numpy as np

from VisualPIC.DataHandling.species import Species
from VisualPIC.DataHandling.folderDataElements import FolderField, FolderRawDataSet
from VisualPIC.DataHandling.rawDataTags import RawDataTags


class FolderDataReader:
    """Scans the simulation folder and creates all the necessary species, fields and rawDataSet objects"""
    def __init__(self, parentDataContainer):
        self._dataContainer = parentDataContainer
        self._dataLocation = ""
        self._loadDataFrom = {"Osiris": self.LoadOsirisData,
                               "HiPACE": self.LoadHiPaceData,
                               "PIConGPU":self.LoadPIConGPUData}

    def SetDataLocation(self, dataLocation):
        self._dataLocation = dataLocation

    def GetDataLocation(self):
        return self._dataLocation

    """
    Data managing. Methods for adding the detected species, fields...
    """
    def AddSpecies(self, species):
        addSpecies = True
        # the species will not be added if it already exists
        for avSpecies in self._dataContainer._availableSpecies:
            if avSpecies.GetName() == species.GetName():
                addSpecies =  False
        if addSpecies:
            self._dataContainer._availableSpecies.append(species)

    def AddFieldToSpecies(self, speciesName, field):
        for species in self._dataContainer._availableSpecies:
            if species.GetName() == speciesName:
                species.AddAvailableField(field)

    def AddRawDataToSpecies(self, speciesName, dataSet):
        for species in self._dataContainer._availableSpecies:
            if species.GetName() == speciesName:
                species.AddRawDataSet(dataSet)

    def AddRawDataTagsToSpecies(self, speciesName, tags):
        for species in self._dataContainer._availableSpecies:
            if species.GetName() == speciesName:
                species.AddRawDataTags(tags)

    def AddDomainField(self,field):
        self._dataContainer._availableDomainFields.append(field)

    """
    Main data loader. It will automatically call the specific loader for a particular simulation code
    """
    def LoadData(self, simulationCode):
        self._loadDataFrom[simulationCode]()

    """
    Specific data loaders
    """
    # OSIRIS
    def LoadOsirisData(self):
        """Osiris Loader"""
        keyFolderNames = ["DENSITY", "FLD", "PHA", "RAW" ]
        mainFolders = os.listdir(self._dataLocation)
        for folder in mainFolders:
            subDir = self._dataLocation + "/" + folder
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
                                timeSteps = self.GetTimeStepsInOsirisLocation(fieldLocation)
                                if timeSteps.size != 0:
                                    self.AddFieldToSpecies(species, FolderField("Osiris", fieldName, self.GiveStandardNameForOsirisQuantity(fieldName), fieldLocation, timeSteps, species))
            elif folder == keyFolderNames[1]:
                domainFields = os.listdir(subDir)
                for field in domainFields:
                    if os.path.isdir(os.path.join(subDir, field)):
                        fieldLocation = subDir + "/" + field
                        fieldName = field
                        timeSteps = self.GetTimeStepsInOsirisLocation(fieldLocation)
                        if timeSteps.size != 0:
                            self.AddDomainField(FolderField("Osiris", fieldName, self.GiveStandardNameForOsirisQuantity(fieldName), fieldLocation, timeSteps))
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
            #                    self.AddFieldToSpecies(species, FolderField(fieldName, fieldLocation, totalTimeSteps, species, simulationCode = self._codeName))
            elif folder ==  keyFolderNames[3]:
                subDir = self._dataLocation + "/" + folder
                speciesNames = os.listdir(subDir)
                for species in speciesNames:
                    if os.path.isdir(os.path.join(subDir, species)):
                        self.AddSpecies(Species(species))
                        dataSetLocation = subDir + "/" + species
                        timeSteps = self.GetTimeStepsInOsirisLocation(dataSetLocation)
                        if timeSteps.size != 0:
                            file_path = dataSetLocation + "/" + "RAW-" + species + "-" + str(timeSteps[0]).zfill(6) + ".h5"
                            file_content = H5File(file_path, 'r')
                            for dataSetName in list(file_content):
                                if dataSetName == "tag":
                                    self.AddRawDataTagsToSpecies(species, RawDataTags("Osiris", dataSetName, dataSetLocation, timeSteps, species, dataSetName))
                                else:
                                    self.AddRawDataToSpecies(species, FolderRawDataSet("Osiris", dataSetName, self.GiveStandardNameForOsirisQuantity(dataSetName), dataSetLocation, timeSteps, species, dataSetName))
                            file_content.close()

    def GetTimeStepsInOsirisLocation(self, location):
        fileNamesList = os.listdir(location)
        # filter only .h5 files
        h5Files = list()
        for file in fileNamesList:
            if file.endswith(".h5"):
                h5Files.append(file)
        timeSteps = np.zeros(len(h5Files))
        i = 0
        for file in h5Files:
            timeStep = int(file[-9:-3])
            timeSteps[i] = timeStep
            i+=1
        timeSteps = timeSteps.astype(np.int64)
        timeSteps.sort()
        return timeSteps

    def GiveStandardNameForOsirisQuantity(self, osirisName):
        if "e1" in osirisName:
            return "Ez"
        elif "e2" in osirisName:
            return "Ey"
        elif "e3" in osirisName:
            return "Ex"
        elif "b1" in osirisName:
            return "Bz"
        elif "b2" in osirisName:
            return "By"
        elif "b3" in osirisName:
            return "Bx"
        elif "charge" in osirisName:
            return "Charge density"
        elif osirisName == "x1":
            return "z"
        elif osirisName == "x2":
            return "y"
        elif osirisName == "x3":
            return "x"
        elif osirisName == "p1":
            return "Pz"
        elif osirisName == "p2":
            return "Py"
        elif osirisName == "p3":
            return "Px"
        elif osirisName == "q":
            return "Charge"
        elif osirisName == "ene":
            return "Energy"
        else:
            return osirisName

    # HiPACE
    def LoadHiPaceData(self):
        """HiPACE loader"""
        data_folder = self._dataLocation
        data_types = ['density', 'field', 'raw']
        
        files_in_folder = os.listdir(data_folder)

        for data_type in data_types:
            if data_type == 'field':
                data_files = list()
                data_names = list()
                for file in files_in_folder:
                    if file.endswith(".h5") and data_type in file:
                        data_files.append(file)
                        data_name = file.replace(data_type + '_', '')[0:-10]
                        if data_name not in data_names:
                            data_names.append(data_name)
                for data_name in data_names:
                    data_time_steps = list()
                    for file in data_files:
                        if data_name in file:
                            time_step = int(file[-9, -3])
                            data_time_steps.append(time_step)
                    data_time_steps = np.array(data_time_steps)
                    self.AddDomainField(FolderField("HiPACE", data_name, self.GiveStandardNameForHiPACEQuantity(data_name), data_folder, data_time_steps))
            
            if data_type == 'density':
                data_name = 'charge'
                data_files = list()
                species_names = list()
                for file in files_in_folder:
                    if file.endswith(".h5") and data_type in file:
                        data_files.append(file)
                        species_name = file.replace(data_type + '_', '').replace('_' + data_name + '_', '')[0:-9]
                        if species_name not in species_names:
                            species_names.append(species_name)
                for species_name in species_names:
                    self.AddSpecies(Species(species_name))
                    data_time_steps = list()
                    for file in data_files:
                        if species_name in file:
                            time_step = int(file[-9:-3])
                            data_time_steps.append(time_step)
                    data_time_steps = np.array(data_time_steps)
                    self.AddFieldToSpecies(species_name, FolderField("HiPACE", data_name, self.GiveStandardNameForOsirisQuantity(data_name), data_folder, data_time_steps, species_name))
            
            if data_type == 'raw':
                data_files = list()
                species_names = list()
                for file in files_in_folder:
                    if file.endswith(".h5") and data_type in file:
                        data_files.append(file)
                        species_name = file.replace(data_type + '_', '')[0:-10]
                        if species_name not in species_names:
                            species_names.append(species_name)


                for species_name in species_names:
                    self.AddSpecies(Species(species_name))
                    data_time_steps = list()
                    for file in data_files:
                        if species_name in file:
                            time_step = int(file[-9:-3])
                            data_time_steps.append(time_step)
                    data_time_steps = np.array(data_time_steps)
                    if data_time_steps.size != 0:
                        file_path = data_folder + '/' + data_type + '_' + species_name + '_' + str(data_time_steps[0]).zfill(6) + '.h5'
                        file_content = H5File(file_path, 'r')
                        for data_set_name in list(file_content):
                            if data_set_name == "tag":
                                self.AddRawDataTagsToSpecies(species_name, RawDataTags("HiPACE", data_set_name, data_folder, data_time_steps, species_name, data_set_name))
                            else:
                                self.AddRawDataToSpecies(species_name, FolderRawDataSet("HiPACE", data_set_name, self.GiveStandardNameForHiPACEQuantity(data_set_name), data_folder, data_time_steps, species_name, data_set_name))
                        file_content.close()

    def GiveStandardNameForHiPACEQuantity(self, original_name):
        if "Ez" in original_name:
            return "Ez"
        elif "charge" in original_name:
            return "Charge density"
        elif original_name == "x1":
            return "z"
        elif original_name == "x2":
            return "y"
        elif original_name == "x3":
            return "x"
        elif original_name == "p1":
            return "Pz"
        elif original_name == "p2":
            return "Py"
        elif original_name == "p3":
            return "Px"
        elif original_name == "q":
            return "Charge"
        elif original_name == "ene":
            return "Energy"
        else:
            return original_name


    # PIConGPU
    def LoadPIConGPUData(self):
        """PIConGPU loader"""
        raise NotImplementedError
        """
        HOW TO USE:
        
        This function has to scan the folder where the simulation data is stored.
        It will create a Species, FolderField, FolderRawDataSet or RawDataTags object for each
        species, field, raw (particle) data set and particle tags found in the folder.

        To add these data into the dataContainer the following functions have to be used:

        self.AddSpecies(..)
        self.AddFieldToSpecies(..)
        self.AddDomainField(..)
        self.AddRawDataToSpecies(..)
        self.AddRawDataTagsToSpecies(..)
        """