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

import matplotlib
import numpy as np

class CustomColorMap:
    def __init__(self, name, colormap):
        self.name = name
        self.colormap = colormap
        
    def GetName(self):
        return self.name
    
    def GetColorMap(self):
        return self.colormap

class CompoundColorMap:
    
    def __init__(self, name, colorMapList):
        self.name = name
        self.colorMapList = colorMapList
        
    def GetName(self):
        return self.name
        
    def GetColorMapList(self):
        return self.colorMapList
        
class ColorMapsCollection:
    def __init__(self):
        self.LoadColorMapsList()
        
    def LoadColorMapsList(self):
        self.SingleColorMapsNamesList = ["Accent", "Blues", "BrBG", "BuGn", "BuPu", "CMRmap",
                              "Dark2", "GnBu", "Greens", "Greys", "OrRd", "Oranges",
                              "PRGn", "Paired", "Pastel1", "Pastel2", "PiYG", "PuBu",
                              "PuBuGn", "PuOr", "PuRd", "Purples", "RdBu", "RdGy",
                              "RdPu", "RdYlBu", "RdYlGn", "Reds", "Set1", "Set2",
                              "Set3", "Spectral", "YlGn", "YlGnBu", "YlOrBr", "YlOrBr",
                              "YlOrRd", "afmhot", "autumn", "binary", "bone", "bgr"
                              "bwr", "cool", "coolwarm", "copper", "cubehelix", "flag",
                              "gist_earth", "gist_gray", "gist_heat", "gist_ncar",
                              "gist_rainbow", "gist_stern", "gist_yarg", "gnuplot",
                              "gnuplot2", "gray", "hot", "hsv", "jet", "ocean",
                              "pink", "prism", "rainbow", "seismic", "spectral",
                              "spring", "summer", "terrain", "winter"]
                              
                         
        #self.CompoundColorMapList = [self.CreateChargeCompoundColorMap()]
        self.CreateTransparentColorMapList()              
        
        #self.CreateListOfAllMapNames()
#        
#    def CreateListOfAllMapNames(self):
#        self.allMapsNames = list(self.SingleColorMapsNamesList)
#        for cmap in self.CompoundColorMapList:
#            self.allMapsNames.append(cmap.GetName())
    

    def CreateTransparentColorMapList(self):
        self.TransparentColorMapList = list()
        gray_cmap = matplotlib.cm.get_cmap('gray')
        #gray_cmap._init()
        
        base_gray = CustomColorMap("Base grey", gray_cmap)
        self.TransparentColorMapList.append(base_gray)
        
        afmhot_cmap = matplotlib.cm.get_cmap('afmhot')
        afmhot_cmap._init()
        alphas = np.abs(np.linspace(1.0, 0, afmhot_cmap.N))
        afmhot_cmap._lut[:-3,-1] = alphas 
        
        orange = CustomColorMap("OrangeT", afmhot_cmap)
        self.TransparentColorMapList.append(orange)
        
        blues_cmap = matplotlib.cm.get_cmap('Blues_r')
        blues_cmap._init()
        alphas = np.abs(np.linspace(1.0, 0, blues_cmap.N))
        blues_cmap._lut[:-3,-1] = alphas  
        
        blue = CustomColorMap("BlueT", blues_cmap)
        self.TransparentColorMapList.append(blue)
        
        greens_cmap = matplotlib.cm.get_cmap('Greens_r')
        greens_cmap._init()
        alphas = np.abs(np.linspace(1.0, 0, greens_cmap.N))
        greens_cmap._lut[:-3,-1] = alphas  
        
        green = CustomColorMap("GreenT", greens_cmap	)
        self.TransparentColorMapList.append(green)
        
        bupu_cmap = matplotlib.cm.get_cmap('BuPu_r')
        bupu_cmap._init()
        alphas = np.abs(np.linspace(1.0, 0, bupu_cmap.N))
        bupu_cmap._lut[:-3,-1] = alphas  
        
        purple = CustomColorMap("PurpleT", bupu_cmap)
        self.TransparentColorMapList.append(purple)
        
#    def CreateChargeCompoundColorMap(self):
#        colorMapList = list()
#        gray_cmap = matplotlib.cm.get_cmap('gray')
#        gray_cmap._init()
#        
#        colorMapList.append(gray_cmap)
#        
#        afmhot_cmap = matplotlib.cm.get_cmap('afmhot')
#        afmhot_cmap._init()
#        alphas = np.abs(np.linspace(1.0, 0, afmhot_cmap.N))
#        afmhot_cmap._lut[:-3,-1] = alphas  
#        colorMapList.append(afmhot_cmap)
#        
#        blues_cmap = matplotlib.cm.get_cmap('Blues_r')
#        blues_cmap._init()
#        alphas = np.abs(np.linspace(1.0, 0, blues_cmap.N))
#        blues_cmap._lut[:-3,-1] = alphas  
#        colorMapList.append(blues_cmap)
#        
#        greens_cmap = matplotlib.cm.get_cmap('Greens_r')
#        greens_cmap._init()
#        alphas = np.abs(np.linspace(1.0, 0, greens_cmap.N))
#        greens_cmap._lut[:-3,-1] = alphas  
#        colorMapList.append(greens_cmap)
#        
#        bupu_cmap = matplotlib.cm.get_cmap('BuPu_r')
#        bupu_cmap._init()
#        alphas = np.abs(np.linspace(1.0, 0, bupu_cmap.N))
#        bupu_cmap._lut[:-3,-1] = alphas  
#        colorMapList.append(bupu_cmap)
#        
#        colorMap = CompoundColorMap("charge multiple", colorMapList)
#        return colorMap
        
#    def GetAllMapsNames(self):
#        return self.allMapsNames
        
    def GetSingleColorMapsNamesList(self):
        return self.SingleColorMapsNamesList
        
    def GetTransparentColorMapsNames(self):
        namesList = list()
        for cmap in self.TransparentColorMapList:
            namesList.append(cmap.GetName())
        return namesList
        
    def GetColorMap(self, colorMapName):
        for cmapName in self.SingleColorMapsNamesList:
            if cmapName == colorMapName:
                cmap = matplotlib.cm.get_cmap(cmapName)
                return cmap
                
        for cmap in self.TransparentColorMapList:
            if cmap.GetName() == colorMapName:
                return cmap.GetColorMap()
                
#        for cmap in self.CompoundColorMapList:
#            if cmap.GetName() == colorMapName:
#                return cmap.GetColorMapList()