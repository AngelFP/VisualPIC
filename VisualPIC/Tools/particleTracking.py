# -*- coding: utf-8 -*-

#Copyright 2016 ?ngel Ferran Pousa
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

import sys
import numpy as np
import math
import h5py

from VisualPIC.DataHandling.species import Species
from VisualPIC.DataHandling.rawDataSet import RawDataSet
from VisualPIC.DataHandling.rawDataEvolutionToPlot import RawDataEvolutionToPlot


class Particle():
    def __init__(self, tag):
        self.tag = tag
        self._timeStepQuantities = {}
        self._wholeSimulationQuantities = {}
        self._particleIndices = None

    def AddTimeStepQuantity(self, quantityName, quantityValue):
        self._timeStepQuantities[quantityName] = quantityValue

    def AddWholeSimulationQuantity(self, quantityName, quantityValues, quantityUnits):
        self._wholeSimulationQuantities[quantityName] = {"values":quantityValues, "units":quantityUnits}

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

    def SetIndices(self, indices):
        self._particleIndices = indices

    def GetIndex(self, timeStep):
        return self._particleIndices[timeStep]

    def WriteDataToFile(self, location, fileName):
        h5file = h5py.File(location + "/" + fileName + ".h5", "w")
        for key in self._wholeSimulationQuantities:
            dataSet = h5file.create_dataset(key, data = self._wholeSimulationQuantities[key]["values"])
            dataSet.attrs["Units"] = self._wholeSimulationQuantities[key]["units"]
        h5file.close()

class ParticleTracker():
    def __init__(self, dataContainer, unitConverter):
        self._dataContainer = dataContainer
        self.unitConverter = unitConverter
        self._speciesList = self._dataContainer.GetSpeciesWithTrackingData()
        self._speciesToAnalyze = None
        self._particleList = list()
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

    def FindParticles(self, timeStep, speciesName, filters):
        """filters is a dictionary where the keys are the names of the variables 
        to filter (eg /q, /x1, etc.) and the values are a tuple with two numbers
        (the lower and higher limit)"""
        for species in self._speciesList:
            if species.GetName() == speciesName:
                self._speciesToAnalyze = species
        indicesList = list()
        if sys.version_info[0] < 3:
            for rawDataSetName, range in filters.iteritems():
                indicesList.append(self._GetIndicesOfParticlesInRange(timeStep, self._speciesToAnalyze, rawDataSetName, range))
        else:
            for rawDataSetName, range in filters.items():
                indicesList.append(self._GetIndicesOfParticlesInRange(timeStep, self._speciesToAnalyze, rawDataSetName, range))
        indicesOfFoundParticles = self._GetCommonElementsInListOfArrays(indicesList)
        particles = self._GetParticlesFromIndices(timeStep, self._speciesToAnalyze, indicesOfFoundParticles)
        return particles
    
    def _GetIndicesOfParticlesInRange(self, timeStep, species, rawDataSetName, range):
        dataSet = species.GetRawDataSet(rawDataSetName)
        data = dataSet.GetData(timeStep)
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
            dataSetValues[dataSet.GetName()] = dataSet.GetData(timeStep) # particle data in selected time step
        particlesList = list()
        for index in indices:
            particle = Particle(particleTags[index]) # create particle instance with corresponding tag
            if sys.version_info[0] < 3:
                for dataSetName, values in dataSetValues.iteritems():
                    particle.AddTimeStepQuantity(dataSetName, values[index])
            else:
                for dataSetName, values in dataSetValues.items():
                    particle.AddTimeStepQuantity(dataSetName, values[index])
            particlesList.append(particle)
        return particlesList

    def _FillEvolutionOfDataSetInParticles(self, dataSet):
        timeSteps = dataSet.GetTimeSteps()
        totalTimeSteps = len(timeSteps)
        numberOfParticles = len(self._particleList)
        quantityValues = np.zeros([numberOfParticles, totalTimeSteps])
        if not self.indexInfoAdded:
            indices = np.zeros([numberOfParticles, totalTimeSteps])
        if not self.timeInfoAdded:
            timeValues = np.zeros(totalTimeSteps)
        particleExitedDomain = False
        dataHasBeenWritten = False
        lastTimeStepIndex = totalTimeSteps
        firstTimeStepIndex = 0
        for timeStep in timeSteps:
            print(timeStep)
            particleTags = self._speciesToAnalyze.GetRawDataTags(timeStep)
            if particleTags.size>1:
                data = dataSet.GetData(timeStep)
                if not self.timeInfoAdded:
                    timeValues[timeStep] = dataSet.GetTime(timeStep)
                for particle in self._particleList:
                    if not self.indexInfoAdded:
                        particleIndex = self.GetParticleIndexFromTag(particle.tag, particleTags)
                        indices[self._particleList.index(particle), timeStep] = particleIndex # if particleIndex is None, it will set a NaN value in the numpy array.
                    else:
                        particleIndex = particle.GetIndex(timeStep)
                    if particleIndex != None and not math.isnan(particleIndex):
                        try:
                            quantityValues[self._particleList.index(particle), timeStep] = data[particleIndex]
                        except:
                            print(particleIndex)
                        if not dataHasBeenWritten:
                            firstTimeStepIndex = np.where(timeSteps == timeStep)[0][0]
                            dataHasBeenWritten = True
                    elif dataHasBeenWritten:
                        particleExitedDomain = True
                        lastTimeStepIndex = np.where(timeSteps == timeStep)[0][0]
                if particleExitedDomain:
                    break
        quantityValues = quantityValues[:,firstTimeStepIndex:lastTimeStepIndex] # remove the colums in which the particle is not in the domain
        if not self.timeInfoAdded:
            timeValues = timeValues[firstTimeStepIndex:lastTimeStepIndex]
        for particle in self._particleList:
            particle.AddWholeSimulationQuantity(dataSet.GetName(), quantityValues[self._particleList.index(particle)], dataSet.GetDataUnits())
            if not self.timeInfoAdded:
                particle.AddWholeSimulationQuantity("Time", timeValues, dataSet.GetTimeUnits())
            if not self.indexInfoAdded:
                particle.SetIndices(indices[self._particleList.index(particle)])
        self.indexInfoAdded = True
        self.timeInfoAdded = True

    def GetParticleIndexFromTag(self, particleTag, allTags):
        n = len(allTags)
        for i in np.arange(0,n):
            if (allTags[i] == particleTag).all():
                return i

    def FillEvolutionOfAllDataSetsInParticles(self):
        self.indexInfoAdded = False
        self.timeInfoAdded = False
        rawDataSets = self._speciesToAnalyze.GetAllRawDataSets()
        for dataSet in rawDataSets:
            self._FillEvolutionOfDataSetInParticles(dataSet)

    def SetParticlesToTrack(self, particleList):
        self._particleList = particleList

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
            singleParticleData["plotStyle"] = "b-" # todo: find a better place for storing the plotStyles in all dataTypes (Field, Raw and RawEvolution)
            singleParticleData["particle"] = particle
            singleParticleData["x"] = RawDataEvolutionToPlot(xDataName, particle)#, self.unitConverter)
            singleParticleData["y"] = RawDataEvolutionToPlot(yDataName, particle)#, self.unitConverter)
            if zDataName != None:
                singleParticleData["z"] = RawDataEvolutionToPlot(zDataName, particle)#, self.unitConverter)
            allParticlesData.append(singleParticleData)
        return allParticlesData

    def GetTrackedSpeciesName(self):
        return self._speciesToAnalyze.GetName()

    def ExportParticleData(self, particleIndices, location):
        for index in particleIndices:
            fileName = "particle" + str(index+1).zfill(3)
            self._particleList[index].WriteDataToFile(location, fileName)
