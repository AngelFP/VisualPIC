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


import numpy as np
from h5py import File as H5File

from VisualPIC.DataPlotting.rawDataEvolutionToPlot import RawDataEvolutionToPlot
from VisualPIC.DataHandling.selfContainedDataElements import SelfContainedRawDataSet, EvolutionData


class Particle():
    def __init__(self, tag):
        self.tag = tag
        self._time_stepQuantities = {}
        self._wholeSimulationQuantities = {}
        self._particleIndices = None
        self._trackedTimeSteps = []

    def AddTimeStepQuantity(self, quantityName, quantityValue):
        self._time_stepQuantities[quantityName] = quantityValue

    def AddWholeSimulationQuantity(self, dataSet, quantityValues):
        #self._wholeSimulationQuantities[quantityName] = {"values":quantityValues, "units":quantityUnits}
        quantityName = dataSet.get_name()
        quantityUnits = dataSet.get_data_original_units()
        timeValues = self._wholeSimulationQuantities["Time"].get_all_data_in_original_units()
        timeUnits = dataSet.get_time_original_units()
        self._wholeSimulationQuantities[quantityName] = EvolutionData(quantityName, quantityValues, quantityUnits, dataSet.has_non_si_units, timeValues, timeUnits, self._trackedTimeSteps)

    def AddTimeInfo(self, timeValues, timeUnits, has_non_si_units):
        self._wholeSimulationQuantities["Time"] = EvolutionData("Time", timeValues, timeUnits, has_non_si_units, timeValues, timeUnits, self._trackedTimeSteps)

    def GetNamesOfWholeSimulationQuantities(self):
        quantitiesList = list()
        for key in self._wholeSimulationQuantities:
            quantitiesList.append(key)
        return quantitiesList

    def GetNamesOfTimeStepQuantities(self):
        quantitiesList = list()
        for key in self._time_stepQuantities:
            quantitiesList.append(key)
        return quantitiesList

    def GetCurrentTimeStepQuantities(self):
        return self._time_stepQuantities

    def GetWholeSimulationQuantity(self, quantityName):
        return self._wholeSimulationQuantities[quantityName]

    def GetDataAtTimeStep(self, time_step):
        time_stepQuantities = {}
        for key in self._time_stepQuantities:
            time_stepQuantities[key] = self._wholeSimulationQuantities[key][time_step]
        return time_stepQuantities

    def SetTrackedTimeSteps(self, time_steps):
        self._trackedTimeSteps = time_steps

    def GetTrackedTimeSteps(self):
        return self._trackedTimeSteps

    def SetIndices(self, indices):
        self._particleIndices = indices

    def GetIndex(self, time_step):
        return self._particleIndices[np.where(self._trackedTimeSteps == time_step)[0][0]]

    def WriteDataToFile(self, location, fileName):
        h5file = H5File(location + "/" + fileName + ".h5", "w")
        for key in self._wholeSimulationQuantities:
            dataSet = h5file.create_dataset(key, data = self._wholeSimulationQuantities[key].get_all_data_in_si_units())
            dataSet.attrs["Units"] = self._wholeSimulationQuantities[key].get_data_si_units()
        h5file.close()


class ParticleTracker():
    def __init__(self, data_container):
        self._data_container = data_container
        self._speciesList = self._data_container.get_species_with_tracking_data()
        self._speciesToAnalyze = None
        self._particleList = list()
        self._instantRawDataSetsList = list()
        self.timeInfoAdded = False
        self.indexInfoAdded = False
        """
        Explanation:
            To save computational time and not having to look where the particle is in the file for 
        every quantity, a list of indices will be created when the first "WholeSimulationQuantity" 
        is loaded. Therefore, for loading the following quantities, the code will already know where
        the particle is without calling the expensive method "GetParticleIndexFromTag".
            Also, the time will be added as a "WholeSimulationQuantity" when loading the first 
        quantity. In order not to repeat this for every quantity, the boolean variable 
        self.indexInfoAdded is introduced.
        """

    def get_data_location(self):
        return self._data_container.get_folder_path()

    def get_species_names(self):
        names = list()
        for species in self._speciesList:
            names.append(species.get_name())
        return names

    def get_speciesDataSet(self, species_name, dataSetName):
        return self._data_container.get_species_raw_dataset(species_name, dataSetName)

    def get_species_raw_datasetNames(self, species_name):
        for species in self._speciesList:
            if species.get_name() == species_name:
                return species.get_raw_dataset_names_list()

    def GetNamesOfInstantRawDataSets(self):
        names = list()
        for dataSet in self._instantRawDataSetsList:
            names.append(dataSet.get_name())
        return names

    def GetInstantRawDataSet(self, dataSetName):
        for dataSet in self._instantRawDataSetsList:
            if dataSet.get_name() == dataSetName:
                return dataSet

    def FindParticles(self, time_step, species_name, filters):
        """filters is a dictionary where the keys are the names of the variables 
        to filter (eg /q, /x1, etc.) and the values are a tuple with two numbers
        (the lower and higher limit)"""
        for species in self._speciesList:
            if species.get_name() == species_name:
                self._speciesToAnalyze = species
        indicesList = list()
        for rawDataSetName, range in filters.items():
            indicesList.append(self._GetIndicesOfParticlesInRange(time_step, self._speciesToAnalyze, rawDataSetName, range))
        indicesOfFoundParticles = self._GetCommonElementsInListOfArrays(indicesList)
        particles = self._GetParticlesFromIndices(time_step, self._speciesToAnalyze, indicesOfFoundParticles)
        return particles
    
    def _GetIndicesOfParticlesInRange(self, time_step, species, rawDataSetName, range):
        dataSet = species.get_raw_dataset(rawDataSetName)
        data = dataSet.get_data_in_original_units(time_step)
        iLowRange = np.where(data > range[0])
        iHighRange = np.where(data < range[1])
        iRange = np.intersect1d(iLowRange, iHighRange)
        return iRange

    def _GetCommonElementsInListOfArrays(self, listOfArrays):
        n = len(listOfArrays)
        commonEls = listOfArrays[0]
        for i in np.arange(1,n):
            commonEls = np.intersect1d(listOfArrays[i], commonEls)
        return commonEls

    def _GetParticlesFromIndices(self, time_step, species, indices):
        rawDataSets = species.get_all_raw_datasets()
        particleTags = species.get_tags(time_step)
        dataSetValues = {}
        for dataSet in rawDataSets:
            dataSetValues[dataSet.get_name()] = dataSet.get_data_in_original_units(time_step) # particle data in selected time step
        particlesList = list()
        for index in indices:
            particle = Particle(particleTags[index]) # create particle instance with corresponding tag
            for dataSetName, values in dataSetValues.items():
                particle.AddTimeStepQuantity(dataSetName, values[index])
            particlesList.append(particle)
        return particlesList

    def SetParticlesToTrack(self, particleList):
        self._particleList = particleList

    def FillEvolutionOfAllDataSetsInParticles(self):
        self.timeInfoAdded = False
        rawDataSets = self._speciesToAnalyze.get_all_raw_datasets()
        self._FindIndicesOfParticles()
        for dataSet in rawDataSets:
            self._FillEvolutionOfDataSetInParticles(dataSet)

    def _FindIndicesOfParticles(self):
        time_steps = self._speciesToAnalyze.get_raw_data_time_steps()
        trackedParticleTags = self._GetTrackedParticleTags()
        totalTimeSteps = len(time_steps)
        numberOfParticles = len(self._particleList)
        trackedTimeSteps = -np.ones([numberOfParticles, totalTimeSteps], dtype=int)
        particleIndices = -np.ones([numberOfParticles, totalTimeSteps], dtype=int)
        particlesFound = False
        i = 0
        for time_step in time_steps:
            print(time_step)
            try:
                allParticleTagsInFile = self._speciesToAnalyze.get_tags(time_step)
                j = 0
                count = 0
                for tag in allParticleTagsInFile:
                    if tag in trackedParticleTags:
                        particlesFound = True
                        pIndex = np.where(trackedParticleTags == tag)[0][0]
                        particleIndices[pIndex, i] = j
                        trackedTimeSteps[pIndex, i] = time_step
                        count += 1
                        if count == numberOfParticles:
                            break
                    j += 1
            except:
                pass
            finally:
                if particlesFound and count == 0:
                    break # break loop if all the particles have already dissapeared from the files (simulation domain)
                i+=1
        k = 0
        for particle in self._particleList:
            unfilteredIndices = particleIndices[k]
            filteredIndices = np.delete(unfilteredIndices, np.where(unfilteredIndices == -1))
            unfilteredTimeSteps = trackedTimeSteps[k]
            filteredTimeSteps = np.delete(unfilteredTimeSteps, np.where(unfilteredTimeSteps == -1))
            particle.SetIndices(filteredIndices)
            particle.SetTrackedTimeSteps(filteredTimeSteps)
            k += 1
        
    def _GetTrackedParticleTags(self):
        tags = list()
        for particle in self._particleList:
            tags.append(particle.tag)
        return tags
                
    def _FillEvolutionOfDataSetInParticles(self, dataSet):
        time_stepsWithParticleData = np.array([])
        quantityValues = list() # one 1D array for each particle
        timeValues = list()
        counter = list()
        for particle in self._particleList:
            time_stepsWithParticleData = np.unique(np.concatenate((time_stepsWithParticleData,particle.GetTrackedTimeSteps()),0))
            quantityValues.append(np.zeros(len(particle.GetTrackedTimeSteps())))
            if not self.timeInfoAdded:
                timeValues.append(np.zeros(len(particle.GetTrackedTimeSteps())))
            counter.append(0)
        allSimulatedTimeSteps = dataSet.get_time_steps()
        for time_step in allSimulatedTimeSteps:
            if time_step <= max(time_stepsWithParticleData) and (time_step in time_stepsWithParticleData):
                print(time_step)
                data = dataSet.get_data_in_original_units(time_step)
                p = 0
                for particle in self._particleList:
                    if time_step in particle.GetTrackedTimeSteps():
                        step = counter[p]
                        quantityValues[p][step] = data[particle.GetIndex(time_step)]
                        if not self.timeInfoAdded:
                            timeValues[p][step] = dataSet.get_time_in_original_units(time_step)
                        counter[p] += 1
                    p += 1
        for particle in self._particleList:
            if not self.timeInfoAdded:
                particle.AddTimeInfo(timeValues[self._particleList.index(particle)], dataSet.get_time_original_units(), dataSet.has_non_si_units)
            particle.AddWholeSimulationQuantity(dataSet, quantityValues[self._particleList.index(particle)])
        self.timeInfoAdded = True

    def MakeInstantaneousRawDataSets(self):
        self._instantRawDataSetsList.clear()
        trackedQuantities = self._particleList[0].GetNamesOfWholeSimulationQuantities()
        time_stepsWithParticleData = np.array([])
        for particle in self._particleList:
            time_stepsWithParticleData = np.unique(np.concatenate((time_stepsWithParticleData,particle.GetTrackedTimeSteps()),0))
        for quantityName in trackedQuantities:
            if quantityName != "Time":
                data = np.zeros([len(time_stepsWithParticleData),len(self._particleList)])
                data.fill(np.nan)
                timeValues = np.array([])
                n = 0
                for particle in self._particleList:
                    quantity = particle.GetWholeSimulationQuantity(quantityName)
                    particleTimeSteps = particle.GetTrackedTimeSteps()
                    first = np.where(time_stepsWithParticleData == particleTimeSteps.min())[0][0]
                    last = np.where(time_stepsWithParticleData == particleTimeSteps.max())[0][0]
                    data[first:last+1,n] = quantity.get_all_data_in_original_units()
                    timeData = particle.GetWholeSimulationQuantity("Time")
                    timeValues = np.unique(np.concatenate((timeValues,timeData.get_all_data_in_original_units()),0))
                    dataUnits = quantity.get_data_original_units()
                    timeUnits = timeData.get_time_original_units()
                    n += 1 
                self._instantRawDataSetsList.append(SelfContainedRawDataSet(quantityName, data, dataUnits, quantity.has_non_si_units, timeValues, timeUnits, time_stepsWithParticleData, self._speciesToAnalyze.get_name()))

    def GetTrackedParticles(self):
        return self._particleList

    def GetAvailableWholeSimulationQuantitiesInParticles(self):
        return self._particleList[0].GetNamesOfWholeSimulationQuantities()

    def GetAvailableTimeStepQuantitiesInParticles(self):
        return self._particleList[0].GetNamesOfTimeStepQuantities()

    def GetTotalNumberOfTrackedParticles(self):
        return len(self._particleList)

    def GetTrackedParticlesDataToPlot(self, xDataName, yDataName, zDataName = None):
        allParticlesData = list()
        for particle in self._particleList:
            singleParticleData = {}
            singleParticleData["plotStyle"] = 'C0' # todo: find a better place for storing the plotStyles in all dataTypes (Field, Raw and RawEvolution)
            singleParticleData["particle"] = particle
            singleParticleData["x"] = RawDataEvolutionToPlot(particle.GetWholeSimulationQuantity(xDataName))
            singleParticleData["y"] = RawDataEvolutionToPlot(particle.GetWholeSimulationQuantity(yDataName))
            if zDataName != None:
                singleParticleData["z"] = RawDataEvolutionToPlot(particle.GetWholeSimulationQuantity(zDataName))
            allParticlesData.append(singleParticleData)
        return allParticlesData

    def GetTrackedSpeciesName(self):
        return self._speciesToAnalyze.get_name()

    def ExportParticleData(self, particleIndices, location):
        for index in particleIndices:
            fileName = "particle" + str(index+1).zfill(3)
            self._particleList[index].WriteDataToFile(location, fileName)
