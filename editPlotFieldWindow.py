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

class EditPlotFieldWindow(QtGui.QDialog):
    def __init__(self, subplot):
        super(EditPlotFieldWindow, self).__init__()
        self.resize(465, 224)
        
        self.subplot = subplot
        self.selectedFieldIndex = 0
        self.updatingUiData = True
        
        self.verticalLayout_5 = QtGui.QVBoxLayout(self)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.verticalLayout_7 = QtGui.QVBoxLayout()
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.label_8 = QtGui.QLabel(self)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.verticalLayout_7.addWidget(self.label_8)
        self.field_listView = QtGui.QListView(self)
        self.field_listView.setObjectName(_fromUtf8("field_listView"))
        self.verticalLayout_7.addWidget(self.field_listView)
        self.horizontalLayout_9.addLayout(self.verticalLayout_7)
        self.verticalLayout_6 = QtGui.QVBoxLayout()
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
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
        self.verticalLayout_6.addLayout(self.horizontalLayout)
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
        self.verticalLayout_6.addLayout(self.verticalLayout_3)
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
        self.verticalLayout_6.addLayout(self.verticalLayout)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.label = QtGui.QLabel(self)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_6.addWidget(self.label)
        self.colorMap_comboBox = QtGui.QComboBox(self)
        self.colorMap_comboBox.setObjectName(_fromUtf8("colorMap_comboBox"))
        self.verticalLayout_6.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_5.addWidget(self.label_2)
        self.horizontalLayout_5.addWidget(self.colorMap_comboBox)
        self.plotType_comboBox = QtGui.QComboBox(self)
        self.plotType_comboBox.setObjectName(_fromUtf8("plotType_comboBox"))
        self.horizontalLayout_6.addWidget(self.plotType_comboBox)
        self.verticalLayout_6.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_9.addLayout(self.verticalLayout_6)
        self.verticalLayout_5.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem)
        self.accept_button = QtGui.QPushButton(self)
        self.accept_button.setObjectName(_fromUtf8("accept_button"))
        self.horizontalLayout_8.addWidget(self.accept_button)
        self.cancel_button = QtGui.QPushButton(self)
        self.cancel_button.setObjectName(_fromUtf8("cancel_button"))
        self.horizontalLayout_8.addWidget(self.cancel_button)
        self.verticalLayout_5.addLayout(self.horizontalLayout_8)

        self.RegisterUIEvents()
        self.setText()
        self.GetFieldsInfo()
        self.FillInitialUI()
        #self.LoadColorMaps()
        #self.LoadUnitsOptions()

    def RegisterUIEvents(self):
        self.field_listView.clicked.connect(self.FieldListView_Clicked)
        self.auto_checkBox.toggled.connect(self.AutoCheckBox_StatusChanged)
        self.min_lineEdit.textChanged.connect(self.MinMaxLineEdit_textChanged)
        self.max_lineEdit.textChanged.connect(self.MinMaxLineEdit_textChanged)
        self.colorMap_comboBox.currentIndexChanged.connect(self.SetColorMap)
        self.axisUnits_comboBox.currentIndexChanged.connect(self.SetAxisUnits)
        self.fieldUnits_comboBox.currentIndexChanged.connect(self.SetFieldUnits)
        self.accept_button.clicked.connect(self.AcceptButton_Clicked)
        self.cancel_button.clicked.connect(self.CancelButton_Clicked)
    
    def setText(self):
#        self.FieldName.setText(self.fieldToPlot.GetName())
#        self.SpeciesName.setText(self.fieldToPlot.GetSpeciesName())
        self.setWindowTitle("Edit plot")
        self.Scale.setText("Scale")
        self.auto_checkBox.setText("Auto")
        self.label.setText("Plot type:")
        self.label_2.setText("Colormap:")
        self.label_5.setText("Min")
        self.label_6.setText("Max")
        self.label_3.setText("Units")
        self.label_4.setText("Field")
        self.label_7.setText("Axis:")
        self.label_8.setText("Select Field:")
        self.min_lineEdit.setText("0")
        self.max_lineEdit.setText("1")
        self.accept_button.setText("Accept")
        self.cancel_button.setText("Cancel")
        
    def GetFieldsInfo(self):
        self.fieldInfoList = list()
        for field in self.subplot.GetFieldsToPlot():
            self.fieldInfoList.append(field.GetFieldInfo())
        
    def FillInitialUI(self):
        self.FillListView()
        self.FillFieldData(self.selectedFieldIndex)
        
    def FillListView(self):
        model = QtGui.QStandardItemModel()
        
        for field in self.subplot.GetFieldsToPlot():
            listLabel = field.GetName()
            if field.GetSpeciesName() != '':
                listLabel += " / " + field.GetSpeciesName()
            item = QtGui.QStandardItem(listLabel)
            model.appendRow(item)
        
        self.field_listView.setModel(model)
    
    def FillFieldData(self, fieldIndex):
        # use this boolean to determine whether UI data is being updated, 
        #so that UI events happening during the process wont have any effect 
        self.updatingUiData = True
        
        self.selectedFieldInfo = self.fieldInfoList[fieldIndex]
        self.FieldName.setText(self.selectedFieldInfo["name"])
        self.SpeciesName.setText(self.selectedFieldInfo["speciesName"])
        
        # Units
        self.fieldUnits_comboBox.clear()
        self.axisUnits_comboBox.clear()
        self.fieldUnits_comboBox.addItems(self.selectedFieldInfo["possibleFieldUnits"])
        self.axisUnits_comboBox.addItems(self.selectedFieldInfo["possibleAxisUnits"])
        index = self.fieldUnits_comboBox.findText(self.selectedFieldInfo["fieldUnits"])
        if index != -1:
           self.fieldUnits_comboBox.setCurrentIndex(index)
       
        index = self.axisUnits_comboBox.findText(self.selectedFieldInfo["axisUnits"]);
        if index != -1:
           self.axisUnits_comboBox.setCurrentIndex(index)
        
        # Scale
        self.auto_checkBox.setChecked(self.selectedFieldInfo["autoScale"])
        self.min_lineEdit.setText(str(self.selectedFieldInfo["minVal"]))
        self.max_lineEdit.setText(str(self.selectedFieldInfo["maxVal"]))
        
        # PlotType
        
        
        # ColorMap
        self.colorMap_comboBox.clear()
        self.colorMap_comboBox.addItems(self.selectedFieldInfo["possibleColorMaps"])
        index = self.colorMap_comboBox.findText(self.selectedFieldInfo["cMap"]);
        if index != -1:
           self.colorMap_comboBox.setCurrentIndex(index)
           
        self.updatingUiData = False
        
        
# UI Events        
    
    def FieldListView_Clicked(self,index):
        self.selectedFieldIndex = index.row()
        self.FillFieldData(self.selectedFieldIndex)
    
    def AutoCheckBox_StatusChanged(self):
        if self.auto_checkBox.checkState():
            self.min_lineEdit.setEnabled(False)
            self.max_lineEdit.setEnabled(False)
            if not self.updatingUiData:
                self.selectedFieldInfo["autoScale"] = True
        else:
            self.min_lineEdit.setEnabled(True)
            self.max_lineEdit.setEnabled(True)
            if not self.updatingUiData:
                self.selectedFieldInfo["autoScale"] = False
        
    def MinMaxLineEdit_textChanged(self):
        if not self.updatingUiData:
            vMin = float(self.min_lineEdit.text())
            vMax = float(self.max_lineEdit.text())
            self.selectedFieldInfo["minVal"] = vMin
            self.selectedFieldInfo["maxVal"] = vMax
    
        
    def SetColorMap(self):
        if not self.updatingUiData:
            cMap = self.colorMap_comboBox.currentText()
            self.selectedFieldInfo["cMap"] = cMap
        #cmap = self.colorMapsCollection.GetColorMap(name)
        #self.fieldToPlot.SetColorMap(cmap)
        
    def SetAxisUnits(self):
        if not self.updatingUiData:
            units = self.axisUnits_comboBox.currentText()
            self.selectedFieldInfo["axisUnits"] = units
        
    def SetFieldUnits(self):
        if not self.updatingUiData:
            units = self.fieldUnits_comboBox.currentText()
            self.selectedFieldInfo["fieldUnits"] = units
    
    def AcceptButton_Clicked(self):
        i = 0
        for field in self.subplot.GetFieldsToPlot():
            field.SetFieldInfo(self.fieldInfoList[i])
            i+=1
        self.close() 
    
    def CancelButton_Clicked(self):
        self.close()        


