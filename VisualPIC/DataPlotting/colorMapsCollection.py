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

import matplotlib
import numpy as np

class CustomColorMap:
    def __init__(self, name, colormap):
        self.name = name
        self.colormap = colormap
        
    def get_name(self):
        return self.name
    
    def GetColorMap(self):
        return self.colormap
        
class ColorMapsCollection:
    def __init__(self):
        self.LoadColorMapsList()
        
    def LoadColorMapsList(self):
        # TODO: simply get the list from matplotlib
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
                              
        self.CreateTransparentColorMapList()              
        self.CreateUniformColorMapsWithTransparency()
    

    def CreateTransparentColorMapList(self):
        self.TransparentColorMapList = list()
        gray_cmap = matplotlib.cm.get_cmap('gray')
        gray_cmap._init()
        alphas = np.abs(np.linspace(1.0, 0, gray_cmap.N))
        gray_cmap._lut[:-3,-1] = alphas

        base_gray = CustomColorMap("Base gray", gray_cmap)
        self.TransparentColorMapList.append(base_gray)
        
        """
        Reverse Transparent CMaps - for charge field (usually negative)
        """
        oranges_cmap = matplotlib.cm.get_cmap('Oranges_r')
        oranges_cmap._init()
        alphas = np.abs(np.linspace(1.0, 0, oranges_cmap.N))
        oranges_cmap._lut[:-3,-1] = alphas 
        
        orange_r = CustomColorMap("Orange_r", oranges_cmap)
        self.TransparentColorMapList.append(orange_r)
        
        blues_cmap = matplotlib.cm.get_cmap('Blues_r')
        blues_cmap._init()
        alphas = np.abs(np.linspace(1.0, 0, blues_cmap.N))
        blues_cmap._lut[:-3,-1] = alphas  
        
        blue_r = CustomColorMap("Blue_r", blues_cmap)
        self.TransparentColorMapList.append(blue_r)
        
        greens_cmap = matplotlib.cm.get_cmap('Greens_r')
        greens_cmap._init()
        alphas = np.abs(np.linspace(1.0, 0, greens_cmap.N))
        greens_cmap._lut[:-3,-1] = alphas  
        
        green_r = CustomColorMap("Green_r", greens_cmap)
        self.TransparentColorMapList.append(green_r)
        
        bupu_cmap = matplotlib.cm.get_cmap('BuPu_r')
        bupu_cmap._init()
        alphas = np.abs(np.linspace(1.0, 0, bupu_cmap.N))
        bupu_cmap._lut[:-3,-1] = alphas  
        
        purple_r = CustomColorMap("Purple_r", bupu_cmap)
        self.TransparentColorMapList.append(purple_r)

        """
        Non-reverse Transparent CMaps
        """
        oranges_cmap = matplotlib.cm.get_cmap('Oranges')
        oranges_cmap._init()
        alphas = np.abs(np.linspace(0, 1.0, oranges_cmap.N))
        oranges_cmap._lut[:-3,-1] = alphas 
        
        orange = CustomColorMap("Orange", oranges_cmap)
        self.TransparentColorMapList.append(orange)
        
        blues_cmap = matplotlib.cm.get_cmap('Blues')
        blues_cmap._init()
        alphas = np.abs(np.linspace(0, 1.0, blues_cmap.N))
        blues_cmap._lut[:-3,-1] = alphas  
        
        blue = CustomColorMap("Blue", blues_cmap)
        self.TransparentColorMapList.append(blue)
        
        greens_cmap = matplotlib.cm.get_cmap('Greens')
        greens_cmap._init()
        alphas = np.abs(np.linspace(0, 1.0, greens_cmap.N))
        greens_cmap._lut[:-3,-1] = alphas  
        
        green = CustomColorMap("Green", greens_cmap)
        self.TransparentColorMapList.append(green)
        
        bupu_cmap = matplotlib.cm.get_cmap('BuPu')
        bupu_cmap._init()
        alphas = np.abs(np.linspace(0, 1.0, bupu_cmap.N))
        bupu_cmap._lut[:-3,-1] = alphas  
        
        purple = CustomColorMap("Purple", bupu_cmap)
        self.TransparentColorMapList.append(purple)

        
    
    def CreateUniformColorMapsWithTransparency(self):
        
        self.UniformCMapsWithTransparency = list()
        # Blue
        cdictBlue = {'red':   ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),

         'green': ((0.0, 0.4, 0.4),
                   (1.0, 0.4, 0.4)),

         'blue':  ((0.0, 0.7, 0.7),
                   (1.0, 0.7, 0.7)),

         'alpha': ((0.0, 1.0, 1.0),
                   (0.02, 0.6, 0.6),
                   (0.1, 0.3, 0.3),
                   (0.2, 0.2, 0.2),
                   (0.5, 0.1, 0.1),
                   (1.0, 0.0, 0.0))
        }
        matplotlib.cm.register_cmap(name='Uniform Blue Transparent', data=cdictBlue)
        
        blueTransp = CustomColorMap('Uniform Blue Transparent', matplotlib.cm.get_cmap('Uniform Blue Transparent'))
        self.UniformCMapsWithTransparency.append(blueTransp)
        
    def get_all_cmap_names(self):
        cmapList = list()
        cmapList = self.GetUniformColorMapsWithTransparencyNames() + self.GetTransparentColorMapsNames() + self.GetSingleColorMapsNamesList()
        return cmapList
    def get_all_cmap_names_with_tansparency(self):
        cmapList = list()
        cmapList = self.GetUniformColorMapsWithTransparencyNames() + self.GetTransparentColorMapsNames()
        return cmapList
        
    def GetSingleColorMapsNamesList(self):
        return self.SingleColorMapsNamesList
        
    def GetTransparentColorMapsNames(self):
        names_list = list()
        for cmap in self.TransparentColorMapList:
            names_list.append(cmap.get_name())
        return names_list
        
    def GetUniformColorMapsWithTransparencyNames(self):
        names_list = list()
        for cmap in self.UniformCMapsWithTransparency:
            names_list.append(cmap.get_name())
        return names_list
        
    def GetColorMap(self, colorMapName):
        for cmapName in self.SingleColorMapsNamesList:
            if cmapName == colorMapName:
                cmap = matplotlib.cm.get_cmap(cmapName)
                return cmap
                
        for cmap in self.TransparentColorMapList:
            if cmap.get_name() == colorMapName:
                return cmap.GetColorMap()
                
        for cmap in self.UniformCMapsWithTransparency:
            if cmap.get_name() == colorMapName:
                return cmap.GetColorMap()