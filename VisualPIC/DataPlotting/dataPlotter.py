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
    # todo: remove time_step from input variables. Allow to have diferent number of input variables.        
    def MakePlot(self, figure, subplotList, rows, columns, time_step = None):
        self.currentAxesNumber = rows*columns
        for ax in figure.axes:
            figure.delaxes(ax)
        figure.subplots_adjust(hspace=.3, top=.93, bottom=.09, right = .93, left = .09)
        for subplot in subplotList:
            if subplot != None:
                # create axes
                if subplot.get_axes_dimension() == "3D":
                    ax = figure.add_subplot(rows,columns,subplot.get_position(), projection='3d')
                else:
                    ax = figure.add_subplot(rows,columns,subplot.get_position())
                # set axis limits
                ax.set_xlim([subplot.get_axis_property("x", "AxisLimits")["Min"],subplot.get_axis_property("x", "AxisLimits")["Max"]])
                ax.set_autoscalex_on(subplot.get_axis_property("x", "AutoAxisLimits"))
                ax.set_ylim([subplot.get_axis_property("y", "AxisLimits")["Min"],subplot.get_axis_property("y", "AxisLimits")["Max"]])
                ax.set_autoscaley_on(subplot.get_axis_property("y", "AutoAxisLimits"))
                if subplot.get_axes_dimension() == "3D":
                    if not subplot.get_axis_property("z", "AutoAxisLimits"):
                        ax.set_zlim([subplot.get_axis_property("z", "AxisLimits")["Min"],subplot.get_axis_property("z", "AxisLimits")["Max"]])

                # make plot on axes
                self.PlotFromDataType[subplot.get_data_type()](figure, ax, subplot, rows, columns, time_step)

    def MakeFieldPlot(self, figure, ax, subplot, rows, columns, time_step):
        num1DFields = len(subplot.get_fields_to_plot_with_dimension("1D"))
        num2DFields = len(subplot.get_fields_to_plot_with_dimension("2D"))
        i = 0
        for field in subplot.get_fields_to_plot_with_dimension("2D"):
            plotData = field.get_data(time_step)
            units = field.get_property("fieldUnits")
            field_cmap = self.colorMapsCollection.GetColorMap(field.get_property("cMap"))
            scale = field.get_property("minVal"), field.get_property("maxVal")
            autoScale = field.get_property("autoScale")
            # make plot
            im = self.plotTypes["Field"][field.get_property("plotType")](ax, plotData, field_cmap, scale, autoScale)
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
            cbar.set_label(label="$"+units+"$",size=subplot.get_cbar_property("FontSize"))
            tick_locator = ticker.MaxNLocator(nbins=int(10/num2DFields))
            cbar.locator = tick_locator
            cbar.update_ticks()
            i += 1
            # label axes
            ax.xaxis.set_major_locator( LinearLocator(5) )
            ax.set_xlabel(subplot.get_axis_property("x", "LabelText") + " $["+subplot.get_axis_property("x", "Units")+"]$", fontsize=subplot.get_axis_property("x", "LabelFontSize"))
            ax.set_ylabel(subplot.get_axis_property("y", "LabelText") + " $["+subplot.get_axis_property("y", "Units")+"]$", fontsize=subplot.get_axis_property("y", "LabelFontSize"))
            ax.set_title(subplot.get_title_property("Text"), fontsize=subplot.get_title_property("FontSize"))
        if num1DFields > 0 and num2DFields > 0:
            axPos = ax.get_position()
            newAxPos = [axPos.x0, axPos.y0 ,  axPos.width-0.07, axPos.height]
            ax.set_position(newAxPos)
            axis1D = ax.twinx()
            axis1D.set_position(axPos)
        elif num1DFields > 0:
            axis1D = ax
        for field in subplot.get_fields_to_plot_with_dimension("1D"):
            units = field.get_property("fieldUnits")
            plotData = field.get_data(time_step)
            self.plotTypes["Field"][field.get_property("plotType")](axis1D, plotData)  
            if num2DFields > 0:
                axis1D.set_ylabel("$"+units+"$")
            else:
                axis1D.xaxis.set_major_locator( LinearLocator(5) )
                axis1D.set_xlabel(subplot.get_axis_property("x", "LabelText") + " $["+subplot.get_axis_property("x", "Units")+"]$", fontsize=subplot.get_axis_property("x", "LabelFontSize"))
                axis1D.set_ylabel("$"+units+"$")
                axis1D.set_title(subplot.get_title_property("Text"), fontsize=subplot.get_title_property("FontSize"))
        
    def MakeAxisDataPlot(self, figure, ax, subplot, rows, columns, time_step):
        #ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        axisData = subplot.get_data_to_plot()
        plotProperties = subplot.get_copy_all_plot_properties()
        axisProperties = subplot.get_copy_all_axes_properties()
        plotData = {}
        # Load data
        for dataSetName, values in axisData.items():
            plotData[dataSetName] = axisData[dataSetName].GetDataSetPlotData(time_step)
        cMap = self.colorMapsCollection.GetColorMap(subplot.get_plot_property(subplot.get_plot_type(),"CMap"))
        # make plot
        im = self.plotTypes["Raw"][subplot.get_plot_type()](ax, plotData, plotProperties, axisProperties, cMap)
        # colorBar
        if subplot.get_plot_property("General", "DisplayColorbar") == True:
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
            if subplot.get_plot_type() == "Histogram" or subplot.get_plot_type() == "Scatter":
                cbar.set_label(label="$"+axisData["weight"].get_property("dataSetUnits")+"$",size=subplot.get_cbar_property("FontSize"))
            elif subplot.get_plot_type() == "Arrows":
                cbar.set_label(label="$"+axisData["Px"].get_property("dataSetUnits")+"$",size=subplot.get_cbar_property("FontSize"))
        # label axes
        ax.xaxis.set_major_locator( LinearLocator(5) )
        ax.set_xlabel(subplot.get_axis_property("x", "LabelText") + " $["+subplot.get_axis_property("x", "Units")+"]$", fontsize=subplot.get_axis_property("x", "LabelFontSize"))
        ax.set_ylabel(subplot.get_axis_property("y", "LabelText") + " $["+subplot.get_axis_property("y", "Units")+"]$", fontsize=subplot.get_axis_property("y", "LabelFontSize"))
        if subplot.get_axes_dimension() == "3D":
            ax.set_zlabel(subplot.get_axis_property("z", "LabelText") + " $["+subplot.get_axis_property("z", "Units")+"]$", fontsize=subplot.get_axis_property("z", "LabelFontSize"))
        ax.set_title(subplot.get_title_property("Text"), fontsize=subplot.get_title_property("FontSize"))

    def MakeRawEvolutionDataPlot(self, figure, ax, subplot, rows, columns, time_step):
        allPaticlesData = subplot.get_data_to_plot() # list of dictionaries (with keys "particle", "x", "y" and "z")
        for particleData in allPaticlesData:
            plotData = {}
            plotData["x"] = particleData["x"].GetDataSetPlotData()
            plotData["y"] = particleData["y"].GetDataSetPlotData()
            if "z" in particleData:
                plotData["z"] = particleData["z"].GetDataSetPlotData()
            # make plot
            im = self.plotTypes["RawEvolution"][subplot.get_axes_dimension()](ax, plotData, particleData["plotStyle"])
        # label axes
        ax.xaxis.set_major_locator( LinearLocator(5) )
        ax.set_xlabel(subplot.get_axis_property("x", "LabelText") + " $["+subplot.get_axis_property("x", "Units")+"]$", fontsize=subplot.get_axis_property("x", "LabelFontSize"))
        ax.set_ylabel(subplot.get_axis_property("y", "LabelText") + " $["+subplot.get_axis_property("y", "Units")+"]$", fontsize=subplot.get_axis_property("y", "LabelFontSize"))
        ax.set_title(subplot.get_title_property("Text"), fontsize=subplot.get_title_property("FontSize"))

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