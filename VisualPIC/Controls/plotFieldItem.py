# -*- coding: utf-8 -*-

#Copyright 2016-2017 Ángel Ferran Pousa
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

from PyQt5 import QtCore, QtGui, QtWidgets
from VisualPIC.Views.editPlotFieldWindow import EditPlotWindowSelector

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class PlotFieldItem(QtWidgets.QWidget):
    def __init__(self, subplot, parent=None):
        super(PlotFieldItem, self).__init__(parent)
        self.subplot = subplot
        
        self.mainWindow = parent
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.FieldName = QtWidgets.QLabel(self)
        self.FieldName.setObjectName(_fromUtf8("FieldName"))
        self.horizontalLayout.addWidget(self.FieldName)
        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.SpeciesName = QtWidgets.QLabel(self)
        self.SpeciesName.setObjectName(_fromUtf8("SpeciesName"))
        self.horizontalLayout.addWidget(self.SpeciesName)
        self.editButton = QtWidgets.QPushButton(self)
        self.editButton.setMaximumSize(QtCore.QSize(24, 16777215))
        self.editButton.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("Icons/editIcon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.editButton.setIcon(icon)
        self.editButton.setObjectName(_fromUtf8("editButton"))
        self.horizontalLayout.addWidget(self.editButton)
        self.deleteButton = QtWidgets.QPushButton(self)
        self.deleteButton.setMaximumSize(QtCore.QSize(24, 16777215))
        self.deleteButton.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8("Icons/deleteIcon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.deleteButton.setIcon(icon1)
        self.deleteButton.setObjectName(_fromUtf8("deleteButton"))
        self.horizontalLayout.addWidget(self.deleteButton)
        self.verticalLayout_5.addLayout(self.horizontalLayout)

        self.setText()
        self.registerUiEvents()

    def setText(self):
        self.FieldName.setText(self.subplot.GetName())
        self.SpeciesName.setText(self.subplot.GetPlottedSpeciesName())

    def registerUiEvents(self):
        self.editButton.clicked.connect(self.editButton_Clicked)
        self.deleteButton.clicked.connect(self.deleteButton_Clicked)
        
    def editButton_Clicked(self):
        self.EditWindow = EditPlotWindowSelector.GetEditPlotWindow(self.subplot, self.mainWindow)
        self.EditWindow.show()
        screenGeometry = QtWidgets.QApplication.desktop().screenGeometry()
        x = (screenGeometry.width()-self.EditWindow.width()) / 2;
        y = (screenGeometry.height()-self.EditWindow.height()) / 2;
        self.EditWindow.move(x, y);
        
    def deleteButton_Clicked(self):
        self.mainWindow.RemoveSubplot(self)
        