# -*- coding: utf-8 -*-

#Copyright 2016-2017 Angel Ferran Pousa
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
        self._timeStepQuantities = {}
        self._wholeSimulationQuantities = {}
        self._particleIndices = None
        self._trackedTimeSteps = []

    def AddTimeStepQuantity(self, quantityName, quantityValue):
        self._timeStepQuantities[quantityName] = quantityValue

    def AddWholeSimulationQuantity(self, dataSet, quantityValues):
        #self._wholeSimulationQuantities[quantityName] = {"values":quantityValues, "units":quantityUnits}
        quantityName = dataSet.GetName()
        quantityUnits = dataSet.GetDataOriginalUnits()
        timeValues = self._wholeSimulationQuantities["Time"].GetAllDataInOriginalUnits()
        timeUnits = dataSet.GetTimeOriginalUnits()
        self._wholeSimulationQuantities[quantityName] = EvolutionData(quantityName, quantityValues, quantityUnits, dataSet.hasNonISUnits, timeValues, timeUnits, self._trackedTimeSteps)

    def AddTimeInfo(self, timeValues, timeUnits, hasNonISUnits):
        self._wholeSimulationQuantities["Time"] = EvolutionData("Time", timeValues, timeUnits, hasNonISUnits, timeValues, timeUnits, self._trackedTimeSteps)

    def GetNamesOfWholeSimulationQuantities(self):
        quantitiesList = list()
        for key in self._wholeSimulationQuantities:
            quantitiesList.append(key)
        return quantitiesList

    def GetNamesOfTimeStepQuantities(self):
        quantitiesList = list()
        for key in self._timeStepQuantities:
            quantitiesList.append(key)
        return quantitiesList

    def GetCurrentTimeStepQuantities(self):
        return self._timeStepQuantities

    def GetWholeSimulationQuantity(self, quantityName):
        return self._wholeSimulationQuantities[quantityName]

    def GetDataAtTimeStep(self, timeStep):
        timeStepQuantities = {}
        for key in self._timeStepQuantities:
            timeStepQuantities[key] = self._wholeSimulationQuantities[key][timeStep]
        return timeStepQuantities

    def SetTrackedTimeSteps(self, timeSteps):
        self._trackedTimeSteps = timeSteps

    def GetTrackedTimeSteps(self):
        return self._trackedTimeSteps

    def SetIndices(self, indices):
        self._particleIndices = indices

    def GetIndex(self, timeStep):
        return self._particleIndices[np.where(self._trackedTimeSteps == timeStep)[0][0]]

    def WriteDataToFile(self, location, fileName):
        h5file = H5File(location + "/" + fileName + ".h5", "w")
        for key in self._wholeSimulationQuantities:
            dataSet = h5file.create_dataset(key, data = self._wholeSimulationQuantities[key].GetAllDataInISUnits())
            dataSet.attrs["Units"] = self._wholeSimulationQuantities[key].GetDataISUnits()
        h5file.close()


class ParticleTracker():
    def __init__(self, dataContainer):
        self._dataContainer = dataContainer
        self._speciesList = self._dataContainer.GetSpeciesWithTrackingData()
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

    def GetDataLocation(self):
        return self._dataContainer.GetFolderPath()

    def GetSpeciesNames(self):
        names = list()
        for species in self._speciesList:
            names.append(species.GetName())
        return names

    def GetSpeciesDataSet(self, speciesName, dataSetName):
        return self._dataContainer.GetSpeciesRawDataSet(speciesName, dataSetName)

    def GetSpeciesRawDataSetNames(self, speciesName):
        for species in self._speciesList:
            if species.GetName() == speciesName:
                return species.GetRawDataSetsNamesList()

    def GetNamesOfInstantRawDataSets(self):
        names = list()
        for dataSet in self._instantRawDataSetsList:
            names.append(dataSet.GetName())
        return names

    def GetInstantRawDataSet(self, dataSetName):
        for dataSet in self._instantRawDataSetsList:
            if dataSet.GetName() == dataSetName:
                return dataSet

    def FindParticles(self, timeStep, speciesName, filters):
        """filters is a dictionary where the keys are the names of the variables 
        to filter (eg /q, /x1, etc.) and the values are a tuple with two numbers
        (the lower and higher limit)"""
        for species in self._speciesList:
            if species.GetName() == speciesName:
                self._speciesToAnalyze = species
        indicesList = list()
        for rawDataSetName, range in filters.items():
            indicesList.append(self._GetIndicesOfParticlesInRange(timeStep, self._speciesToAnalyze, rawDataSetName, range))
        indicesOfFoundParticles = self._GetCommonElementsInListOfArrays(indicesList)
        particles = self._GetParticlesFromIndices(timeStep, self._speciesToAnalyze, indicesOfFoundParticles)
        return particles
    
    def _GetIndicesOfParticlesInRange(self, timeStep, species, rawDataSetName, range):
        dataSet = species.GetRawDataSet(rawDataSetName)
        data = dataSet.GetDataInOriginalUnits(timeStep)
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

    def _GetParticlesFromIndices(self, timeStep, species, indices):
        rawDataSets = species.GetAllRawDataSets()
        particleTags = species.GetRawDataTags(timeStep)
        dataSetValues = {}
        for dataSet in rawDataSets:
            dataSetValues[dataSet.GetName()] = dataSet.GetDataInOriginalUnits(timeStep) # particle data in selected time step
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
        rawDataSets = self._speciesToAnalyze.GetAllRawDataSets()
        self._FindIndicesOfParticles()
        for dataSet in rawDataSets:
            self._FillEvolutionOfDataSetInParticles(dataSet)

    def _FindIndicesOfParticles(self):
        timeSteps = self._speciesToAnalyze.GetRawDataTimeSteps()
        trackedParticleTags = self._GetTrackedParticleTags()
        totalTimeSteps = len(timeSteps)
        numberOfParticles = len(self._particleList)
        trackedTimeSteps = -np.ones([numberOfParticles, totalTimeSteps], dtype=int)
        particleIndices = -np.ones([numberOfParticles, totalTimeSteps], dtype=int)
        particlesFound = False
        i = 0
        for timeStep in timeSteps:
            print(timeStep)
            try:
                allParticleTagsInFile = self._speciesToAnalyze.GetRawDataTags(timeStep)
                j = 0
                count = 0
                for tag in allParticleTagsInFile:
                    if tag in trackedParticleTags:
                        particlesFound = True
                        pIndex = np.where(trackedParticleTags == tag)[0][0]
                        particleIndices[pIndex, i] = j
                        trackedTimeSteps[pIndex, i] = timeStep
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
        timeStepsWithParticleData = np.array([])
        quantityValues = list() # one 1D array for each particle
        timeValues = list()
        counter = list()
        for particle in self._particleList:
            timeStepsWithParticleData = np.unique(np.concatenate((timeStepsWithParticleData,particle.GetTrackedTimeSteps()),0))
            quantityValues.append(np.zeros(len(particle.GetTrackedTimeSteps())))
            if not self.timeInfoAdded:
                timeValues.append(np.zeros(len(particle.GetTrackedTimeSteps())))
            counter.append(0)
        allSimulatedTimeSteps = dataSet.GetTimeSteps()
        for timeStep in allSimulatedTimeSteps:
            if timeStep <= max(timeStepsWithParticleData) and (timeStep in timeStepsWithParticleData):
                print(timeStep)
                data = dataSet.GetDataInOriginalUnits(timeStep)
                p = 0
                for particle in self._particleList:
                    if timeStep in particle.GetTrackedTimeSteps():
                        step = counter[p]
                        quantityValues[p][step] = data[particle.GetIndex(timeStep)]
                        if not self.timeInfoAdded:
                            timeValues[p][step] = dataSet.GetTimeInOriginalUnits(timeStep)
                        counter[p] += 1
                    p += 1
        for particle in self._particleList:
            if not self.timeInfoAdded:
                particle.AddTimeInfo(timeValues[self._particleList.index(particle)], dataSet.GetTimeOriginalUnits(), dataSet.hasNonISUnits)
            particle.AddWholeSimulationQuantity(dataSet, quantityValues[self._particleList.index(particle)])
        self.timeInfoAdded = True

    def MakeInstantaneousRawDataSets(self):
        self._instantRawDataSetsList.clear()
        trackedQuantities = self._particleList[0].GetNamesOfWholeSimulationQuantities()
        timeStepsWithParticleData = np.array([])
        for particle in self._particleList:
            timeStepsWithParticleData = np.unique(np.concatenate((timeStepsWithParticleData,particle.GetTrackedTimeSteps()),0))
        for quantityName in trackedQuantities:
            if quantityName != "Time":
                data = np.zeros([len(timeStepsWithParticleData),len(self._particleList)])
                data.fill(np.nan)
                timeValues = np.array([])
                n = 0
                for particle in self._particleList:
                    quantity = particle.GetWholeSimulationQuantity(quantityName)
                    particleTimeSteps = particle.GetTrackedTimeSteps()
                    first = np.where(timeStepsWithParticleData == particleTimeSteps.min())[0][0]
                    last = np.where(timeStepsWithParticleData == particleTimeSteps.max())[0][0]
                    data[first:last+1,n] = quantity.GetAllDataInOriginalUnits()
                    timeData = particle.GetWholeSimulationQuantity("Time")
                    timeValues = np.unique(np.concatenate((timeValues,timeData.GetAllDataInOriginalUnits()),0))
                    dataUnits = quantity.GetDataOriginalUnits()
                    timeUnits = timeData.GetTimeOriginalUnits()
                    n += 1 
                self._instantRawDataSetsList.append(SelfContainedRawDataSet(quantityName, data, dataUnits, quantity.hasNonISUnits, timeValues, timeUnits, timeStepsWithParticleData, self._speciesToAnalyze.GetName()))

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
        return self._speciesToAnalyze.GetName()

    def ExportParticleData(self, particleIndices, location):
        for index in particleIndices:
            fileName = "particle" + str(index+1).zfill(3)
            self._particleList[index].WriteDataToFile(location, fileName)
