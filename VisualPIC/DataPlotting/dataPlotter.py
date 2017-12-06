# -*- coding: utf-8 -*-

#Copyright 2016-2017 Angel Ferran Pousa, DESY
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
#from matplotlib.ticker import FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import ticker

class DataPlotter:
    def __init__(self, colorMapsCollection):
        self.testprop = 0
        self.currentAxesNumber = 1
        self.colorMapsCollection = colorMapsCollection
        self.cbSpacing = 0.02 # vertical space between color bars
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
            "Histogram":self.MakeHistogramPlot,
            "Arrows":self.MakeArrowPlot
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
                # set axis limits
                ax.set_xlim([subplot.GetAxisProperty("x", "AxisLimits")["Min"],subplot.GetAxisProperty("x", "AxisLimits")["Max"]])
                ax.set_autoscalex_on(subplot.GetAxisProperty("x", "AutoAxisLimits"))
                ax.set_ylim([subplot.GetAxisProperty("y", "AxisLimits")["Min"],subplot.GetAxisProperty("y", "AxisLimits")["Max"]])
                ax.set_autoscaley_on(subplot.GetAxisProperty("y", "AutoAxisLimits"))
                if subplot.GetAxesDimension() == "3D":
                    if not subplot.GetAxisProperty("z", "AutoAxisLimits"):
                        ax.set_zlim([subplot.GetAxisProperty("z", "AxisLimits")["Min"],subplot.GetAxisProperty("z", "AxisLimits")["Max"]])

                # make plot on axes
                self.PlotFromDataType[subplot.GetDataType()](figure, ax, subplot, rows, columns, timeStep)

    def MakeFieldPlot(self, figure, ax, subplot, rows, columns, timeStep):
        num1DFields = len(subplot.GetFieldsToPlotWithDimension("1D"))
        num2DFields = len(subplot.GetFieldsToPlotWithDimension("2D"))
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
            # colorBar
            cbWidth = 0.015
            cbHeight = (pos2[3]-(num2DFields-1)*self.cbSpacing)/num2DFields
            cbX = pos2[0] + pos2[2] + 0.02
            cbY = pos2[1] + i*(cbHeight + self.cbSpacing)
            cbAxes = figure.add_axes([cbX, cbY, cbWidth, cbHeight]) 
            cbar = figure.colorbar(im, cax = cbAxes, cmap=field_cmap, drawedges=False)
            cbar.solids.set_edgecolor("face")
            cbar.set_label(label="$"+units+"$",size=subplot.GetColorBarProperty("FontSize"))
            tick_locator = ticker.MaxNLocator(nbins=int(10/num2DFields))
            cbar.locator = tick_locator
            cbar.update_ticks()
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
            axis1D = ax.twinx()
            axis1D.set_position(axPos)
        elif num1DFields > 0:
            axis1D = ax
        for field in subplot.GetFieldsToPlotWithDimension("1D"):
            units = field.GetProperty("fieldUnits")
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
        #ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        axisData = subplot.GetDataToPlot()
        plotProperties = subplot.GetCopyAllPlotProperties()
        axisProperties = subplot.GetCopyAllAxesProperties()
        plotData = {}
        # Load data
        for dataSetName, values in axisData.items():
            plotData[dataSetName] = axisData[dataSetName].GetDataSetPlotData(timeStep)
        cMap = self.colorMapsCollection.GetColorMap(subplot.GetPlotProperty(subplot.GetPlotType(),"CMap"))
        # make plot
        im = self.plotTypes["Raw"][subplot.GetPlotType()](ax, plotData, plotProperties, axisProperties, cMap)
        # colorBar
        if subplot.GetPlotProperty("General", "DisplayColorbar") == True:
            # change plot size to make room for the colorBar
            pos1 = ax.get_position()
            pos2 = [pos1.x0, pos1.y0 ,  pos1.width-0.1, pos1.height]
            ax.set_position(pos2)
            cbWidth = 0.015
            cbHeight = pos2[3]
            cbX = pos2[0] + pos2[2] + 0.02
            cbY = pos2[1]
            cbAxes = figure.add_axes([cbX, cbY, cbWidth, cbHeight]) 
            cbar = figure.colorbar(im, cax = cbAxes, cmap=cMap, drawedges=False)
            cbar.solids.set_edgecolor("face")
            if subplot.GetPlotType() == "Histogram" or subplot.GetPlotType() == "Scatter":
                cbar.set_label(label="$"+axisData["weight"].GetProperty("dataSetUnits")+"$",size=subplot.GetColorBarProperty("FontSize"))
            elif subplot.GetPlotType() == "Arrows":
                cbar.set_label(label="$"+axisData["Px"].GetProperty("dataSetUnits")+"$",size=subplot.GetColorBarProperty("FontSize"))
        # label axes
        ax.xaxis.set_major_locator( LinearLocator(5) )
        ax.set_xlabel(subplot.GetAxisProperty("x", "LabelText") + " $["+subplot.GetAxisProperty("x", "Units")+"]$", fontsize=subplot.GetAxisProperty("x", "LabelFontSize"))
        ax.set_ylabel(subplot.GetAxisProperty("y", "LabelText") + " $["+subplot.GetAxisProperty("y", "Units")+"]$", fontsize=subplot.GetAxisProperty("y", "LabelFontSize"))
        if subplot.GetAxesDimension() == "3D":
            ax.set_zlabel(subplot.GetAxisProperty("z", "LabelText") + " $["+subplot.GetAxisProperty("z", "Units")+"]$", fontsize=subplot.GetAxisProperty("z", "LabelFontSize"))
        ax.set_title(subplot.GetTitleProperty("Text"), fontsize=subplot.GetTitleProperty("FontSize"))

    def MakeRawEvolutionDataPlot(self, figure, ax, subplot, rows, columns, timeStep):
        allPaticlesData = subplot.GetDataToPlot() # list of dictionaries (with keys "particle", "x", "y" and "z")
        for particleData in allPaticlesData:
            plotData = {}
            plotData["x"] = particleData["x"].GetDataSetPlotData()
            plotData["y"] = particleData["y"].GetDataSetPlotData()
            if "z" in particleData:
                plotData["z"] = particleData["z"].GetDataSetPlotData()
            # make plot
            im = self.plotTypes["RawEvolution"][subplot.GetAxesDimension()](ax, plotData, particleData["plotStyle"])
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
        return ax.imshow(fieldData, extent = axesLimits, aspect='auto', cmap=cMap, vmin=scale[0], vmax = scale[1], origin="lower", interpolation='none')
        
    def MakeSurfacePlot(self, ax, plotData, cMap, scale, autoScale):  
        if autoScale:
            scale = [None, None]
        x = plotData[-3]
        y = plotData[-2]
        X, Y = np.meshgrid(x,y)
        Z = plotData[-1]
        cStride = 10
        rStride = 10
        return ax.plot_surface(X, Y, Z, cmap=cMap, linewidth=0.0, antialiased=True, shade=False, rstride=rStride, cstride=cStride, vmin=scale[0], vmax = scale[1])
   
    def MakeLinePlot(self, ax, plotData, plotStyle = 'C0'):
        xValues = plotData[-2]
        yValues = plotData[-1]
        ax.plot(xValues, yValues, plotStyle)
        ax.set_xlim([xValues[0], xValues[-1]])
        
    """
    Raw (non-evolving) data plot types
    """  
    #todo: change cMap argument for a plotSettings argument.
    def MakeArrowPlot(self, ax, plotData, plotProperties, axisProperties, cMap):
        xValues = plotData["x"]
        yValues = plotData["y"]
        pxValues = plotData["Px"]
        pyValues = plotData["Py"]
        H, xedges, yedges = np.histogram2d(xValues, yValues, bins = 100) # H contains the number of macroparticles in each histogram cell
        Hpx, xedges, yedges = np.histogram2d(xValues, yValues, bins = 100, weights = pxValues) # Hpx contains the total x component of the momentum in each histogram cell
        Hpy, xedges, yedges = np.histogram2d(xValues, yValues, bins = 100, weights = pyValues) # Hpy contains the total y component of the momentum in each histogram cell
        px = self.div0(Hpx,H) # average value of Px in each cell
        py = self.div0(Hpy,H) # average value of Py in each cell

        xLeft = xedges[:-1] + np.abs((xedges[1]-xedges[0]))/2
        yLeft = yedges[:-1] + np.abs((yedges[1]-yedges[0]))/2
        X, Y = np.meshgrid(xLeft, yLeft)
        modP = np.hypot(px,py) # modulus of the average P in each cell (used for normalization)
        pxN = self.div0(px,np.max(modP))
        pyN = self.div0(py,np.max(modP))
        
        #extent = xedges[0], xedges[-1], yedges[0], yedges[-1]
        #return ax.imshow(py.transpose(), extent=extent, cmap=cMap, aspect='auto', origin='lower')
        ax.set_xlim([min(xedges), max(xedges)])
        ax.set_ylim([min(yedges), max(yedges)])
        return ax.quiver(X, Y, pxN.transpose(), pyN.transpose(), modP.transpose(),
            scale=100,
            pivot='mid',                                           
            cmap=cMap)

    def MakeHistogramPlot(self, ax, plotData, plotProperties, axisProperties, cMap):
        xValues = plotData["x"]
        yValues = plotData["y"]
        weightValues = plotData["weight"]
        histogramProperties = plotProperties["Histogram"]
        histBins = [histogramProperties["Bins"]["XBins"], histogramProperties["Bins"]["YBins"]]
        if axisProperties["x"]["AutoAxisLimits"]:
            x_lims = [min(xValues), max(xValues)]
        else:
            x_lims = [axisProperties["x"]["AxisLimits"]["Min"], axisProperties["x"]["AxisLimits"]["Max"]]
        if axisProperties["y"]["AutoAxisLimits"]:
            y_lims = [min(yValues), max(yValues)]
        else:
            y_lims = [axisProperties["y"]["AxisLimits"]["Min"], axisProperties["y"]["AxisLimits"]["Max"]]
        hist_range = [x_lims, y_lims]
        if histogramProperties["UseChargeWeighting"]:
            H, xedges, yedges = np.histogram2d(xValues, yValues, bins = histBins, weights = weightValues, range=hist_range)
        else:
            H, xedges, yedges = np.histogram2d(xValues, yValues, bins = histBins, range=hist_range)
        extent = xedges[0], xedges[-1], yedges[0], yedges[-1]
        return ax.imshow(H.transpose(), extent=extent, cmap=cMap, aspect='auto', origin='lower')
        #if histogramProperties["UseChargeWeighting"]:
        #    H, xedges, yedges = np.histogram2d(xValues, yValues, bins = histBins, weights = weightValues, range=hist_range)
        #    H_count, xedges, yedges = np.histogram2d(xValues, yValues, bins = histBins, range=hist_range)
        #    H = H/H_count
        #    H = H.transpose()
        #    s = H.shape
        #    H = H - H[int(s[0]/2),:]
        #else:
        #    H, xedges, yedges = np.histogram2d(xValues, yValues, bins = histBins, range=hist_range)
        #extent = xedges[0], xedges[-1], yedges[0], yedges[-1]
        #return ax.imshow(H, extent=extent, cmap=cMap, aspect='auto', origin='lower')
        
    def MakeScatterPlot(self, ax, plotData, plotProperties, axisProperties, cMap):
        xValues = plotData["x"]
        yValues = plotData["y"]
        scatterProperties = plotProperties["Scatter"]
        if scatterProperties["UseChargeWeighting"]:
            weightValues = plotData["weight"]
            return ax.scatter(xValues, yValues, c=weightValues, cmap=cMap, linewidths=0)
        else:
            return ax.scatter(xValues, yValues, cmap=cMap, linewidths=0)
        
    def Make3DScatterPlot(self, ax, plotData, plotProperties, axisProperties, cMap):
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

    """
    Helpers
    """
    def div0(self, a, b ):
        """ Return 0 whrn dividing by 0. Ignore / 0, div0( [-1, 0, 1], 0 ) -> [0, 0, 0] """
        with np.errstate(divide='ignore', invalid='ignore'):
            c = np.true_divide( a, b )
            c[ ~ np.isfinite( c )] = 0  # -inf inf NaN
        return c