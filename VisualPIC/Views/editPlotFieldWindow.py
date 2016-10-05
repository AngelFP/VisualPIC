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

import sys
import os

from PyQt4.uic import loadUiType
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *

from VisualPIC.DataHandling.fieldToPlot import FieldToPlot
from VisualPIC.DataHandling.subplot import *

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

if getattr(sys, 'frozen', False):
    # we are running in a bundle
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
guipath = os.path.join( bundle_dir, 'EditPlotFieldWindow.ui' )

Ui_EditPlotFieldWindow, QEditPlotFieldWindow = loadUiType(guipath)

class EditPlotWindow(QEditPlotFieldWindow, Ui_EditPlotFieldWindow):
    def __init__(self, subplot, parent=None):
        super(EditPlotWindow, self).__init__()
        self.setupUi(self)
        self.mainWindow = parent
        self.subplot = subplot
        self.selectedFieldIndex = 0
        self.updatingUiData = True
        
        self.RegisterUIEvents()
        self.SetVisibleTabs()
        self.GetAxisProperties()
        self.GetColorbarProperties()
        self.GetTitleProperties()

    def RegisterUIEvents(self):
        # Fields tab
        self.field_listView.clicked.connect(self.FieldListView_Clicked)
        self.auto_checkBox.toggled.connect(self.AutoCheckBox_StatusChanged)
        self.min_lineEdit.textChanged.connect(self.MinMaxLineEdit_textChanged)
        self.max_lineEdit.textChanged.connect(self.MinMaxLineEdit_textChanged)
        self.colorMap_comboBox.currentIndexChanged.connect(self.SetColorMap)
        self.fieldUnits_comboBox.currentIndexChanged.connect(self.SetFieldUnits)
        self.apply_button.clicked.connect(self.ApplyButton_Clicked)
        self.accept_button.clicked.connect(self.AcceptButton_Clicked)
        self.cancel_button.clicked.connect(self.CancelButton_Clicked)
        self.plotType_comboBox.currentIndexChanged.connect(self.PlotTypeComboBox_IndexChanged)
        self.removeField_button.clicked.connect(self.RemoveFieldButton_Clicked)
        # Plot settings tab
        self.axisPlotType_comboBox.currentIndexChanged.connect(self.AxisPlotTypeComboBox_IndexChanged)
        self.chargeUnits_comboBox.currentIndexChanged.connect(self.ChargeUnitsComboBox_IndexChanged)
        self.axisColorMap_comboBox.currentIndexChanged.connect(self.AxisColorMapComboBox_IndexChanged)
        self.chargeWeight_checkBox.toggled.connect(self.ChargeWeightCheckBox_StatusChanged)
        self.displayColorbar_checkBox.toggled.connect(self.DisplayColorbarCheckBox_StatusChanged)
        # Axes tab
        self.xUnits_comboBox.currentIndexChanged.connect(self.SetXAxisUnits)
        self.yUnits_comboBox.currentIndexChanged.connect(self.SetYAxisUnits)
        self.xAutoLabel_checkBox.toggled.connect(self.XAutoLabelCheckBox_statusChanged)
        self.yAutoLabel_checkBox.toggled.connect(self.YAutoLabelCheckBox_statusChanged)
        self.xAutoLabel_lineEdit.textChanged.connect(self.XAutoLabelLineEdit_textChanged)
        self.yAutoLabel_lineEdit.textChanged.connect(self.YAutoLabelLineEdit_textChanged)
        self.xFontSize_spinBox.valueChanged.connect(self.XFontSizeSpinBox_valueChanged)
        self.yFontSize_spinBox.valueChanged.connect(self.YFontSizeSpinBox_valueChanged)
        self.autoTitle_checkBox.toggled.connect(self.AutoTitleCheckBox_statusChanged)
        self.titleFontSize_spinBox.valueChanged.connect(self.TitleFontSizeSpinBox_valueChanged)
        self.autoTitle_lineEdit.textChanged.connect(self.AutoTitleLineEdit_textChanged)
        # Colorbar tab
        self.cbAutoLabel_checkBox.toggled.connect(self.CbAutoLabelCheckBox_statusChanged)
        self.cbFontSize_spinBox.valueChanged.connect(self.CbFontSizeSpinBox_valueChanged)
        # 1D Slices tab
        self.speciesFieldsSlice_radioButton.toggled.connect(self.FieldSliceTypeRadioButton_Toggled)
        self.domainFieldsSlice_radioButton.toggled.connect(self.FieldSliceTypeRadioButton_Toggled)
        self.speciesSelectorSlice_comboBox.currentIndexChanged.connect(self.SpeciesSelectorSliceComboBox_IndexChanged)
        self.addSlice_button.clicked.connect(self.AddSliceButton_Clicked)

    def SetVisibleTabs(self):
        raise NotImplementedError

    def GetAxisProperties(self):
        self.axisProperties = {
            "x":self.subplot.GetCopyAllAxisProperties("x"),
            "y":self.subplot.GetCopyAllAxisProperties("y")
            }

    def GetColorbarProperties(self):
        self.cbProperties = self.subplot.GetCopyAllColorbarProperties()

    def GetTitleProperties(self):
        self.titleProperties = self.subplot.GetCopyAllTitleProperties()

    def FillInitialUI(self):
        raise NotImplementedError

    def FillFieldData(self, fieldIndex):
        self.updatingUiData = True
        self.selectedFieldProperties = self.fieldPropertiesList[fieldIndex]
        self.FieldName.setText(self.selectedFieldProperties["name"])
        self.SpeciesName.setText(self.selectedFieldProperties["speciesName"])
        # Units
        self.fieldUnits_comboBox.clear()
        self.fieldUnits_comboBox.addItems(self.selectedFieldProperties["possibleFieldUnits"])
        index = self.fieldUnits_comboBox.findText(self.selectedFieldProperties["fieldUnits"])
        if index != -1:
            self.fieldUnits_comboBox.setCurrentIndex(index)
        # Scale
        self.auto_checkBox.setChecked(self.selectedFieldProperties["autoScale"])
        self.min_lineEdit.setText(str(self.selectedFieldProperties["minVal"]))
        self.max_lineEdit.setText(str(self.selectedFieldProperties["maxVal"]))
        # ColorMap
        self.colorMap_comboBox.clear()
        self.colorMap_comboBox.addItems(self.selectedFieldProperties["possibleColorMaps"])
        index = self.colorMap_comboBox.findText(self.selectedFieldProperties["cMap"]);
        if index != -1:
           self.colorMap_comboBox.setCurrentIndex(index)
        # Plot type
        self.plotType_comboBox.clear()
        self.plotType_comboBox.addItems(self.selectedFieldProperties["possiblePlotTypes"])
        index = self.plotType_comboBox.findText(self.selectedFieldProperties["plotType"]);
        if index != -1:
           self.plotType_comboBox.setCurrentIndex(index)
        self.updatingUiData = False

    def FillPlotSettingsData(self):
        self.updatingUiData = True
        self.axisPlotType_comboBox.clear()
        self.axisPlotType_comboBox.addItems(self.subplot.GetPossiblePlotTypes())
        index = self.axisPlotType_comboBox.findText(self.plotProperties["PlotType"]);
        if index != -1:
            self.axisPlotType_comboBox.setCurrentIndex(index)
        self.chargeWeight_checkBox.setChecked(self.plotProperties["UseChargeWeighting"])
        self.chargeUnits_comboBox.clear()
        self.chargeUnits_comboBox.addItems(self.subplot.GetWeightingUnitsOptions())
        index = self.chargeUnits_comboBox.findText(self.plotProperties["ChargeUnits"]);
        if index != -1:
            self.chargeUnits_comboBox.setCurrentIndex(index)
        self.axisColorMap_comboBox.clear()
        self.axisColorMap_comboBox.addItems(self.subplot.GetAxisColorMapOptions(self.plotProperties["PlotType"]))
        index = self.axisColorMap_comboBox.findText(self.plotProperties["CMap"]);
        if index != -1:
            self.axisColorMap_comboBox.setCurrentIndex(index)
        self.displayColorbar_checkBox.setChecked(self.plotProperties["DisplayColorbar"])
        self.updatingUiData = False

    def FillAxesData(self):
        self.updatingUiData = True
        unitOptions = self.subplot.GetAxesUnitsOptions()
        self.xUnits_comboBox.clear()
        self.xUnits_comboBox.addItems(unitOptions["x"])
        index = self.xUnits_comboBox.findText(self.axisProperties["x"]["Units"])
        if index != -1:
            self.xUnits_comboBox.setCurrentIndex(index)
        self.yUnits_comboBox.clear()
        self.yUnits_comboBox.addItems(unitOptions["y"])
        index = self.yUnits_comboBox.findText(self.axisProperties["y"]["Units"])
        if index != -1:
            self.yUnits_comboBox.setCurrentIndex(index)
        self.xAutoLabel_checkBox.setChecked(self.axisProperties["x"]["AutoLabel"])
        self.yAutoLabel_checkBox.setChecked(self.axisProperties["y"]["AutoLabel"])
        self.xAutoLabel_lineEdit.setText(self.axisProperties["x"]["LabelText"])
        self.yAutoLabel_lineEdit.setText(self.axisProperties["y"]["LabelText"])
        self.xFontSize_spinBox.setValue(self.axisProperties["x"]["LabelFontSize"])
        self.yFontSize_spinBox.setValue(self.axisProperties["y"]["LabelFontSize"])
        self.updatingUiData = False

    def FillColorbarData(self):
        self.updatingUiData = True
        self.cbAutoLabel_checkBox.setChecked(self.cbProperties["AutoTickLabelSpacing"])
        self.cbFontSize_spinBox.setValue(self.cbProperties["FontSize"])
        self.updatingUiData = False

    def FillTitleData(self):
        self.updatingUiData = True
        self.autoTitle_lineEdit.setText(self.titleProperties["Text"])
        self.autoTitle_checkBox.setChecked(self.titleProperties["AutoText"])
        self.titleFontSize_spinBox.setValue(self.titleProperties["FontSize"])
        self.updatingUiData = False

    def Fill1DSlicesData(self):
        if self.mainWindow.dataContainer.GetAvailableSpeciesNames() != []:
            self.speciesSelectorSlice_comboBox.addItems(self.mainWindow.dataContainer.GetAvailableSpeciesNames())
            self.speciesFieldSelectorSlice_comboBox.addItems(self.mainWindow.dataContainer.GetAvailableFieldsInSpecies(self.speciesSelectorSlice_comboBox.currentText()))
        self.domainFieldSelecteorSlice_comboBox.addItems(self.mainWindow.dataContainer.GetAvailableDomainFieldsNames())

    """
    UI event handlers
    """
    def FieldListView_Clicked(self,index):
        self.selectedFieldIndex = index.row()
        self.FillFieldData(self.selectedFieldIndex)

    def AutoCheckBox_StatusChanged(self):
        if self.auto_checkBox.checkState():
            self.min_lineEdit.setEnabled(False)
            self.max_lineEdit.setEnabled(False)
            if not self.updatingUiData:
                self.selectedFieldProperties["autoScale"] = True
        else:
            self.min_lineEdit.setEnabled(True)
            self.max_lineEdit.setEnabled(True)
            if not self.updatingUiData:
                self.selectedFieldProperties["autoScale"] = False

    def MinMaxLineEdit_textChanged(self):
        if not self.updatingUiData:
            vMin = float(self.min_lineEdit.text())
            vMax = float(self.max_lineEdit.text())
            self.selectedFieldProperties["minVal"] = vMin
            self.selectedFieldProperties["maxVal"] = vMax

    def SetColorMap(self):
        if not self.updatingUiData:
            cMap = str(self.colorMap_comboBox.currentText())
            self.selectedFieldProperties["cMap"] = cMap
        #cmap = self.colorMapsCollection.GetColorMap(name)
        #self.fieldToPlot.SetColorMap(cmap)

    def SetXAxisUnits(self):
        if not self.updatingUiData:
            if sys.version_info[0] < 3:
                units = unicode(self.xUnits_comboBox.currentText())
            else:
                units = self.xUnits_comboBox.currentText()
            self.axisProperties["x"]["Units"] = units
            for fieldProperties in self.fieldPropertiesList:
                fieldProperties["axesUnits"]["x"] = units

    def SetYAxisUnits(self):
        if not self.updatingUiData:
            if sys.version_info[0] < 3:
                units = unicode(self.yUnits_comboBox.currentText())
            else:
                units = self.yUnits_comboBox.currentText()
            self.axisProperties["y"]["Units"] = units
            for fieldProperties in self.fieldPropertiesList:
                fieldProperties["axesUnits"]["y"] = units

    def SetFieldUnits(self):
        if not self.updatingUiData:
            units = str(self.fieldUnits_comboBox.currentText())
            self.selectedFieldProperties["fieldUnits"] = units

    def PlotTypeComboBox_IndexChanged(self):
        if not self.updatingUiData:
            plotType = str(self.plotType_comboBox.currentText())
            self.selectedFieldProperties["plotType"] = plotType

    def RemoveFieldButton_Clicked(self):
        raise NotImplementedError

    def ApplyButton_Clicked(self):
        self.SaveChanges()
        self.mainWindow.MakePlots()

    def AcceptButton_Clicked(self):
        self.SaveChanges()
        self.close() 

    def CancelButton_Clicked(self):
        self.close()     

    def SaveChanges(self):
        self.subplot.SetAllAxisProperties("x", self.axisProperties["x"])
        self.subplot.SetAllAxisProperties("y", self.axisProperties["y"])
        self.subplot.SetAllColorbarProperties(self.cbProperties)
        self.subplot.SetAllTitleProperties(self.titleProperties)

    def XAutoLabelCheckBox_statusChanged(self):
        if self.xAutoLabel_checkBox.checkState():
            self.xAutoLabel_lineEdit.setEnabled(False)
            self.xAutoLabel_lineEdit.setText(self.axisProperties["x"]["DefaultLabelText"] )
        else:
            self.xAutoLabel_lineEdit.setEnabled(True)
        self.axisProperties["x"]["AutoLabel"] = self.xAutoLabel_checkBox.checkState()

    def YAutoLabelCheckBox_statusChanged(self):
        if self.yAutoLabel_checkBox.checkState():
            self.yAutoLabel_lineEdit.setEnabled(False)
            self.yAutoLabel_lineEdit.setText(self.axisProperties["y"]["DefaultLabelText"] )
        else:
            self.yAutoLabel_lineEdit.setEnabled(True)
        self.axisProperties["y"]["AutoLabel"] = self.yAutoLabel_checkBox.checkState()

    def CbAutoLabelCheckBox_statusChanged(self):
        if self.cbAutoLabel_checkBox.checkState():
            self.cbAutoLabel_lineEdit.setEnabled(False)
        else:
            self.cbAutoLabel_lineEdit.setEnabled(True)
        self.cbProperties["AutoTickLabelSpacing"] = self.cbAutoLabel_checkBox.checkState()

    def AutoTitleCheckBox_statusChanged(self):
        if self.autoTitle_checkBox.checkState():
            self.autoTitle_lineEdit.setEnabled(False)
            self.autoTitle_lineEdit.setText(self.titleProperties["DefaultText"])
        else:
            self.autoTitle_lineEdit.setEnabled(True) 
        self.titleProperties["AutoText"] = self.autoTitle_checkBox.checkState()

    def XAutoLabelLineEdit_textChanged(self, text):
        self.axisProperties["x"]["LabelText"] = text

    def YAutoLabelLineEdit_textChanged(self, text):
        self.axisProperties["y"]["LabelText"] = text

    def XFontSizeSpinBox_valueChanged(self, value):
        self.axisProperties["x"]["LabelFontSize"] = value

    def YFontSizeSpinBox_valueChanged(self, value):
        self.axisProperties["y"]["LabelFontSize"] = value

    def CbFontSizeSpinBox_valueChanged(self, value):
        self.cbProperties["FontSize"] = value

    def TitleFontSizeSpinBox_valueChanged(self, value):
        self.titleProperties["FontSize"] = value

    def AutoTitleLineEdit_textChanged(self, text):
        self.titleProperties["Text"] = text

    # Plot settings tab
    def AxisPlotTypeComboBox_IndexChanged(self):
        plotType = str(self.axisPlotType_comboBox.currentText())
        # set visible options
        if plotType == "Histogram":
            self.histogramSettings_widget.setVisible(True)
            self.scatterSettings_widget.setVisible(False)
            self.arrowsSettings_widget.setVisible(False)
        elif plotType == "Scatter":
            self.histogramSettings_widget.setVisible(False)
            self.scatterSettings_widget.setVisible(True)
            self.arrowsSettings_widget.setVisible(False)
        elif plotType == "Arrows":
            self.histogramSettings_widget.setVisible(False)
            self.scatterSettings_widget.setVisible(False)
            self.arrowsSettings_widget.setVisible(True)
        if not self.updatingUiData:
            # general changes
            self.plotProperties["PlotType"] = plotType
            self.axisColorMap_comboBox.clear()
            self.axisColorMap_comboBox.addItems(self.subplot.GetAxisColorMapOptions(plotType))
            self.plotProperties["CMap"] = self.subplot.GetAxisDefaultColorMap(plotType)
            index = self.axisColorMap_comboBox.findText(self.plotProperties["CMap"]);
            if index != -1:
                self.axisColorMap_comboBox.setCurrentIndex(index)

    def ChargeUnitsComboBox_IndexChanged(self):
        if not self.updatingUiData:
            units = str(self.chargeUnits_comboBox.currentText())
            self.plotProperties["ChargeUnits"] = units

    def AxisColorMapComboBox_IndexChanged(self):
        if not self.updatingUiData:
            cMap = str(self.axisColorMap_comboBox.currentText())
            self.plotProperties["CMap"] = cMap

    def ChargeWeightCheckBox_StatusChanged(self):
        state = self.chargeWeight_checkBox.checkState()
        self.chargeUnits_comboBox.setEnabled(state)
        self.plotProperties["UseChargeWeighting"] = state

    def DisplayColorbarCheckBox_StatusChanged(self):
        self.plotProperties["DisplayColorbar"] = self.displayColorbar_checkBox.checkState()

    def FieldSliceTypeRadioButton_Toggled(self):
        self.speciesSelectorSlice_comboBox.setEnabled(self.speciesFieldsSlice_radioButton.isChecked())
        self.speciesFieldSelectorSlice_comboBox.setEnabled(self.speciesFieldsSlice_radioButton.isChecked())
        self.domainFieldSelecteorSlice_comboBox.setEnabled(not self.speciesFieldsSlice_radioButton.isChecked())

    def SpeciesSelectorSliceComboBox_IndexChanged(self):
        self.speciesFieldSelectorSlice_comboBox.clear()
        self.speciesFieldSelectorSlice_comboBox.addItems(self.mainWindow.dataContainer.GetAvailableFieldsInSpecies(self.speciesSelectorSlice_comboBox.currentText()))

    def AddSliceButton_Clicked(self):
        if self.speciesFieldsSlice_radioButton.isChecked():
            speciesName = str(self.speciesSelectorSlice_comboBox.currentText())
            fieldName = str(self.speciesFieldSelectorSlice_comboBox.currentText())
            field = self.mainWindow.dataContainer.GetSpeciesField(speciesName, fieldName)
        else:
            fieldName = str(self.domainFieldSelecteorSlice_comboBox.currentText())
            field = self.mainWindow.dataContainer.GetDomainField(fieldName)
            
        fieldToPlot = FieldToPlot(field, "1D", self.mainWindow.unitConverter, self.mainWindow.colorMapsCollection, isPartOfMultiplot = False)
        self.subplot.AddFieldToPlot(fieldToPlot)
        self.fieldPropertiesList.append(fieldToPlot.GetFieldProperties())
        self.FillListView()
        self.FillFieldData(0)


class EditFieldPlotWindow(EditPlotWindow):
    def __init__(self, subplot, parent = None):
        super(EditFieldPlotWindow, self).__init__(subplot, parent)  
        self.GetFieldsInfo()
        self.FillInitialUI()

    def SetVisibleTabs(self):
        self.tabWidget.removeTab(1)

    def GetFieldsInfo(self):
        self.fieldPropertiesList = list()
        for field in self.subplot.GetDataToPlot():
            self.fieldPropertiesList.append(field.GetFieldProperties())

    def FillInitialUI(self):
        self.FillListView()
        self.FillFieldData(self.selectedFieldIndex)
        self.FillAxesData()
        self.FillColorbarData()
        self.FillTitleData()
        self.Fill1DSlicesData()

    def FillListView(self):
        model = QtGui.QStandardItemModel()
        for field in self.subplot.GetDataToPlot():
            listLabel = field.GetProperty("name")
            if field.GetProperty("speciesName") != '':
                listLabel += " / " + field.GetProperty("speciesName")
            item = QtGui.QStandardItem(listLabel)
            model.appendRow(item)
        self.field_listView.setModel(model)

    def RemoveFieldButton_Clicked(self):
        self.subplot.RemoveField(self.selectedFieldIndex)
        del self.fieldPropertiesList[self.selectedFieldIndex]
        self.FillListView()
        self.FillFieldData(0)

    def SaveChanges(self):
        i = 0
        for field in self.subplot.GetDataToPlot():
            field.SetFieldProperties(self.fieldPropertiesList[i])
            i+=1
        super(EditFieldPlotWindow, self).SaveChanges()


class EditRawPlotWindow(EditPlotWindow):
    def __init__(self, subplot, parent = None):
        super(EditRawPlotWindow, self).__init__(subplot, parent)
        self.GetPlotProperties()
        self.FillInitialUI()

    def GetPlotProperties(self):
        self.plotProperties = self.subplot.GetCopyAllPlotProperties()

    def SetVisibleTabs(self):
        self.tabWidget.removeTab(5)
        self.tabWidget.removeTab(0)

    def FillInitialUI(self):
        self.FillPlotSettingsData()
        self.FillAxesData()
        self.FillColorbarData()
        self.FillTitleData()
        self.Fill1DSlicesData()

    def SaveChanges(self):
        super(EditRawPlotWindow, self).SaveChanges()
        self.subplot.SetAllPlotProperties(self.plotProperties)


class EditPlotWindowSelector:
    editWindows = {"Field": EditFieldPlotWindow,
                   "Raw": EditRawPlotWindow
                   }
    @classmethod
    def GetEditPlotWindow(cls, subplot, mainWindow):
        return cls.editWindows[subplot.GetDataType()](subplot, mainWindow)