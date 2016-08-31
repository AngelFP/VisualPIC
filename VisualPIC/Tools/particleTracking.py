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

from VisualPIC.DataHandling.species import Species
from VisualPIC.DataHandling.rawDataSet import RawDataSet
from VisualPIC.DataHandling.rawDataEvolutionToPlot import RawDataEvolutionToPlot


class Particle():
    def __init__(self, tag):
        self.tag = tag
        self._timeStepQuantities = {}
        self._wholeSimulationQuantities = {}

    def AddTimeStepQuantity(self, quantityName, quantityValue):
        self._timeStepQuantities[quantityName] = quantityValue

    def AddWholeSimulationQuantity(self, quantityName, quantityValues, quantityUnits):
        self._wholeSimulationQuantities[quantityName] = {"values":quantityValues, "units":quantityUnits}

    def GetNamesOfAvailableQuantities(self):
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

    def GetTotalTimeSteps(self):
        return len(timeStepQuantities[timeStepQuantities.keys()[0]])


class ParticleTracker():
    def __init__(self, dataContainer, unitConverter):
        self._dataContainer = dataContainer
        self.unitConverter = unitConverter
        self._speciesList = self._dataContainer.GetSpeciesWithTrackingData()
        self._speciesToAnalyze = None
        self._particleList = list()

    def GetSpeciesNames(self):
        names = list()
        for species in self._speciesList:
            names.append(species.GetName())
        return names

    def GetTotalTimeSteps(self):
        return self._speciesList[0].GetAllRawDataSets()[0].GetTotalTimeSteps()

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
        totalTimeSteps = dataSet.GetTotalTimeSteps()
        numberOfParticles = len(self._particleList)
        timeValues = np.zeros([numberOfParticles, totalTimeSteps])
        for timeStep in np.arange(0,totalTimeSteps):
            particleTags = self._speciesToAnalyze.GetRawDataTags(timeStep)
            data = dataSet.GetData(timeStep)
            for particle in self._particleList:
                timeValues[self._particleList.index(particle), timeStep] = data[self.GetParticleIndexFromTag(particle.tag, particleTags)]
        for particle in self._particleList:
            particle.AddWholeSimulationQuantity(dataSet.GetName(), timeValues[self._particleList.index(particle)], dataSet.GetDataUnits())
    
    def GetParticleIndexFromTag(self, particleTag, allTags):
        n = len(allTags)
        for i in np.arange(0,n):
            if (allTags[i] == particleTag).all():
                return i

    def FillEvolutionOfAllDataSetsInParticles(self):
        rawDataSets = self._speciesToAnalyze.GetAllRawDataSets()
        for dataSet in rawDataSets:
            self._FillEvolutionOfDataSetInParticles(dataSet)

    def SetParticlesToTrack(self, particleList):
        self._particleList = particleList

    def GetTrackedParticles(self):
        return self._particleList

    def GetAvailableQuantitiesInParticles(self):
        return self._particleList[0].GetNamesOfAvailableQuantities()

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
