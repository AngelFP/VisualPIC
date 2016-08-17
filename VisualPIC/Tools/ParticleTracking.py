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

import numpy as np

from VisualPIC.DataHandling.species import Species
from VisualPIC.DataHandling.rawDataSet import RawDataSet


class Particle():
    def __init__(self, index):
        self.index = index
        self._timeStepQuantities = {}
        self._wholeSimulationQuantities = {}

    def AddTimeStepQuantity(self, quantityName, quantityValue):
        self._timeStepQuantities[quantityName] = quantityValue

    def AddWholeSimulationQuantity(self, quantityName, quantityValues):
        self._wholeSimulationQuantities[quantityName] = quantityValues


class ParticleTracker():
    def __init__(self, dataContainer):
        self.dataContainer = dataContainer
        self._speciesList = self.dataContainer.GetSpeciesWithRawData()
        self._speciesToAnalyze = None
        self._particlesList = list()

    def FindParticles(self, timeStep, speciesName, filters):
        """filters is a dictionary where the keys are the names of the variables 
        to filter (eg /q, /x1, etc.) and the values are a tuple with two numbers
        (the lower and higher limit)"""
        for species in self._speciesList:
            if species.GetName() == speciesName:
                self.speciesToAnalyze = species
        indicesList = list()
        for rawDataSetName, range in filters.iteritems():
            indicesList.append(self._GetIndicesOfParticlesInRange(timeStep, speciesToAnalyze, rawDataSetName, range))
        indicesOfFoundParticles = self._GetCommonElementsInListOfArrays(indicesList)
        particles = self._GetParticlesFromIndices(timeStep, speciesToAnalyze, indicesOfFoundParticles)
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
        for i in np.linspace(1,n-1,n-1):
            commonEls = np.intersect1d(listOfArrays[i], commonEls)
        return commonEls

    def _GetParticlesFromIndices(self, timeStep, species, indices):
        rawDataSets = species.GetAllRawDataSets()
        dataSetValues = {}
        for dataSet in rawDataSets:
            dataSetValues[dataSet.GetName()]=append(dataSet.GetData(timeStep))
        particlesList = list()
        for index in indices:
            particle = Particle(index)
            for dataSetName, values in dataSetValues.iteritems():
                particle.AddTimeStepQuantity(dataSetName, values[index])
            particlesList.append(particle)
        return particlesList

    def SetParticlesToTrack(self, particlesList):
        self._particlesList = particlesList

    def _FillEvolutionOfDataSetInParticles(self, dataSet):
        totalTimeSteps = dataSet.GetTotalTimeSteps()
        numberOfParticles = len(self._particleList)
        timeValues = np.zeros([numberOfParticles, totalTimeSteps])
        for timeStep in np.linspace(0,totalTimeSteps-1, totalTimeSteps):
            data = dataSet.GetData(timeStep)
            for particle in self._particleList:
                timeValues[self._particleList.index(particle), timeStep] = data[particle.index]
        for particle in self._particleList:
            particle.AddWholeSimulationQuantity(dataSet.GetName(), timeValues[self._particleList.index(particle)])

    def FillEvolutionOfAllDataSetsInParticles(self):
        rawDataSets = self._speciesToAnalyze.GetAllRawDataSets()
        for dataSet in rawDataSets:
            self._FillEvolutionOfDataSetInParticles(dataSet)
