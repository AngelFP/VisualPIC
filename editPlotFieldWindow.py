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
from fieldToPlotClass import FieldToPlot

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class EditPlotFieldWindow(QtGui.QDialog):
    def __init__(self, subplot, parent=None):
        super(EditPlotFieldWindow, self).__init__(parent)
        self.resize(500, 312)
        
        self.mainWindow = parent
        self.subplot = subplot
        self.dataType = self.subplot.GetDataType()
        self.selectedFieldIndex = 0
        self.updatingUiData = True
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.verticalLayout_5 = QtGui.QVBoxLayout(self)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.tabWidget = QtGui.QTabWidget(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.verticalLayout_7 = QtGui.QVBoxLayout()
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.label_8 = QtGui.QLabel(self.tab)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.verticalLayout_7.addWidget(self.label_8)
        self.field_listView = QtGui.QListView(self.tab)
        self.field_listView.setObjectName(_fromUtf8("field_listView"))
        self.verticalLayout_7.addWidget(self.field_listView)
        self.horizontalLayout_9.addLayout(self.verticalLayout_7)
        self.verticalLayout_6 = QtGui.QVBoxLayout()
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.FieldName = QtGui.QLabel(self.tab)
        self.FieldName.setObjectName(_fromUtf8("FieldName"))
        self.horizontalLayout.addWidget(self.FieldName)
        self.line = QtGui.QFrame(self.tab)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.SpeciesName = QtGui.QLabel(self.tab)
        self.SpeciesName.setObjectName(_fromUtf8("SpeciesName"))
        self.horizontalLayout.addWidget(self.SpeciesName)
        self.verticalLayout_6.addLayout(self.horizontalLayout)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.label_4 = QtGui.QLabel(self.tab)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_7.addWidget(self.label_4)
        self.fieldUnits_comboBox = QtGui.QComboBox(self.tab)
        self.fieldUnits_comboBox.setObjectName(_fromUtf8("fieldUnits_comboBox"))
        self.horizontalLayout_7.addWidget(self.fieldUnits_comboBox)
        self.verticalLayout_3.addLayout(self.horizontalLayout_7)
        self.verticalLayout_6.addLayout(self.verticalLayout_3)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scale_label = QtGui.QLabel(self.tab)
        self.scale_label.setObjectName(_fromUtf8("scale_label"))
        self.verticalLayout.addWidget(self.scale_label)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.auto_checkBox = QtGui.QCheckBox(self.tab)
        self.auto_checkBox.setChecked(True)
        self.auto_checkBox.setObjectName(_fromUtf8("auto_checkBox"))
        self.verticalLayout_2.addWidget(self.auto_checkBox)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_5 = QtGui.QLabel(self.tab)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_3.addWidget(self.label_5)
        self.min_lineEdit = QtGui.QLineEdit(self.tab)
        self.min_lineEdit.setEnabled(False)
        self.min_lineEdit.setObjectName(_fromUtf8("min_lineEdit"))
        self.horizontalLayout_3.addWidget(self.min_lineEdit)
        self.horizontalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_6 = QtGui.QLabel(self.tab)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout_4.addWidget(self.label_6)
        self.max_lineEdit = QtGui.QLineEdit(self.tab)
        self.max_lineEdit.setEnabled(False)
        self.max_lineEdit.setObjectName(_fromUtf8("max_lineEdit"))
        self.horizontalLayout_4.addWidget(self.max_lineEdit)
        self.horizontalLayout_2.addLayout(self.horizontalLayout_4)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_6.addLayout(self.verticalLayout)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.color_label = QtGui.QLabel(self.tab)
        self.color_label.setObjectName(_fromUtf8("color_label"))
        self.horizontalLayout_5.addWidget(self.color_label)
        self.colorMap_comboBox = QtGui.QComboBox(self.tab)
        self.colorMap_comboBox.setObjectName(_fromUtf8("colorMap_comboBox"))
        self.horizontalLayout_5.addWidget(self.colorMap_comboBox)
        self.verticalLayout_6.addLayout(self.horizontalLayout_5)
        self.line_2 = QtGui.QFrame(self.tab)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.verticalLayout_6.addWidget(self.line_2)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.label_2 = QtGui.QLabel(self.tab)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_6.addWidget(self.label_2)
        self.plotType_comboBox = QtGui.QComboBox(self.tab)
        self.plotType_comboBox.setObjectName(_fromUtf8("plotType_comboBox"))
        self.horizontalLayout_6.addWidget(self.plotType_comboBox)
        self.verticalLayout_6.addLayout(self.horizontalLayout_6)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem)
        self.horizontalLayout_32 = QtGui.QHBoxLayout()
        self.horizontalLayout_32.setObjectName(_fromUtf8("horizontalLayout_32"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_32.addItem(spacerItem1)
        self.removeField_button = QtGui.QPushButton(self.tab)
        self.removeField_button.setObjectName(_fromUtf8("removeField_button"))
        self.horizontalLayout_32.addWidget(self.removeField_button)
        self.verticalLayout_6.addLayout(self.horizontalLayout_32)
        self.horizontalLayout_9.addLayout(self.verticalLayout_6)
        self.verticalLayout_4.addLayout(self.horizontalLayout_9)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.axisPlot_tab = QtGui.QWidget()
        self.axisPlot_tab.setObjectName(_fromUtf8("axisPlot_tab"))
        self.verticalLayout_14 = QtGui.QVBoxLayout(self.axisPlot_tab)
        self.verticalLayout_14.setObjectName(_fromUtf8("verticalLayout_14"))
        self.verticalLayout_17 = QtGui.QVBoxLayout()
        self.verticalLayout_17.setObjectName(_fromUtf8("verticalLayout_17"))
        self.horizontalLayout_22 = QtGui.QHBoxLayout()
        self.horizontalLayout_22.setObjectName(_fromUtf8("horizontalLayout_22"))
        self.label_3 = QtGui.QLabel(self.axisPlot_tab)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_22.addWidget(self.label_3)
        self.axisPlotType_comboBox = QtGui.QComboBox(self.axisPlot_tab)
        self.axisPlotType_comboBox.setObjectName(_fromUtf8("axisPlotType_comboBox"))
        self.horizontalLayout_22.addWidget(self.axisPlotType_comboBox)
        self.verticalLayout_17.addLayout(self.horizontalLayout_22)
        self.histogramSettings_widget = QtGui.QWidget(self.axisPlot_tab)
        self.histogramSettings_widget.setObjectName(_fromUtf8("histogramSettings_widget"))
        self.horizontalLayout_28 = QtGui.QHBoxLayout(self.histogramSettings_widget)
        self.horizontalLayout_28.setObjectName(_fromUtf8("horizontalLayout_28"))
        self.horizontalLayout_27 = QtGui.QHBoxLayout()
        self.horizontalLayout_27.setObjectName(_fromUtf8("horizontalLayout_27"))
        self.label_29 = QtGui.QLabel(self.histogramSettings_widget)
        self.label_29.setObjectName(_fromUtf8("label_29"))
        self.horizontalLayout_27.addWidget(self.label_29)
        self.label_31 = QtGui.QLabel(self.histogramSettings_widget)
        self.label_31.setObjectName(_fromUtf8("label_31"))
        self.horizontalLayout_27.addWidget(self.label_31)
        self.xBins_spinBox = QtGui.QSpinBox(self.histogramSettings_widget)
        self.xBins_spinBox.setMinimumSize(QtCore.QSize(60, 0))
        self.xBins_spinBox.setWrapping(False)
        self.xBins_spinBox.setFrame(True)
        self.xBins_spinBox.setSuffix(_fromUtf8(""))
        self.xBins_spinBox.setObjectName(_fromUtf8("xBins_spinBox"))
        self.horizontalLayout_27.addWidget(self.xBins_spinBox)
        self.label_30 = QtGui.QLabel(self.histogramSettings_widget)
        self.label_30.setObjectName(_fromUtf8("label_30"))
        self.horizontalLayout_27.addWidget(self.label_30)
        self.yBins_spinBox = QtGui.QSpinBox(self.histogramSettings_widget)
        self.yBins_spinBox.setMinimumSize(QtCore.QSize(60, 0))
        self.yBins_spinBox.setObjectName(_fromUtf8("yBins_spinBox"))
        self.horizontalLayout_27.addWidget(self.yBins_spinBox)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_27.addItem(spacerItem2)
        self.horizontalLayout_28.addLayout(self.horizontalLayout_27)
        self.verticalLayout_17.addWidget(self.histogramSettings_widget)
        self.verticalLayout_14.addLayout(self.verticalLayout_17)
        self.verticalLayout_15 = QtGui.QVBoxLayout()
        self.verticalLayout_15.setObjectName(_fromUtf8("verticalLayout_15"))
        self.label_26 = QtGui.QLabel(self.axisPlot_tab)
        self.label_26.setObjectName(_fromUtf8("label_26"))
        self.verticalLayout_15.addWidget(self.label_26)
        self.horizontalLayout_24 = QtGui.QHBoxLayout()
        self.horizontalLayout_24.setObjectName(_fromUtf8("horizontalLayout_24"))
        self.chargeWeight_checkBox = QtGui.QCheckBox(self.axisPlot_tab)
        self.chargeWeight_checkBox.setChecked(True)
        self.chargeWeight_checkBox.setObjectName(_fromUtf8("chargeWeight_checkBox"))
        self.horizontalLayout_24.addWidget(self.chargeWeight_checkBox)
        self.verticalLayout_15.addLayout(self.horizontalLayout_24)
        self.horizontalLayout_25 = QtGui.QHBoxLayout()
        self.horizontalLayout_25.setObjectName(_fromUtf8("horizontalLayout_25"))
        self.label_27 = QtGui.QLabel(self.axisPlot_tab)
        self.label_27.setObjectName(_fromUtf8("label_27"))
        self.horizontalLayout_25.addWidget(self.label_27)
        self.chargeUnits_comboBox = QtGui.QComboBox(self.axisPlot_tab)
        self.chargeUnits_comboBox.setObjectName(_fromUtf8("chargeUnits_comboBox"))
        self.horizontalLayout_25.addWidget(self.chargeUnits_comboBox)
        self.verticalLayout_15.addLayout(self.horizontalLayout_25)
        self.verticalLayout_14.addLayout(self.verticalLayout_15)
        self.verticalLayout_16 = QtGui.QVBoxLayout()
        self.verticalLayout_16.setObjectName(_fromUtf8("verticalLayout_16"))
        self.label_28 = QtGui.QLabel(self.axisPlot_tab)
        self.label_28.setObjectName(_fromUtf8("label_28"))
        self.verticalLayout_16.addWidget(self.label_28)
        self.horizontalLayout_23 = QtGui.QHBoxLayout()
        self.horizontalLayout_23.setObjectName(_fromUtf8("horizontalLayout_23"))
        self.label_7 = QtGui.QLabel(self.axisPlot_tab)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.horizontalLayout_23.addWidget(self.label_7)
        self.axisColorMap_comboBox = QtGui.QComboBox(self.axisPlot_tab)
        self.axisColorMap_comboBox.setObjectName(_fromUtf8("axisColorMap_comboBox"))
        self.horizontalLayout_23.addWidget(self.axisColorMap_comboBox)
        self.verticalLayout_16.addLayout(self.horizontalLayout_23)
        self.horizontalLayout_26 = QtGui.QHBoxLayout()
        self.horizontalLayout_26.setObjectName(_fromUtf8("horizontalLayout_26"))
        self.displayColorbar_checkBox = QtGui.QCheckBox(self.axisPlot_tab)
        self.displayColorbar_checkBox.setChecked(True)
        self.displayColorbar_checkBox.setObjectName(_fromUtf8("displayColorbar_checkBox"))
        self.horizontalLayout_26.addWidget(self.displayColorbar_checkBox)
        self.verticalLayout_16.addLayout(self.horizontalLayout_26)
        self.verticalLayout_14.addLayout(self.verticalLayout_16)
        self.tabWidget.addTab(self.axisPlot_tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_9.setObjectName(_fromUtf8("verticalLayout_9"))
        self.tabWidget_2 = QtGui.QTabWidget(self.tab_2)
        self.tabWidget_2.setTabPosition(QtGui.QTabWidget.West)
        self.tabWidget_2.setObjectName(_fromUtf8("tabWidget_2"))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.tab_3)
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.label_15 = QtGui.QLabel(self.tab_3)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.verticalLayout_8.addWidget(self.label_15)
        self.horizontalLayout_10 = QtGui.QHBoxLayout()
        self.horizontalLayout_10.setObjectName(_fromUtf8("horizontalLayout_10"))
        self.label_9 = QtGui.QLabel(self.tab_3)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.horizontalLayout_10.addWidget(self.label_9)
        self.xAutoLabel_checkBox = QtGui.QCheckBox(self.tab_3)
        self.xAutoLabel_checkBox.setChecked(True)
        self.xAutoLabel_checkBox.setObjectName(_fromUtf8("xAutoLabel_checkBox"))
        self.horizontalLayout_10.addWidget(self.xAutoLabel_checkBox)
        self.xAutoLabel_lineEdit = QtGui.QLineEdit(self.tab_3)
        self.xAutoLabel_lineEdit.setEnabled(False)
        self.xAutoLabel_lineEdit.setObjectName(_fromUtf8("xAutoLabel_lineEdit"))
        self.horizontalLayout_10.addWidget(self.xAutoLabel_lineEdit)
        self.verticalLayout_8.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_15 = QtGui.QHBoxLayout()
        self.horizontalLayout_15.setObjectName(_fromUtf8("horizontalLayout_15"))
        self.label_16 = QtGui.QLabel(self.tab_3)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.horizontalLayout_15.addWidget(self.label_16)
        self.xFontSize_spinBox = QtGui.QSpinBox(self.tab_3)
        self.xFontSize_spinBox.setMinimum(1)
        self.xFontSize_spinBox.setProperty("value", 20)
        self.xFontSize_spinBox.setObjectName(_fromUtf8("xFontSize_spinBox"))
        self.horizontalLayout_15.addWidget(self.xFontSize_spinBox)
        self.verticalLayout_8.addLayout(self.horizontalLayout_15)
        self.label_17 = QtGui.QLabel(self.tab_3)
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.verticalLayout_8.addWidget(self.label_17)
        self.horizontalLayout_19 = QtGui.QHBoxLayout()
        self.horizontalLayout_19.setObjectName(_fromUtf8("horizontalLayout_19"))
        self.label_23 = QtGui.QLabel(self.tab_3)
        self.label_23.setObjectName(_fromUtf8("label_23"))
        self.horizontalLayout_19.addWidget(self.label_23)
        self.xUnits_comboBox = QtGui.QComboBox(self.tab_3)
        self.xUnits_comboBox.setObjectName(_fromUtf8("xUnits_comboBox"))
        self.horizontalLayout_19.addWidget(self.xUnits_comboBox)
        self.verticalLayout_8.addLayout(self.horizontalLayout_19)
        self.horizontalLayout_11 = QtGui.QHBoxLayout()
        self.horizontalLayout_11.setObjectName(_fromUtf8("horizontalLayout_11"))
        self.label_10 = QtGui.QLabel(self.tab_3)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.horizontalLayout_11.addWidget(self.label_10)
        self.xScale_comboBox = QtGui.QComboBox(self.tab_3)
        self.xScale_comboBox.setObjectName(_fromUtf8("xScale_comboBox"))
        self.horizontalLayout_11.addWidget(self.xScale_comboBox)
        self.verticalLayout_8.addLayout(self.horizontalLayout_11)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_8.addItem(spacerItem3)
        self.tabWidget_2.addTab(self.tab_3, _fromUtf8(""))
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName(_fromUtf8("tab_4"))
        self.verticalLayout_11 = QtGui.QVBoxLayout(self.tab_4)
        self.verticalLayout_11.setObjectName(_fromUtf8("verticalLayout_11"))
        self.label_20 = QtGui.QLabel(self.tab_4)
        self.label_20.setObjectName(_fromUtf8("label_20"))
        self.verticalLayout_11.addWidget(self.label_20)
        self.horizontalLayout_13 = QtGui.QHBoxLayout()
        self.horizontalLayout_13.setObjectName(_fromUtf8("horizontalLayout_13"))
        self.label_12 = QtGui.QLabel(self.tab_4)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.horizontalLayout_13.addWidget(self.label_12)
        self.yAutoLabel_checkBox = QtGui.QCheckBox(self.tab_4)
        self.yAutoLabel_checkBox.setChecked(True)
        self.yAutoLabel_checkBox.setObjectName(_fromUtf8("yAutoLabel_checkBox"))
        self.horizontalLayout_13.addWidget(self.yAutoLabel_checkBox)
        self.yAutoLabel_lineEdit = QtGui.QLineEdit(self.tab_4)
        self.yAutoLabel_lineEdit.setEnabled(False)
        self.yAutoLabel_lineEdit.setObjectName(_fromUtf8("yAutoLabel_lineEdit"))
        self.horizontalLayout_13.addWidget(self.yAutoLabel_lineEdit)
        self.verticalLayout_11.addLayout(self.horizontalLayout_13)
        self.horizontalLayout_16 = QtGui.QHBoxLayout()
        self.horizontalLayout_16.setObjectName(_fromUtf8("horizontalLayout_16"))
        self.label_18 = QtGui.QLabel(self.tab_4)
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.horizontalLayout_16.addWidget(self.label_18)
        self.yFontSize_spinBox = QtGui.QSpinBox(self.tab_4)
        self.yFontSize_spinBox.setMinimum(1)
        self.yFontSize_spinBox.setProperty("value", 20)
        self.yFontSize_spinBox.setObjectName(_fromUtf8("yFontSize_spinBox"))
        self.horizontalLayout_16.addWidget(self.yFontSize_spinBox)
        self.verticalLayout_11.addLayout(self.horizontalLayout_16)
        self.label_19 = QtGui.QLabel(self.tab_4)
        self.label_19.setObjectName(_fromUtf8("label_19"))
        self.verticalLayout_11.addWidget(self.label_19)
        self.horizontalLayout_20 = QtGui.QHBoxLayout()
        self.horizontalLayout_20.setObjectName(_fromUtf8("horizontalLayout_20"))
        self.label_24 = QtGui.QLabel(self.tab_4)
        self.label_24.setObjectName(_fromUtf8("label_24"))
        self.horizontalLayout_20.addWidget(self.label_24)
        self.yUnits_comboBox = QtGui.QComboBox(self.tab_4)
        self.yUnits_comboBox.setObjectName(_fromUtf8("yUnits_comboBox"))
        self.horizontalLayout_20.addWidget(self.yUnits_comboBox)
        self.verticalLayout_11.addLayout(self.horizontalLayout_20)
        self.horizontalLayout_14 = QtGui.QHBoxLayout()
        self.horizontalLayout_14.setObjectName(_fromUtf8("horizontalLayout_14"))
        self.label_13 = QtGui.QLabel(self.tab_4)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.horizontalLayout_14.addWidget(self.label_13)
        self.yScale_comboBox = QtGui.QComboBox(self.tab_4)
        self.yScale_comboBox.setObjectName(_fromUtf8("yScale_comboBox"))
        self.horizontalLayout_14.addWidget(self.yScale_comboBox)
        self.verticalLayout_11.addLayout(self.horizontalLayout_14)
        spacerItem4 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_11.addItem(spacerItem4)
        self.tabWidget_2.addTab(self.tab_4, _fromUtf8(""))
        self.tab_7 = QtGui.QWidget()
        self.tab_7.setObjectName(_fromUtf8("tab_7"))
        self.verticalLayout_13 = QtGui.QVBoxLayout(self.tab_7)
        self.verticalLayout_13.setObjectName(_fromUtf8("verticalLayout_13"))
        self.horizontalLayout_12 = QtGui.QHBoxLayout()
        self.horizontalLayout_12.setObjectName(_fromUtf8("horizontalLayout_12"))
        self.label_11 = QtGui.QLabel(self.tab_7)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.horizontalLayout_12.addWidget(self.label_11)
        self.autoTitle_checkBox = QtGui.QCheckBox(self.tab_7)
        self.autoTitle_checkBox.setChecked(True)
        self.autoTitle_checkBox.setObjectName(_fromUtf8("autoTitle_checkBox"))
        self.horizontalLayout_12.addWidget(self.autoTitle_checkBox)
        self.autoTitle_lineEdit = QtGui.QLineEdit(self.tab_7)
        self.autoTitle_lineEdit.setEnabled(False)
        self.autoTitle_lineEdit.setObjectName(_fromUtf8("autoTitle_lineEdit"))
        self.horizontalLayout_12.addWidget(self.autoTitle_lineEdit)
        self.verticalLayout_13.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_21 = QtGui.QHBoxLayout()
        self.horizontalLayout_21.setObjectName(_fromUtf8("horizontalLayout_21"))
        self.label_25 = QtGui.QLabel(self.tab_7)
        self.label_25.setObjectName(_fromUtf8("label_25"))
        self.horizontalLayout_21.addWidget(self.label_25)
        self.titleFontSize_spinBox = QtGui.QSpinBox(self.tab_7)
        self.titleFontSize_spinBox.setMinimum(1)
        self.titleFontSize_spinBox.setProperty("value", 20)
        self.titleFontSize_spinBox.setObjectName(_fromUtf8("titleFontSize_spinBox"))
        self.horizontalLayout_21.addWidget(self.titleFontSize_spinBox)
        self.verticalLayout_13.addLayout(self.horizontalLayout_21)
        spacerItem5 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_13.addItem(spacerItem5)
        self.tabWidget_2.addTab(self.tab_7, _fromUtf8(""))
        self.verticalLayout_9.addWidget(self.tabWidget_2)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_6 = QtGui.QWidget()
        self.tab_6.setObjectName(_fromUtf8("tab_6"))
        self.verticalLayout_12 = QtGui.QVBoxLayout(self.tab_6)
        self.verticalLayout_12.setObjectName(_fromUtf8("verticalLayout_12"))
        self.horizontalLayout_17 = QtGui.QHBoxLayout()
        self.horizontalLayout_17.setObjectName(_fromUtf8("horizontalLayout_17"))
        self.label_21 = QtGui.QLabel(self.tab_6)
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.horizontalLayout_17.addWidget(self.label_21)
        self.cbFontSize_spinBox = QtGui.QSpinBox(self.tab_6)
        self.cbFontSize_spinBox.setMinimum(1)
        self.cbFontSize_spinBox.setProperty("value", 20)
        self.cbFontSize_spinBox.setObjectName(_fromUtf8("cbFontSize_spinBox"))
        self.horizontalLayout_17.addWidget(self.cbFontSize_spinBox)
        self.verticalLayout_12.addLayout(self.horizontalLayout_17)
        self.horizontalLayout_18 = QtGui.QHBoxLayout()
        self.horizontalLayout_18.setObjectName(_fromUtf8("horizontalLayout_18"))
        self.label_22 = QtGui.QLabel(self.tab_6)
        self.label_22.setObjectName(_fromUtf8("label_22"))
        self.horizontalLayout_18.addWidget(self.label_22)
        self.cbAutoLabel_checkBox = QtGui.QCheckBox(self.tab_6)
        self.cbAutoLabel_checkBox.setChecked(True)
        self.cbAutoLabel_checkBox.setObjectName(_fromUtf8("cbAutoLabel_checkBox"))
        self.horizontalLayout_18.addWidget(self.cbAutoLabel_checkBox)
        self.cbAutoLabel_lineEdit = QtGui.QLineEdit(self.tab_6)
        self.cbAutoLabel_lineEdit.setEnabled(False)
        self.cbAutoLabel_lineEdit.setObjectName(_fromUtf8("cbAutoLabel_lineEdit"))
        self.horizontalLayout_18.addWidget(self.cbAutoLabel_lineEdit)
        self.verticalLayout_12.addLayout(self.horizontalLayout_18)
        spacerItem6 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_12.addItem(spacerItem6)
        self.tabWidget.addTab(self.tab_6, _fromUtf8(""))
        self.tab_5 = QtGui.QWidget()
        self.tab_5.setObjectName(_fromUtf8("tab_5"))
        self.verticalLayout_10 = QtGui.QVBoxLayout(self.tab_5)
        self.verticalLayout_10.setObjectName(_fromUtf8("verticalLayout_10"))
        self.label_14 = QtGui.QLabel(self.tab_5)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.verticalLayout_10.addWidget(self.label_14)
        self.overlaytext_listView = QtGui.QListView(self.tab_5)
        self.overlaytext_listView.setObjectName(_fromUtf8("overlaytext_listView"))
        self.verticalLayout_10.addWidget(self.overlaytext_listView)
        self.tabWidget.addTab(self.tab_5, _fromUtf8(""))
        self.tab_8 = QtGui.QWidget()
        self.tab_8.setObjectName(_fromUtf8("tab_8"))
        self.verticalLayout_18 = QtGui.QVBoxLayout(self.tab_8)
        self.verticalLayout_18.setObjectName(_fromUtf8("verticalLayout_18"))
        self.label_32 = QtGui.QLabel(self.tab_8)
        self.label_32.setObjectName(_fromUtf8("label_32"))
        self.verticalLayout_18.addWidget(self.label_32)
        self.speciesFieldsSlice_radioButton = QtGui.QRadioButton(self.tab_8)
        self.speciesFieldsSlice_radioButton.setChecked(True)
        self.speciesFieldsSlice_radioButton.setObjectName(_fromUtf8("speciesFieldsSlice_radioButton"))
        self.verticalLayout_18.addWidget(self.speciesFieldsSlice_radioButton)
        self.horizontalLayout_29 = QtGui.QHBoxLayout()
        self.horizontalLayout_29.setObjectName(_fromUtf8("horizontalLayout_29"))
        self.label_33 = QtGui.QLabel(self.tab_8)
        self.label_33.setObjectName(_fromUtf8("label_33"))
        self.horizontalLayout_29.addWidget(self.label_33)
        self.speciesSelectorSlice_comboBox = QtGui.QComboBox(self.tab_8)
        self.speciesSelectorSlice_comboBox.setObjectName(_fromUtf8("speciesSelectorSlice_comboBox"))
        self.horizontalLayout_29.addWidget(self.speciesSelectorSlice_comboBox)
        self.label_34 = QtGui.QLabel(self.tab_8)
        self.label_34.setObjectName(_fromUtf8("label_34"))
        self.horizontalLayout_29.addWidget(self.label_34)
        self.speciesFieldSelectorSlice_comboBox = QtGui.QComboBox(self.tab_8)
        self.speciesFieldSelectorSlice_comboBox.setObjectName(_fromUtf8("speciesFieldSelectorSlice_comboBox"))
        self.horizontalLayout_29.addWidget(self.speciesFieldSelectorSlice_comboBox)
        self.verticalLayout_18.addLayout(self.horizontalLayout_29)
        self.domainFieldsSlice_radioButton = QtGui.QRadioButton(self.tab_8)
        self.domainFieldsSlice_radioButton.setObjectName(_fromUtf8("domainFieldsSlice_radioButton"))
        self.verticalLayout_18.addWidget(self.domainFieldsSlice_radioButton)
        self.horizontalLayout_30 = QtGui.QHBoxLayout()
        self.horizontalLayout_30.setObjectName(_fromUtf8("horizontalLayout_30"))
        self.label_35 = QtGui.QLabel(self.tab_8)
        self.label_35.setObjectName(_fromUtf8("label_35"))
        self.horizontalLayout_30.addWidget(self.label_35)
        self.domainFieldSelecteorSlice_comboBox = QtGui.QComboBox(self.tab_8)
        self.domainFieldSelecteorSlice_comboBox.setEnabled(False)
        self.domainFieldSelecteorSlice_comboBox.setObjectName(_fromUtf8("domainFieldSelecteorSlice_comboBox"))
        self.horizontalLayout_30.addWidget(self.domainFieldSelecteorSlice_comboBox)
        self.verticalLayout_18.addLayout(self.horizontalLayout_30)
        spacerItem7 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_18.addItem(spacerItem7)
        self.horizontalLayout_31 = QtGui.QHBoxLayout()
        self.horizontalLayout_31.setObjectName(_fromUtf8("horizontalLayout_31"))
        spacerItem8 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_31.addItem(spacerItem8)
        self.addSlice_button = QtGui.QPushButton(self.tab_8)
        self.addSlice_button.setObjectName(_fromUtf8("addSlice_button"))
        self.horizontalLayout_31.addWidget(self.addSlice_button)
        self.verticalLayout_18.addLayout(self.horizontalLayout_31)
        self.tabWidget.addTab(self.tab_8, _fromUtf8(""))
        self.verticalLayout_5.addWidget(self.tabWidget)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        spacerItem9 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem9)
        self.apply_button = QtGui.QPushButton(self)
        self.apply_button.setObjectName(_fromUtf8("apply_button"))
        self.horizontalLayout_8.addWidget(self.apply_button)
        self.accept_button = QtGui.QPushButton(self)
        self.accept_button.setObjectName(_fromUtf8("accept_button"))
        self.horizontalLayout_8.addWidget(self.accept_button)
        self.cancel_button = QtGui.QPushButton(self)
        self.cancel_button.setObjectName(_fromUtf8("cancel_button"))
        self.horizontalLayout_8.addWidget(self.cancel_button)
        self.verticalLayout_5.addLayout(self.horizontalLayout_8)

        self.SetText()
        self.RegisterUIEvents()
        self.SetVisibleTabs()
        self.GetFieldsInfo()
        self.GetAxisProperties()
        self.GetColorbarProperties()
        self.GetPlotProperties()
        self.GetTitleProperties()
        self.FillInitialUI()
        #self.LoadColorMaps()
        #self.LoadUnitsOptions()
        
    def SetText(self):
#        self.FieldName.setText(self.fieldToPlot.GetName())
#        self.SpeciesName.setText(self.fieldToPlot.GetSpeciesName())
        self.setWindowTitle("Edit plot")
        self.label_8.setText("Select Field:")
        self.FieldName.setText("Field")
        self.SpeciesName.setText("Species")
        self.label_4.setText("Units:")
        self.scale_label.setText("Scale")
        self.auto_checkBox.setText("Auto")
        self.label_5.setText("Min")
        self.min_lineEdit.setText("0")
        self.label_6.setText("Max")
        self.max_lineEdit.setText("1")
        self.color_label.setText("Colormap:")
        self.label_2.setText("Plot type:")
        self.removeField_button.setText("Remove Field from Subplot")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), "Fields")
        self.label_3.setText("Plot type:")
        self.label_29.setText("Number of bins:")
        self.label_31.setText("x:")
        self.label_30.setText("y:")
        self.label_26.setText("Options:")
        self.chargeWeight_checkBox.setText("Use macroparticle charge as weighting parameter (recommended)")
        self.label_27.setText("Charge units:")
        self.label_28.setText("Color:")
        self.label_7.setText("Colormap:")
        self.displayColorbar_checkBox.setText("Display colorbar")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.axisPlot_tab), "Plot settings")
        self.label_15.setText("Label:")
        self.label_9.setText("Text")
        self.xAutoLabel_checkBox.setText("Auto")
        self.label_16.setText("Fontsize:")
        self.label_17.setText("Properties:")
        self.label_23.setText("Units")
        self.label_10.setText("Scale:")
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_3), "X axis")
        self.label_20.setText("Label:")
        self.label_12.setText("Text")
        self.yAutoLabel_checkBox.setText("Auto")
        self.label_18.setText("Fontsize:")
        self.label_19.setText("Properties:")
        self.label_24.setText("Units")
        self.label_13.setText("Scale:")
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_4), "Y axis")
        self.label_11.setText("Text:")
        self.autoTitle_checkBox.setText("Auto")
        self.label_25.setText("Fontsize:")
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_7), "Title")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), "Axes")
        self.label_21.setText("Fontsize:")
        self.label_22.setText("Tick label spacing:")
        self.cbAutoLabel_checkBox.setText("Auto")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), "Colorbars")
        self.label_14.setText("Overlay the following lines:")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), "Text")
        self.label_32.setText("Add 1D field slices to current subplot")
        self.speciesFieldsSlice_radioButton.setText("Species Fields")
        self.label_33.setText("Select species")
        self.label_34.setText("Select field")
        self.domainFieldsSlice_radioButton.setText("Domain Fields")
        self.label_35.setText("Select field")
        self.addSlice_button.setText("Add to Subplot")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_8), "1D Slices")
        self.apply_button.setText("Apply")
        self.accept_button.setText("Accept")
        self.cancel_button.setText("Cancel")

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
        
        if self.dataType == "Field":
            self.tabWidget.removeTab(1)
        elif self.dataType == "Axis":
            self.tabWidget.removeTab(0)
        
    def GetFieldsInfo(self):
        self.fieldInfoList = list()
        for field in self.subplot.GetFieldsToPlot():
            self.fieldInfoList.append(field.GetFieldInfo())
    
    def GetAxisProperties(self):
        self.axisProperties = {
            "x":self.subplot.GetCopyAllAxisProperties("x"),
            "y":self.subplot.GetCopyAllAxisProperties("y")
            }
            
    def GetColorbarProperties(self):
        self.cbProperties = self.subplot.GetCopyAllColorbarProperties()
        
    def GetTitleProperties(self):
        self.titleProperties = self.subplot.GetCopyAllTitleProperties()
        
    def GetPlotProperties(self):
        self.plotProperties = self.subplot.GetCopyAllPlotProperties()
        
    def FillInitialUI(self):
                # use this boolean to determine whether UI data is being updated, 
        #so that UI events happening during the process wont have any effect 
        
        self.FillListView()
        if self.dataType == "Field":
            self.FillFieldData(self.selectedFieldIndex)
        elif self.dataType == "Axis":
            self.FillPlotSettingsData()
        self.FillAxesData()
        self.FillColorbarData()
        self.FillTitleData()
        self.Fill1DSlicesData()
        
        
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

        self.updatingUiData = True
        self.selectedFieldInfo = self.fieldInfoList[fieldIndex]
        self.FieldName.setText(self.selectedFieldInfo["name"])
        self.SpeciesName.setText(self.selectedFieldInfo["speciesName"])
        
        # Units
        self.fieldUnits_comboBox.clear()
        
        self.fieldUnits_comboBox.addItems(self.selectedFieldInfo["possibleFieldUnits"])
        
        index = self.fieldUnits_comboBox.findText(self.selectedFieldInfo["fieldUnits"])
        if index != -1:
            self.fieldUnits_comboBox.setCurrentIndex(index)
       
       
        
        
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
           
           
        # Plot type
        self.plotType_comboBox.clear()
        self.plotType_comboBox.addItems(self.selectedFieldInfo["possiblePlotTypes"])
        index = self.plotType_comboBox.findText(self.selectedFieldInfo["plotType"]);
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
        self.speciesSelectorSlice_comboBox.addItems(self.mainWindow.availableData.GetAvailableSpeciesNames())
        self.speciesFieldSelectorSlice_comboBox.addItems(self.mainWindow.availableData.GetAvailableFieldsInSpecies(self.speciesSelectorSlice_comboBox.currentText()))
        self.domainFieldSelecteorSlice_comboBox.addItems(self.mainWindow.availableData.GetAvailableDomainFieldsNames())
        
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
        
    def SetXAxisUnits(self):
        if not self.updatingUiData:
            units = self.xUnits_comboBox.currentText()
            self.axisProperties["x"]["Units"] = units
    
    def SetYAxisUnits(self):
        if not self.updatingUiData:
            units = self.yUnits_comboBox.currentText()
            self.axisProperties["y"]["Units"] = units
            
    def SetFieldUnits(self):
        if not self.updatingUiData:
            units = self.fieldUnits_comboBox.currentText()
            self.selectedFieldInfo["fieldUnits"] = units
            
    def PlotTypeComboBox_IndexChanged(self):
        if not self.updatingUiData:
            plotType = self.plotType_comboBox.currentText()
            self.selectedFieldInfo["plotType"] = plotType
    
    def RemoveFieldButton_Clicked(self):
        self.subplot.RemoveField(self.selectedFieldIndex)
        del self.fieldInfoList[self.selectedFieldIndex]
        self.FillListView()
        self.FillFieldData(0)
        
        
    def ApplyButton_Clicked(self):
        self.SaveChanges()
        self.mainWindow.PlotFields()
        
    def AcceptButton_Clicked(self):
        self.SaveChanges()
        self.close() 
    
    def CancelButton_Clicked(self):
        self.close()     
        
    def SaveChanges(self):
        i = 0
        for field in self.subplot.GetFieldsToPlot():
            field.SetFieldInfo(self.fieldInfoList[i])
            i+=1
            
        self.subplot.SetAllAxisProperties("x", self.axisProperties["x"])
        self.subplot.SetAllAxisProperties("y", self.axisProperties["y"])
        self.subplot.SetAllColorbarProperties(self.cbProperties)
        self.subplot.SetAllTitleProperties(self.titleProperties)
        self.subplot.SetAllPlotProperties(self.plotProperties)

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
        if not self.updatingUiData:
            plotType = self.axisPlotType_comboBox.currentText()
            self.plotProperties["PlotType"] = plotType
            self.axisColorMap_comboBox.clear()
            self.axisColorMap_comboBox.addItems(self.subplot.GetAxisColorMapOptions(plotType))
            self.plotProperties["CMap"] = self.subplot.GetAxisDefaultColorMap(plotType)
            index = self.axisColorMap_comboBox.findText(self.plotProperties["CMap"]);
            if index != -1:
                self.axisColorMap_comboBox.setCurrentIndex(index)
    
    def ChargeUnitsComboBox_IndexChanged(self):
        if not self.updatingUiData:
            units = self.chargeUnits_comboBox.currentText()
            self.plotProperties["ChargeUnits"] = units
            
    def AxisColorMapComboBox_IndexChanged(self):
        if not self.updatingUiData:
            cMap = self.axisColorMap_comboBox.currentText()
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
        self.speciesFieldSelectorSlice_comboBox.addItems(self.mainWindow.availableData.GetAvailableFieldsInSpecies(self.speciesSelectorSlice_comboBox.currentText()))
        
    def AddSliceButton_Clicked(self):
        if self.speciesFieldsSlice_radioButton.isChecked():
            speciesName = self.speciesSelectorSlice_comboBox.currentText()
            fieldName = self.speciesFieldSelectorSlice_comboBox.currentText()
            field = self.mainWindow.availableData.GetSpeciesField(speciesName, fieldName)
        else:
            fieldName = self.domainFieldSelecteorSlice_comboBox.currentText()
            field = self.mainWindow.availableData.GetDomainField(fieldName)
            
        fieldToPlot = FieldToPlot(field, "1D", self.mainWindow.unitConverter, self.mainWindow.colorMapsCollection, isPartOfMultiplot = False)
        self.subplot.AddFieldToPlot(fieldToPlot)
        self.fieldInfoList.append(fieldToPlot.GetFieldInfo())
        self.FillListView()
        self.FillFieldData(0)
        