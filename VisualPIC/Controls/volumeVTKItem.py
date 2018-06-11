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

from pkg_resources import resource_filename

from PyQt5 import QtCore, QtGui, QtWidgets

from VisualPIC.Views.editVolumeVTKWindow import EditVolumeVTKWindow


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class VolumeVTKItem(QtWidgets.QWidget):
    def __init__(self, volume, parent=None):
        super().__init__(parent)
        self.volume = volume
        self.main_window = parent
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
        edit_icon_path = resource_filename(
                'VisualPIC.Icons', 'editIcon.png')
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(edit_icon_path)),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.editButton.setIcon(icon)
        self.editButton.setObjectName(_fromUtf8("editButton"))
        self.horizontalLayout.addWidget(self.editButton)
        self.deleteButton = QtWidgets.QPushButton(self)
        self.deleteButton.setMaximumSize(QtCore.QSize(24, 16777215))
        self.deleteButton.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        delete_icon_path = resource_filename(
                'VisualPIC.Icons', 'deleteIcon.png')
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(delete_icon_path)),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.deleteButton.setIcon(icon1)
        self.deleteButton.setObjectName(_fromUtf8("deleteButton"))
        self.horizontalLayout.addWidget(self.deleteButton)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        # call initial methods
        self.set_text()
        self.register_ui_events()

    def set_text(self):
        self.FieldName.setText(self.volume.get_field_name())
        self.SpeciesName.setText(self.volume.get_species_name())

    def register_ui_events(self):
        self.editButton.clicked.connect(self.edit_button_clicked)
        self.deleteButton.clicked.connect(self.delete_button_clicked)
        
    def edit_button_clicked(self):
        self.edit_window = EditVolumeVTKWindow(self.volume, self.main_window)
        self.edit_window.show()
        screen_geometry = QtWidgets.QApplication.desktop().screenGeometry()
        x = (screen_geometry.width()-self.edit_window.width()) / 2;
        y = (screen_geometry.height()-self.edit_window.height()) / 2;
        self.edit_window.move(x, y);
        
    def delete_button_clicked(self):
        self.main_window.remove_field(self)
        