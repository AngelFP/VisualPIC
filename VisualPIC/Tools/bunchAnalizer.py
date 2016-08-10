# -*- coding: utf-8 -*-

### TO REMOVE ###
# Add VisualPIC folder to python path, so that folders can be called as modules
import os
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(os.path.dirname(currentdir))
os.sys.path.insert(0,parentdir) 
### TO REMOVE ###

from VisualPIC.DataReading.availableData import AvailableData
from VisualPIC.DataReading.species import Species

from VisualPIC.DataPlotting.colorMapsCollection import ColorMapsCollection
from VisualPIC.DataPlotting.dataPlotter import DataPlotter
from VisualPIC.DataHandling.fieldToPlot import FieldToPlot
from VisualPIC.DataHandling.rawDataSetToPlot import RawDataSetToPlot
from VisualPIC.DataHandling.subplot import Subplot
import VisualPIC.DataHandling.unitConverters as unitConverters

import numpy as np

class BunchAnalizer:

    def __init__(self, availableData, dataPlotter, colorMapsCollection):
        self.availableData = availableData
        self.dataPlotter = dataPlotter
        self.colorMapsCollection = colorMapsCollection
        self.rawSpeciesList = self.availableData.GetSpeciesWithRawData() #list containing the species, not just the names

    def GetSpecies(self, speciesName):
        for species in self.rawSpeciesList:
            if species.GetName() == speciesName:
                return species

    def dot(self, A, B):
        return np.sum(A.conj()*B, axis=0)

    def WeightedMean(self, x, x_weight):
        w = np.divide(x_weight,np.sum(x_weight))
        mean = self.dot(x, w)
        std = np.sqrt(self.dot(np.square(x-mean),w))
        return mean, std

    def CalculateMeanEnergy(self, bunchName, timeStep):
        c=299792458 #m/s
        e=1.60217733e-19 #C
        m_e=9.1093897e-31 #kg
        selectedSpecies = self.GetSpecies(bunchName)

        ene = np.array(selectedSpecies.GetRawDataSet("ene").GetPlotData(timeStep)[0])
        q = np.array(selectedSpecies.GetRawDataSet("q").GetPlotData(timeStep)[0])

        eMean, eStd = self.WeightedMean(ene, q)
        return eMean*m_e*c**2/e

    def CalculateEnergySpread(self, bunchName, timeStep):
        selectedSpecies = self.GetSpecies(bunchName)

        ene = np.array(selectedSpecies.GetRawDataSet("ene").GetPlotData(timeStep)[0])
        q = np.array(selectedSpecies.GetRawDataSet("q").GetPlotData(timeStep)[0])

        eMean, eStd = self.WeightedMean(ene, q)
        eSpread = eStd / eMean
        return eSpread

    def CalculateEmmitance(self, bunchName, timeStep):
        c=299792458 #m/s
        e=1.60217733e-19 #C
        m_e=9.1093897e-31 #kg
        eps_0=8.854187817e-12 #As/(Vm)

        n_p = 1e17
        n_p_SI = n_p*1e6
        w_p = np.sqrt(n_p_SI*(e)**2/(m_e*eps_0)) #plasma freq (s-1)
        s_d = c/w_p #plasma skin depth [m]

        selectedSpecies = self.GetSpecies(bunchName)

        eMass = 0.510998 # in MeV

        p1 = np.array(selectedSpecies.GetRawDataSet("p1").GetPlotData(timeStep)[0])
        p2 = np.array(selectedSpecies.GetRawDataSet("p2").GetPlotData(timeStep)[0])
        ene = np.array(selectedSpecies.GetRawDataSet("ene").GetPlotData(timeStep)[0])
        x2 = np.array(selectedSpecies.GetRawDataSet("x2").GetPlotData(timeStep)[0])
        q = np.array(selectedSpecies.GetRawDataSet("q").GetPlotData(timeStep)[0])

        p = np.divide(q,np.sum(q))

        x2pr = np.divide(p2, p1)

        x2_ave = self.dot(np.square(x2),p) - np.square(self.dot(x2,p))
        x2pr_ave = self.dot(np.square(x2pr),p) - np.square(self.dot(x2pr,p))
        x2x2pr_ave = self.dot(np.multiply(x2,x2pr),p) - np.multiply(self.dot(x2,p),self.dot(x2pr,p))

        emitt=np.sqrt(x2_ave*x2pr_ave-x2x2pr_ave*x2x2pr_ave)
        eMean = self.WeightedMean(ene, q)[0]
        norm_trans_emm = emitt*s_d*eMean*eMass*1e6
        return norm_trans_emm

    def CalculateAll(self, bunchName, timeStep):
        print(self.CalculateMeanEnergy(bunchName, timeStep))
        print(self.CalculateEnergySpread(bunchName, timeStep))
        print(self.CalculateEmmitance(bunchName, timeStep))


availableData = AvailableData()
colorMapsCollection = ColorMapsCollection()
dataPlotter = DataPlotter(colorMapsCollection)

folderPath = 'H:\\PhD\\Osiris_test_data\\MS'
availableData.SetDataFolderLocation(folderPath)
availableData.LoadFolderData()

analizer = BunchAnalizer(availableData, dataPlotter, colorMapsCollection)
em = analizer.CalculateAll("sinbad-bunch", 26)




