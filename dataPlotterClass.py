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
import random
import numpy as np
    
 

class DataPlotter:
    
    def __init__(self, colorMapsCollection):
        
        self.testprop = 0
        self.currentAxesNumber = 1
        self.colorMapsCollection = colorMapsCollection
        self.cbSpacing = 0.01 # vertical space between color bars
        self.LoadPlotTypes()
     
    def LoadPlotTypes(self):
        
        self.plotTypes = {
            "Field":self.MakeFieldPlot,
            "Axis":self.Make2DHistogram
            }
            
    def MakePlot(self, figure, subplotList, rows, columns, timeStep):
        self.currentAxesNumber = rows*columns
        for ax in figure.axes:
            figure.delaxes(ax)
            
        
        figure.subplots_adjust(hspace=.3, top=.93, bottom=.09, right = .93, left = .09)
        
        
        
        for subplot in subplotList:
            self.plotTypes[subplot.GetDataType()](figure, subplot, rows, columns, timeStep)
                    
    def MakeFieldPlot(self, figure, subplot, rows, columns, timeStep):

            if subplot != None:
                numFields = len(subplot.GetFieldsToPlot())
                ax = figure.add_subplot(rows,columns,subplot.GetPosition())
                ax.hold(False)
                i = 0
                for field in subplot.GetFieldsToPlot():
                    
                    plotData = field.GetFieldPlotData(timeStep)
                    units = plotData[2]
                    field_cmap = self.colorMapsCollection.GetColorMap(field.GetColorMap())
                    if field.IsScaleCustom():
                        scale = field.GetScale()
                        im = ax.imshow(plotData[0], extent = plotData[1], aspect='auto', cmap=field_cmap, vmin=scale[0], vmax = scale[1])
                    else:
                        im = ax.imshow(plotData[0], extent = plotData[1], aspect='auto', cmap=field_cmap)
                    ax.xaxis.set_major_locator( LinearLocator(5) )
                    ax.set_xlabel(subplot.GetXAxisText() + "$["+units[0]+"]$", fontsize=subplot.GetXAxisTextFontSize())
                    ax.set_ylabel(subplot.GetYAxisText() + "$["+units[1]+"]$", fontsize=subplot.GetYAxisTextFontSize())
                    ax.set_title(field.GetName())
                    if i == 0:
                        pos1 = ax.get_position()
                        pos2 = [pos1.x0, pos1.y0 ,  pos1.width-0.1, pos1.height]
                        ax.set_position(pos2)
                    ax.hold(True)
                    
                    cbWidth = 0.015
                    cbHeight = (pos2[3]-(numFields-1)*self.cbSpacing)/numFields
                    cbX = pos2[0] + pos2[2] + 0.02
                    cbY = pos2[1] + i*(cbHeight + self.cbSpacing)
                    
                    cbAxes = figure.add_axes([cbX, cbY, cbWidth, cbHeight]) 
                    cbar = figure.colorbar(im, cax = cbAxes, cmap=field_cmap, drawedges=False)
                    cbar.solids.set_edgecolor("face")
                    cbar.set_label(label="$"+units[2]+"$",size=20)
                    i += 1
                    
    def MakeAxisDataPlot(self, figure, subplot, rows, columns, timeStep):    
        if subplot != None:
            ax = figure.add_subplot(rows,columns,subplot.GetPosition())
            plotData = subplot.GetAxisData()
            xData = plotData["x"].GetDataSetPlotData(timeStep)
            yData = plotData["y"].GetDataSetPlotData(timeStep)
            weightData = plotData["weight"].GetDataSetPlotData(timeStep)
            
            blues_cmap = matplotlib.cm.get_cmap('Blues_r')
            blues_cmap._init()
            alphas = np.abs(np.linspace(1.0, 0, blues_cmap.N))
            blues_cmap._lut[:-3,-1] = alphas  
        
            ax.scatter(xData[0],yData[0],c=weightData[0], cmap=blues_cmap, linewidths=0)
    
    def Make2DHistogram(self, figure, subplot, rows, columns, timeStep):
        if subplot != None:
            ax = figure.add_subplot(rows,columns,subplot.GetPosition())
            plotData = subplot.GetAxisData()
            xData = plotData["x"].GetDataSetPlotData(timeStep)
            yData = plotData["y"].GetDataSetPlotData(timeStep)
            weightData = plotData["weight"].GetDataSetPlotData(timeStep)
            
            xValues = xData[0]
            yValues = yData[0]
            weightValues = weightData[0]
            
            xUnits = xData[1]
            yUnits = yData[1]
            weightUnits = weightData[1]
            
            xMin = min(xValues)
            xMax = max(xValues)
            yMin = min(yValues)
            yMax = max(yValues)
            
            rangex = xMax - xMin
            rangey = yMax - yMin
            
            xMargin = rangex/10
            yMargin = rangey/10
            
            xMinHist = round(xMin-xMargin)
            xMaxHist = round(xMax+xMargin)
            yMinHist = round(yMin-yMargin)
            yMaxHist = round(yMax+yMargin)
#            
#            numPart = len(xData)
#            numBins = 100
#            
#            for i in np.linspace(0, numPart-1, numPart-1):
#                x = xValues[i]
#                y = yValues[i]
#                w = weightValues[i]
#                
#                xBin = round((x-xMin)/dx * numBins)
#                yBin = round((y-yMin)/dy * numBins)
#                
#            ax.scatter(xData[0],yData[0],c=weightData[0], cmap=blues_cmap, linewidths=0)
            blues_cmap = matplotlib.cm.get_cmap('Blues_r')
            blues_cmap._init()
#            
            H, xedges, yedges = np.histogram2d(xValues, yValues, bins = 80, weights = weightValues)
            dx = xedges[1]-xedges[0]
            dy = yedges[1]-yedges[0]
#            X, Y = np.meshgrid(xedges, yedges)
#            ax.pcolormesh(X, Y, H.transpose(), cmap=blues_cmap)
            
            extent = xedges[0], xedges[-1], yedges[0], yedges[-1]
            ax.imshow(H.transpose(), extent=extent, cmap=blues_cmap, aspect='auto', origin='lower')
            
            #ax.hexbin(xValues,yValues)
            
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