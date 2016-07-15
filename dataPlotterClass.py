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
 
from matplotlib.figure import Figure
import matplotlib
from matplotlib.ticker import LinearLocator
import numpy as np
import random
    
 

class DataPlotter:
    
    def __init__(self):
        
        self.testprop = 0
        self.currentAxesNumber = 1
        
    def MakePlot(self, figure, fieldsToPlot, rows, columns, timeStep):

        #if rows*columns != self.currentAxesNumber:
        self.currentAxesNumber = rows*columns
        for ax in figure.axes:
            figure.delaxes(ax)
            
        my_cmap = matplotlib.cm.get_cmap('gray')
        my_cmap._init()
        
        alphas = np.abs(np.linspace(1.0, 0, my_cmap.N))
        my_cmap._lut[:-3,-1] = alphas
        
        figure.subplots_adjust(hspace=.3, top=.93, bottom=.09, right = .93, left = .09)
        
        cbSpacing = 0.01 # vertical space between color bars
        
        for fieldToPlot in fieldsToPlot:
            if fieldToPlot != None:
#                if len(fieldToPlot)>=1:
                numFields = len(fieldToPlot)
                ax = figure.add_subplot(rows,columns,fieldToPlot[0].GetPosition())
                ax.hold(False)
                i = 0
                for field in fieldToPlot:
                    
                    plotData = field.GetFieldPlotData(timeStep)
                    units = plotData[2]
                    field_cmap = field.GetColorMap()
                    if field.IsScaleCustom():
                        scale = field.GetScale()
                        im = ax.imshow(plotData[0], extent = plotData[1], aspect='auto', cmap=field_cmap, vmin=scale[0], vmax = scale[1])
                    else:
                        im = ax.imshow(plotData[0], extent = plotData[1], aspect='auto', cmap=field_cmap)
                    ax.xaxis.set_major_locator( LinearLocator(5) )
                    ax.set_xlabel("x " + "$["+units[0]+"]$", fontsize=20)
                    ax.set_ylabel("y " + "$["+units[1]+"]$", fontsize=20)
                    ax.set_title(field.GetName())
                    if i == 0:
                        pos1 = ax.get_position()
                        pos2 = [pos1.x0, pos1.y0 ,  pos1.width-0.1, pos1.height]
                        ax.set_position(pos2)
                    ax.hold(True)
#                        if i == 0:
#                            cbar = figure.colorbar(im, cmap=field_cmap, label="$"+units[2][2:-1].replace("\\\\","\\")+"$")
#                            cbax = cbar.ax
#                            cbarpos = cbax.get_position()
#                            cbax.set_position([cbarpos.x0, cbarpos.y0 + i*cbarpos.height/numFields, cbarpos.width, cbarpos.height/numFields])
#                        else:
                    #cbaxes = figure.add_axes([cbarpos.x0, cbarpos.y0 + i*cbarpos.height/numFields, 0.03, cbarpos.height/numFields]) 
                    #cbar = figure.colorbar(im, cax = cbaxes, cmap=field_cmap, label="$"+units[2][2:-1].replace("\\\\","\\")+"$")
                    cbWidth = 0.015
                    cbHeight = (pos2[3]-(numFields-1)*cbSpacing)/numFields
                    cbX = pos2[0] + pos2[2] + 0.02
                    cbY = pos2[1] + i*(cbHeight + cbSpacing)
                    
                    cbAxes = figure.add_axes([cbX, cbY, cbWidth, cbHeight]) 
                    cbar = figure.colorbar(im, cax = cbAxes, cmap=field_cmap, drawedges=False)
                    cbar.solids.set_edgecolor("face")
                    cbar.set_label(label="$"+units[2]+"$",size=20)
                    i += 1
                    
#                else:
#                    plotData = fieldToPlot[0].GetFieldPlotData(timeStep)
#                    units = plotData[2]
#                    ax = figure.add_subplot(rows,columns,fieldToPlot[0].GetPosition())
#                    ax.hold(False)
#                    field_cmap = fieldToPlot[0].GetColorMap()
#                    if fieldToPlot[0].IsScaleCustom():
#                        scale = fieldToPlot[0].GetScale()
#                        im = ax.imshow(plotData[0], extent = plotData[1], aspect='auto', cmap=field_cmap, vmin=scale[0], vmax = scale[1])
#                    else:
#                        im = ax.imshow(plotData[0], extent = plotData[1], aspect='auto', cmap=field_cmap)
#                    ax.set_xlabel("$"+units[0]+"$", fontsize=20)
#                    ax.set_ylabel("$"+units[1]+"$", fontsize=20)
#                    ax.set_title(fieldToPlot[0].GetName())
#                    cbar = figure.colorbar(im, cmap=field_cmap, label="$"+units[2]+"$")     
        #figure.tight_layout()
        
    
    def UpdateFigure(self, figure):
        # random data
        data = [random.random() for i in range(10)]

        # create an axis
        ax = figure.add_subplot(111)

        # discards the old graph
        ax.hold(False)

        # plot data
        ax.plot(data, '*-')
            
    def GetSimplePlot(self, plotData):
    
        
        fig1 = Figure()
        ax1f1 = fig1.add_subplot(111)
        ax1f1.imshow(plotData[0], extent = plotData[1], aspect='auto')
        return fig1
    def PlotFields(self, fieldsToPlot, rows, columns, timeStep):
        
        my_cmap = matplotlib.cm.get_cmap('rainbow')
        my_cmap._init()
        
#        alphas = np.abs(np.linspace(-1.0, 1.0, my_cmap.N))
#        my_cmap._lut[:-3,-1] = alphas
        
        plotFig = Figure()
        for fieldToPlot in fieldsToPlot:
            if fieldToPlot != None:
                if isinstance(list,fieldToPlot):
                    ax = plotFig.add_subplot(rows,columns,fieldToPlot[0].GetPosition())
                    ax.hold(True)
                    for field in fieldToPlot:
                        plotData = field.GetFieldPlotData(timeStep)
                        ax.imshow(plotData[0], extent = plotData[1], aspect='auto', cmap=my_cmap)
                else:
                    plotData = fieldToPlot.GetFieldPlotData(timeStep)
                    ax = plotFig.add_subplot(rows,columns,fieldToPlot.GetPosition())
                    ax.imshow(plotData[0], extent = plotData[1], aspect='auto', cmap=my_cmap)
                
        return plotFig