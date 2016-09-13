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
            "Raw":self.MakeAxisDataPlot,
            "RawEvolution":self.MakeRawEvolutionDataPlot
            }
            
    def LoadPlotTypes(self):
        fieldTypes ={
            "Image":self.MakeImagePlot,
            "Surface":self.MakeSurfacePlot,
            "Line":self.MakeLinePlot
            }
        axisTypes = {
            "Scatter":self.MakeScatterPlot,
            "Scatter3D":self.Make3DScatterPlot,
            "Histogram":self.MakeHistogramPlot
            }
        evolutionTypes = {
            "2D":self.MakeLinePlot_E,
            "3D":self.Make3DLinePlot_E
            }
        self.plotTypes = {
            "Field":fieldTypes,
            "Raw":axisTypes,
            "RawEvolution":evolutionTypes
            }
    # todo: remove timeStep from input variables. Allow to have diferent number of input variables.        
    def MakePlot(self, figure, subplotList, rows, columns, timeStep = None):
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
            plotData = field.GetData(timeStep)
            units = field.GetProperty("fieldUnits")
            field_cmap = self.colorMapsCollection.GetColorMap(field.GetProperty("cMap"))
            scale = field.GetProperty("minVal"), field.GetProperty("maxVal")
            autoScale = field.GetProperty("autoScale")
            # make plot
            im = self.plotTypes["Field"][field.GetProperty("plotType")](ax, plotData, field_cmap, scale, autoScale)
            # change plot size to make room for the colorBar
            if i == 0:
                pos1 = ax.get_position()
                pos2 = [pos1.x0, pos1.y0 ,  pos1.width-0.1, pos1.height]
                ax.set_position(pos2)
            ax.hold(True)
            # colorBar
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
            units = field.GetProperty("fieldUnits")
            if num2DFields > 0:
                axPos = ax.get_position()
                axis1D = ax.twinx()
                axis1D.set_position(axPos)
            else:
                axis1D = ax
            plotData = field.GetData(timeStep)
            self.plotTypes["Field"][field.GetProperty("plotType")](axis1D, plotData)  
            if num2DFields > 0:
                axis1D.set_ylabel("$"+units+"$")
            else:
                axis1D.xaxis.set_major_locator( LinearLocator(5) )
                axis1D.set_xlabel(subplot.GetAxisProperty("x", "LabelText") + " $["+subplot.GetAxisProperty("x", "Units")+"]$", fontsize=subplot.GetAxisProperty("x", "LabelFontSize"))
                axis1D.set_ylabel("$"+units+"$")
                axis1D.set_title(subplot.GetTitleProperty("Text"), fontsize=subplot.GetTitleProperty("FontSize"))
        
    def MakeAxisDataPlot(self, figure, ax, subplot, rows, columns, timeStep):
        axisData = subplot.GetDataToPlot()
        plotData = {}
        plotData["x"] = axisData["x"].GetDataSetPlotData(timeStep)
        plotData["y"] = axisData["y"].GetDataSetPlotData(timeStep)
        if "z" in axisData:
            plotData["z"] = axisData["z"].GetDataSetPlotData(timeStep)
        if "weight" in axisData:
            plotData["weight"] = axisData["weight"].GetDataSetPlotData(timeStep)
        cMap = self.colorMapsCollection.GetColorMap(subplot.GetPlotProperty("CMap"))
        # make plot
        im = self.plotTypes["Raw"][subplot.GetPlotProperty("PlotType")](ax, plotData, cMap)
        # change plot size to make room for the colorBar
        pos1 = ax.get_position()
        pos2 = [pos1.x0, pos1.y0 ,  pos1.width-0.1, pos1.height]
        ax.set_position(pos2)
        ax.hold(True)
        # colorBar
        if "weight" in axisData:
            cbWidth = 0.015
            cbHeight = pos2[3]
            cbX = pos2[0] + pos2[2] + 0.02
            cbY = pos2[1]
            cbAxes = figure.add_axes([cbX, cbY, cbWidth, cbHeight]) 
            cbar = figure.colorbar(im, cax = cbAxes, cmap=cMap, drawedges=False)
            cbar.solids.set_edgecolor("face")
            cbar.set_label(label="$"+axisData["weight"].GetProperty("dataSetUnits")+"$",size=subplot.GetColorBarProperty("FontSize"))
        # label axes
        ax.xaxis.set_major_locator( LinearLocator(5) )
        ax.set_xlabel(subplot.GetAxisProperty("x", "LabelText") + " $["+subplot.GetAxisProperty("x", "Units")+"]$", fontsize=subplot.GetAxisProperty("x", "LabelFontSize"))
        ax.set_ylabel(subplot.GetAxisProperty("y", "LabelText") + " $["+subplot.GetAxisProperty("y", "Units")+"]$", fontsize=subplot.GetAxisProperty("y", "LabelFontSize"))
        ax.set_title(subplot.GetTitleProperty("Text"), fontsize=subplot.GetTitleProperty("FontSize"))

    def MakeRawEvolutionDataPlot(self, figure, ax, subplot, rows, columns, timeStep):
        ax.hold(False)
        allPaticlesData = subplot.GetDataToPlot() # list of dictionaries (with keys "particle", "x", "y" and "z")
        for particleData in allPaticlesData:
            plotData = {}
            plotData["x"] = particleData["x"].GetDataSetPlotData()
            plotData["y"] = particleData["y"].GetDataSetPlotData()
            if "z" in particleData:
                plotData["z"] = particleData["z"].GetDataSetPlotData()
            # make plot
            im = self.plotTypes["RawEvolution"][subplot.GetAxesDimension()](ax, plotData, particleData["plotStyle"])
            ax.hold(True)
        # label axes
        ax.xaxis.set_major_locator( LinearLocator(5) )
        ax.set_xlabel(subplot.GetAxisProperty("x", "LabelText") + " $["+subplot.GetAxisProperty("x", "Units")+"]$", fontsize=subplot.GetAxisProperty("x", "LabelFontSize"))
        ax.set_ylabel(subplot.GetAxisProperty("y", "LabelText") + " $["+subplot.GetAxisProperty("y", "Units")+"]$", fontsize=subplot.GetAxisProperty("y", "LabelFontSize"))
        ax.set_title(subplot.GetTitleProperty("Text"), fontsize=subplot.GetTitleProperty("FontSize"))

    """
    Field data plot types
    """
    def MakeImagePlot(self, ax, plotData, cMap, scale, autoScale):  
        if autoScale:
            scale = [None, None]
        fieldData = plotData[-1]
        yAxisData = plotData[-2]
        xAxisData = plotData[-3]
        axesLimits =[min(xAxisData), max(xAxisData), min(yAxisData), max(yAxisData)]
        return ax.imshow(fieldData, extent = axesLimits, aspect='auto', cmap=cMap, vmin=scale[0], vmax = scale[1], origin="lower")
        
    def MakeSurfacePlot(self, ax, plotData, cMap, scale, autoScale):  
        if autoScale:
            scale = [None, None]
        x = plotData[-3]
        y = plotData[-2]
        X, Y = np.meshgrid(x,y)
        Z = plotData[-1]
        cStride = 100
        rStride = 100
        return ax.plot_surface(X, Y, Z, cmap=cMap, linewidth=0.0, antialiased=False, shade=False, rstride=rStride, cstride=cStride, vmin=scale[0], vmax = scale[1])
   
    def MakeLinePlot(self, ax, plotData, plotStyle = "b-"):
        xValues = plotData[-2]
        yValues = plotData[-1]
        ax.plot(xValues, yValues, plotStyle)
        ax.set_xlim([xValues[0], xValues[-1]])
        
    """
    Raw (non-evolving) data plot types
    """    
    def MakeHistogramPlot(self, ax, plotData, cMap):
        xValues = plotData["x"]
        yValues = plotData["y"]
        weightValues = plotData["weight"]
        H, xedges, yedges = np.histogram2d(xValues, yValues, bins = 80, weights = weightValues)
        extent = xedges[0], xedges[-1], yedges[0], yedges[-1]
        return ax.imshow(H.transpose(), extent=extent, cmap=cMap, aspect='auto', origin='lower')
        
    def MakeScatterPlot(self, ax, plotData, cMap):
        xValues = plotData["x"]
        yValues = plotData["y"]
        if "weight" in plotData:
            weightValues = plotData["weight"]
            return ax.scatter(xValues, yValues, c=weightValues, cmap=cMap, linewidths=0)
        else:
            return ax.scatter(xValues, yValues, cmap=cMap, linewidths=0)
        
    def Make3DScatterPlot(self, ax, plotData, cMap):
        xValues = plotData["x"]
        yValues = plotData["y"]
        zValues = plotData["z"]
        if "weight" in plotData:
            weightValues = plotData["weight"]
            return ax.scatter(xValues, yValues, zValues, c=weightValues, cmap=cMap, linewidths=0)
        else:
            return ax.scatter(xValues, yValues, zValues, cmap=cMap, linewidths=0)
    
    """
    Raw (evolving) data plot types
    """ 
    def MakeLinePlot_E(self, ax, plotData, plotStyle = "b-"):
        xValues = plotData["x"]
        yValues = plotData["y"]
        ax.plot(xValues, yValues, plotStyle)
        #ax.set_xlim([min(xValues), max(xValues)]) #if active, it might cause the bounds to be too small when "ax.hold" is true because the bound will be set as the maximum and minimum of the last data set.

    def Make3DLinePlot_E(self, ax, plotData, plotStyle = "b-"):
        raise NotImplementedError