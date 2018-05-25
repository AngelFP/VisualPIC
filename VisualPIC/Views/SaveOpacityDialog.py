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

import sys
import os

from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QDialogButtonBox, QMessageBox
from VisualPIC.Tools.visualizer3Dvtk import ColormapHandler


if getattr(sys, 'frozen', False):
    # we are running in a bundle
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
guipath = os.path.join( bundle_dir, 'SaveOpacityDialog.ui' )
Ui_SaveOpacityDialog, QSaveOpacityDialog = loadUiType(guipath)


class SaveOpacityDialog(QSaveOpacityDialog, Ui_SaveOpacityDialog):
    def __init__(self, fld_val, op_val, parent=None):
        super(SaveOpacityDialog, self).__init__(parent)
        self.setupUi(self)
        self.cmap_handler = ColormapHandler()
        self.fld_val = fld_val
        self.op_val = op_val
        self.register_ui_events()
        self.setup_ui()

    def register_ui_events(self):
        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.save_to_file)

    def setup_ui(self):
        self.location_lineEdit.setText(self.cmap_handler.opacity_folder_path)

    def save_to_file(self):
        op_name = self.opacity_name_lineEdit.text()
        folder_path = self.location_lineEdit.text()
        if self.cmap_handler.save_opacity(op_name, self.fld_val, self.op_val, folder_path):
            success_message = QMessageBox(parent=self, text="Profile succesfully saved.")
            success_message.exec_()


