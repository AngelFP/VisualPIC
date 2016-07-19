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

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
#
#try:
#    _encoding = QtGui.QApplication.UnicodeUTF8
#    def _translate(context, text, disambig):
#        return QtGui.QApplication.translate(context, text, disambig, _encoding)
#except AttributeError:
#    def _translate(context, text, disambig):
#        return QtGui.QApplication.translate(context, text, disambig)

class PlotFieldWidget(QtGui.QWidget):
    def __init__(self, FieldToPlot, ColorMapsCollection, MultipleFields):
        super(PlotFieldWidget, self).__init__()
        self.fieldToPlot = FieldToPlot     
        self.colorMapsCollection = ColorMapsCollection
        self.MultipleFields = MultipleFields
        
        self.verticalLayout_5 = QtGui.QVBoxLayout(self)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.FieldName = QtGui.QLabel(self)
        self.FieldName.setObjectName(_fromUtf8("FieldName"))
        self.horizontalLayout.addWidget(self.FieldName)
        self.line = QtGui.QFrame(self)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.SpeciesName = QtGui.QLabel(self)
        self.SpeciesName.setObjectName(_fromUtf8("SpeciesName"))
        self.horizontalLayout.addWidget(self.SpeciesName)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_3 = QtGui.QLabel(self)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_3.addWidget(self.label_3)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.label_4 = QtGui.QLabel(self)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_7.addWidget(self.label_4)
        self.fieldUnits_comboBox = QtGui.QComboBox(self)
        self.fieldUnits_comboBox.setObjectName(_fromUtf8("fieldUnits_comboBox"))
        self.horizontalLayout_7.addWidget(self.fieldUnits_comboBox)
        self.label_7 = QtGui.QLabel(self)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.horizontalLayout_7.addWidget(self.label_7)
        self.axisUnits_comboBox = QtGui.QComboBox(self)
        self.axisUnits_comboBox.setObjectName(_fromUtf8("axisUnits_comboBox"))
        self.horizontalLayout_7.addWidget(self.axisUnits_comboBox)
        self.verticalLayout_3.addLayout(self.horizontalLayout_7)
        self.verticalLayout_5.addLayout(self.verticalLayout_3)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.Scale = QtGui.QLabel(self)
        self.Scale.setObjectName(_fromUtf8("Scale"))
        self.verticalLayout.addWidget(self.Scale)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.auto_checkBox = QtGui.QCheckBox(self)
        self.auto_checkBox.setChecked(True)
        self.auto_checkBox.setObjectName(_fromUtf8("auto_checkBox"))
        self.verticalLayout_2.addWidget(self.auto_checkBox)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_5 = QtGui.QLabel(self)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_3.addWidget(self.label_5)
        self.min_lineEdit = QtGui.QLineEdit(self)
        self.min_lineEdit.setEnabled(False)
        self.min_lineEdit.setObjectName(_fromUtf8("min_lineEdit"))
        self.horizontalLayout_3.addWidget(self.min_lineEdit)
        self.horizontalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_6 = QtGui.QLabel(self)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout_4.addWidget(self.label_6)
        self.max_lineEdit = QtGui.QLineEdit(self)
        self.max_lineEdit.setEnabled(False)
        self.max_lineEdit.setObjectName(_fromUtf8("max_lineEdit"))
        self.horizontalLayout_4.addWidget(self.max_lineEdit)
        self.horizontalLayout_2.addLayout(self.horizontalLayout_4)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_5.addLayout(self.verticalLayout)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.label = QtGui.QLabel(self)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_5.addWidget(self.label)
        self.plotType_comboBox = QtGui.QComboBox(self)
        self.plotType_comboBox.setObjectName(_fromUtf8("plotType_comboBox"))
        self.horizontalLayout_5.addWidget(self.plotType_comboBox)
        self.verticalLayout_5.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_6.addWidget(self.label_2)
        self.colorMap_comboBox = QtGui.QComboBox(self)
        self.colorMap_comboBox.setObjectName(_fromUtf8("colorMap_comboBox"))
        self.horizontalLayout_6.addWidget(self.colorMap_comboBox)
        self.verticalLayout_5.addLayout(self.horizontalLayout_6)
        
        self.RegisterUIEvents()
        self.setText()
        self.LoadColorMaps()
        self.LoadUnitsOptions()
        
    def RegisterUIEvents(self):
        self.auto_checkBox.toggled.connect(self.AutoCheckBox_StatusChanged)
        self.min_lineEdit.textChanged.connect(self.MinMaxLineEdit_textChanged)
        self.max_lineEdit.textChanged.connect(self.MinMaxLineEdit_textChanged)
        self.colorMap_comboBox.currentIndexChanged.connect(self.SetColorMap)
        self.axisUnits_comboBox.currentIndexChanged.connect(self.SetAxisUnits)
        self.fieldUnits_comboBox.currentIndexChanged.connect(self.SetFieldUnits)

    def AutoCheckBox_StatusChanged(self):
        if self.auto_checkBox.checkState():
            self.min_lineEdit.setEnabled(False)
            self.max_lineEdit.setEnabled(False)
            self.fieldToPlot.SetAutoScale()
        else:
            self.min_lineEdit.setEnabled(True)
            self.max_lineEdit.setEnabled(True)
            vMin = float(self.min_lineEdit.text())
            vMax = float(self.max_lineEdit.text())
            self.fieldToPlot.SetScale(vMin, vMax)
        
    def MinMaxLineEdit_textChanged(self):
        if not self.auto_checkBox.checkState():
            vMin = float(self.min_lineEdit.text())
            vMax = float(self.max_lineEdit.text())
            self.fieldToPlot.SetScale(vMin, vMax)
    
    def setText(self):
        self.FieldName.setText(self.fieldToPlot.GetName())
        self.SpeciesName.setText(self.fieldToPlot.GetSpeciesName())
        self.Scale.setText("Scale")
        self.auto_checkBox.setText("Auto")
        self.label.setText("Plot type:")
        self.label_2.setText("Colormap:")
        self.label_5.setText("Min")
        self.label_6.setText("Max")
        self.label_3.setText("Units")
        self.label_4.setText("Field")
        self.label_7.setText("Axis:")
        self.min_lineEdit.setText("0")
        self.max_lineEdit.setText("1")
        
    def SetColorMap(self):
        name = self.colorMap_comboBox.currentText()
        cmap = self.colorMapsCollection.GetColorMap(name)
        self.fieldToPlot.SetColorMap(cmap)
        
    def SetAxisUnits(self):
        units = self.axisUnits_comboBox.currentText()
        self.fieldToPlot.SetAxisUnits(units)
        
    def SetFieldUnits(self):
        units = self.fieldUnits_comboBox.currentText()
        self.fieldToPlot.SetFieldUnits(units)
        
    def GetFieldName(self):
        return self.FieldName.text()
        
    def GetSpeciesName(self):
        return self.SpeciesName.text()
        
    def GetLimits(self):
        return float(self.min_lineEdit.text()), float(self.max_lineEdit.text())
        
    def IsAutoScale(self):
        return self.auto_checkBox.isChecked()

    def LoadColorMaps(self):
        if self.MultipleFields:
            self.colorMap_comboBox.addItems(self.colorMapsCollection.GetTransparentColorMapsNames())
        else:
            self.colorMap_comboBox.addItems(self.colorMapsCollection.GetSingleColorMapsNamesList())
            
    def LoadUnitsOptions(self):
        self.axisUnits_comboBox.clear()
        self.fieldUnits_comboBox.clear()
        self.axisUnits_comboBox.addItems(self.fieldToPlot.GetPossibleAxisUnits())
        self.fieldUnits_comboBox.addItems(self.fieldToPlot.GetPossibleFieldUnits())