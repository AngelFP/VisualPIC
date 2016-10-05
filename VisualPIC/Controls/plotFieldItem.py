# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\ferran\Desktop\PlotFieldItem.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from VisualPIC.Views.editPlotFieldWindow import EditPlotWindowSelector

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class PlotFieldItem(QtGui.QWidget):
    def __init__(self, subplot, parent=None):
        super(PlotFieldItem, self).__init__(parent)
        self.subplot = subplot
        
        self.mainWindow = parent
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
        self.editButton = QtGui.QPushButton(self)
        self.editButton.setMaximumSize(QtCore.QSize(24, 16777215))
        self.editButton.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("Icons/editIcon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.editButton.setIcon(icon)
        self.editButton.setObjectName(_fromUtf8("editButton"))
        self.horizontalLayout.addWidget(self.editButton)
        self.deleteButton = QtGui.QPushButton(self)
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
        
    def deleteButton_Clicked(self):
        self.mainWindow.RemoveSubplot(self)
        