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
from matplotlib.ticker import LinearLocator
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
    
 

class DataPlotter:
    
    def __init__(self, colorMapsCollection):
        
        self.testprop = 0
        self.currentAxesNumber = 1
        self.colorMapsCollection = colorMapsCollection
        self.cbSpacing = 0.01 # vertical space between color bars
        self.LoadPlotFromDataTypes()
        self.LoadPlotTypes()
     
    def LoadPlotFromDataTypes(self):
        
        self.PlotFromDataType = {
            "Field":self.MakeFieldPlot,
            "Axis":self.MakeAxisDataPlot
            }
            
    def LoadPlotTypes(self):
        fieldTypes ={
            "Image":self.MakeImagePlot,
            "Surface":self.MakeSurfacePlot,
            "Line":self.MakeLinePlot
            }
            
        axisTypes = {
            "Scatter":self.MakeScatterPlot,
            "Histogram":self.MakeHistogramPlot
            }
        self.plotTypes = {
            "Field":fieldTypes,
            "Axis":axisTypes
            }

            
    def MakePlot(self, figure, subplotList, rows, columns, timeStep):
        self.currentAxesNumber = rows*columns
        for ax in figure.axes:
            figure.delaxes(ax)
        
        figure.subplots_adjust(hspace=.3, top=.93, bottom=.09, right = .93, left = .09)
        
        for subplot in subplotList:
            if subplot != None:
                # create axes
                if subplot.GetAxesDimension() == "3D":
                    ax = figure.add_subplot(rows,columns,subplot.GetPosition(), projection='3d')
                else:
                    ax = figure.add_subplot(rows,columns,subplot.GetPosition())
                # make plot on axes
                self.PlotFromDataType[subplot.GetDataType()](figure, ax, subplot, rows, columns, timeStep)
                
                    
    def MakeFieldPlot(self, figure, ax, subplot, rows, columns, timeStep):
        num1DFields = len(subplot.GetFieldsToPlotWithDimension("1D"))
        num2DFields = len(subplot.GetFieldsToPlotWithDimension("2D"))
        ax.hold(False)
        i = 0
        for field in subplot.GetFieldsToPlotWithDimension("2D"):
            
            plotData = field.GetFieldPlotData(timeStep)
            units = field.GetFieldUnits()
            field_cmap = self.colorMapsCollection.GetColorMap(field.GetColorMap())
            scale = field.GetScale()
            isScaleCustom = field.IsScaleCustom()
            
            im = self.plotTypes["Field"][field.GetPlotType()](ax, plotData, field_cmap, scale, isScaleCustom)
            
            if i == 0:
                pos1 = ax.get_position()
                pos2 = [pos1.x0, pos1.y0 ,  pos1.width-0.1, pos1.height]
                ax.set_position(pos2)
            ax.hold(True)
            
            cbWidth = 0.015
            cbHeight = (pos2[3]-(num2DFields-1)*self.cbSpacing)/num2DFields
            cbX = pos2[0] + pos2[2] + 0.02
            cbY = pos2[1] + i*(cbHeight + self.cbSpacing)
            
            cbAxes = figure.add_axes([cbX, cbY, cbWidth, cbHeight]) 
            cbar = figure.colorbar(im, cax = cbAxes, cmap=field_cmap, drawedges=False)
            cbar.solids.set_edgecolor("face")
            cbar.set_label(label="$"+units+"$",size=subplot.GetColorBarProperty("FontSize"))
            i += 1
            
            # label axes
            ax.xaxis.set_major_locator( LinearLocator(5) )
            ax.set_xlabel(subplot.GetAxisProperty("x", "LabelText") + " $["+subplot.GetAxisProperty("x", "Units")+"]$", fontsize=subplot.GetAxisProperty("x", "LabelFontSize"))
            ax.set_ylabel(subplot.GetAxisProperty("y", "LabelText") + " $["+subplot.GetAxisProperty("y", "Units")+"]$", fontsize=subplot.GetAxisProperty("y", "LabelFontSize"))
            ax.set_title(subplot.GetTitleProperty("Text"), fontsize=subplot.GetTitleProperty("FontSize"))
        
        if num1DFields > 0 and num2DFields > 0:
            axPos = ax.get_position()
            newAxPos = [axPos.x0, axPos.y0 ,  axPos.width-0.07, axPos.height]
            ax.set_position(newAxPos)
        for field in subplot.GetFieldsToPlotWithDimension("1D"):
            units = field.GetFieldUnits()
            if num2DFields > 0:
                axPos = ax.get_position()
                axis1D = ax.twinx()
                axis1D.set_position(axPos)
            else:
                axis1D = ax
                
            plotData = field.GetFieldPlotData(timeStep)
            self.plotTypes["Field"][field.GetPlotType()](axis1D, plotData)   
            
            if num2DFields > 0:
                axis1D.set_ylabel("$"+units+"$")
            else:
                axis1D.xaxis.set_major_locator( LinearLocator(5) )
                axis1D.set_xlabel(subplot.GetAxisProperty("x", "LabelText") + " $["+subplot.GetAxisProperty("x", "Units")+"]$", fontsize=subplot.GetAxisProperty("x", "LabelFontSize"))
                axis1D.set_ylabel("$"+units+"$")
                axis1D.set_title(subplot.GetTitleProperty("Text"), fontsize=subplot.GetTitleProperty("FontSize"))
        
        
        
    def MakeAxisDataPlot(self, figure, ax, subplot, rows, columns, timeStep):
        plotData = subplot.GetAxisData()
        xData = plotData["x"].GetDataSetPlotData(timeStep)
        yData = plotData["y"].GetDataSetPlotData(timeStep)
        weightData = plotData["weight"].GetDataSetPlotData(timeStep)
        
        xValues = xData[0]
        yValues = yData[0]
        weightValues = weightData[0]
        
        cMap = self.colorMapsCollection.GetColorMap(subplot.GetPlotProperty("CMap"))
        
        im = self.plotTypes["Axis"][subplot.GetPlotProperty("PlotType")](ax, xValues, yValues, weightValues, cMap)
        
        pos1 = ax.get_position()
        pos2 = [pos1.x0, pos1.y0 ,  pos1.width-0.1, pos1.height]
        ax.set_position(pos2)
        ax.hold(True)
        
        cbWidth = 0.015
        cbHeight = pos2[3]
        cbX = pos2[0] + pos2[2] + 0.02
        cbY = pos2[1]
        
        cbAxes = figure.add_axes([cbX, cbY, cbWidth, cbHeight]) 
        cbar = figure.colorbar(im, cax = cbAxes, cmap=cMap, drawedges=False)
        cbar.solids.set_edgecolor("face")
        cbar.set_label(label="$"+plotData["weight"].GetUnits()+"$",size=subplot.GetColorBarProperty("FontSize"))
        
        # label axes
        ax.xaxis.set_major_locator( LinearLocator(5) )
        ax.set_xlabel(subplot.GetAxisProperty("x", "LabelText") + " $["+subplot.GetAxisProperty("x", "Units")+"]$", fontsize=subplot.GetAxisProperty("x", "LabelFontSize"))
        ax.set_ylabel(subplot.GetAxisProperty("y", "LabelText") + " $["+subplot.GetAxisProperty("y", "Units")+"]$", fontsize=subplot.GetAxisProperty("y", "LabelFontSize"))
        ax.set_title(subplot.GetTitleProperty("Text"), fontsize=subplot.GetTitleProperty("FontSize"))
        
# Field data plot types
    def MakeImagePlot(self, ax, plotData, cMap, scale, isScaleCustom):  
        if not isScaleCustom:
            scale = [None, None]
            
        return ax.imshow(plotData[0], extent = plotData[1], aspect='auto', cmap=cMap, vmin=scale[0], vmax = scale[1])
        
    def MakeSurfacePlot(self, ax, plotData, cMap, scale, isScaleCustom):  
        if not isScaleCustom:
            scale = [None, None]
        elementsX = len(plotData[0][0]) # longitudinal
        elementsY = len(plotData[0]) # transverse
        xMin = plotData[1][0]
        xMax = plotData[1][1]
        yMin = plotData[1][2]
        yMax = plotData[1][3]
        x = np.linspace(xMin, xMax, elementsX)
        y = np.linspace(yMin, yMax, elementsY)
        X, Y = np.meshgrid(x,y)
        Z = plotData[0]
        
        cStride = round(elementsX/40)
        rStride = round(elementsY/40)
        return ax.plot_surface(X, Y, Z, cmap=cMap, linewidth=0.0, antialiased=False, shade=False, rstride=rStride, cstride=cStride, vmin=scale[0], vmax = scale[1])
   
    def MakeLinePlot(self, ax, plotData):
        xValues = plotData[0]
        yValues = plotData[1]
        ax.plot(xValues, yValues)
        ax.set_xlim([xValues[0], xValues[-1]])
        
        
# Axis data plot types     
    def MakeHistogramPlot(self, ax, xValues, yValues, weightValues, cMap):
        H, xedges, yedges = np.histogram2d(xValues, yValues, bins = 80, weights = weightValues)
        extent = xedges[0], xedges[-1], yedges[0], yedges[-1]
        return ax.imshow(H.transpose(), extent=extent, cmap=cMap, aspect='auto', origin='lower')
        
    def MakeScatterPlot(self, ax, xValues, yValues, weightValues, cMap):
        return ax.scatter(xValues, yValues, c=weightValues, cmap=cMap, linewidths=0)
    