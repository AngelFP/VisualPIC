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


import os
from h5py import File as H5File
import numpy as np

from VisualPIC.DataHandling.species import Species
from VisualPIC.DataHandling.folderDataElements import FolderField, FolderRawDataSet
from VisualPIC.DataHandling.rawDataTags import RawDataTags
from VisualPIC.DataReading.openPMDTimeSeriesSingleton import OpenPMDTimeSeriesSingleton, openpmd_installed

class FolderDataReader:
    """Scans the simulation folder and creates all the necessary species, fields and rawDataSet objects"""
    def __init__(self, parentDataContainer):
        self._dataContainer = parentDataContainer
        self._dataLocation = ""
        self._loadDataFrom = {"Osiris": self.LoadOsirisData,
                               "HiPACE": self.LoadHiPaceData,
                               "openPMD": self.LoadOpenPMDData }

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


    # openPMD
    def LoadOpenPMDData(self):
        """OpenPMD Loader"""
        # First check whether openPMD is installed
        if not openpmd_installed:
            raise RunTimeError("You need to install openPMD-viewer, e.g. with:\n"
                "pip install openPMD-viewer")
        # Scan the folder using openPMD-viewer
        ts = OpenPMDTimeSeriesSingleton( self._dataLocation, check_all_files=False, reset=True )

        # TODO: Change hasNonISUnits to False once unit reading is implemented
        # Register the available fields
        if ts.avail_fields is not None:
            for field in ts.avail_fields:
                # Vector field
                if ts.fields_metadata[field]['type'] == 'vector':
                    available_coord = ts.fields_metadata[field]['axis_labels']
                    if ts.fields_metadata[field]['geometry'] == 'thetaMode':
                        available_coord += ['x', 'y']
                    # Register each coordinate of the vector
                    for coord in available_coord:
                        fieldName = field + '/' + coord
                        standardName = self.GiveStandardNameForOpenPMDQuantity(fieldName)
                        self.AddDomainField(
                            FolderField( "openPMD", fieldName, standardName,
                                        self._dataLocation, ts.iterations,
                                        hasNonISUnits = True ) )
                # Scalar field
                if ts.fields_metadata[field]['type'] == 'scalar':
                    fieldName = field
                    standardName = self.GiveStandardNameForOpenPMDQuantity(field)
                    self.AddDomainField(
                        FolderField( "openPMD", fieldName, standardName,
                                    self._dataLocation, ts.iterations,
                                    hasNonISUnits = True ) )

        # Register the available species
        if ts.avail_species is not None:
            for species in ts.avail_species:
                self.AddSpecies(Species(species))
                for species_quantity in ts.avail_record_components[species]:
                    if species_quantity == "id":
                        self.AddRawDataTagsToSpecies( species,
                            RawDataTags( "openPMD", species_quantity,
                                self._dataLocation, ts.iterations,
                                species, species_quantity) )
                    else:
                        self.AddRawDataToSpecies( species,
                            FolderRawDataSet( "openPMD", species_quantity,
                                self.GiveStandardNameForOpenPMDQuantity(species_quantity),
                                self._dataLocation, ts.iterations,
                                species, species_quantity, hasNonISUnits = True) )

    def GetTimeStepsInOpenPMDLocation(self, location):
        ts = OpenPMDTimeSeriesSingleton( location, check_all_files=False )
        return ts.iterations

    def GiveStandardNameForOpenPMDQuantity(self, openpmdName):
        if "E/z" in openpmdName:
            return "Ez"
        elif "E/y" in openpmdName:
            return "Ey"
        elif "E/x" in openpmdName:
            return "Ex"
        elif "E/r" in openpmdName:
            return "Er"
        elif "B/z" in openpmdName:
            return "Bz"
        elif "B/y" in openpmdName:
            return "By"
        elif "B/x" in openpmdName:
            return "Bx"
        elif "B/r" in openpmdName:
            return "Br"
        elif "rho" in openpmdName:
            return "Charge density"
        elif openpmdName == "uz":
            return "Pz"
        elif openpmdName == "uy":
            return "Py"
        elif openpmdName == "ux":
            return "Px"
        elif openpmdName == "charge":
            return "Charge"
        else:
            return openpmdName
