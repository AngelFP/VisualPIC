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


# Add VisualPIC folder to python path, so that folders can be called as modules
import os
import inspect
import ctypes
import platform
import matplotlib
matplotlib.use('Qt5agg')
from matplotlib import rcParams
rcParams['figure.dpi'] = 80
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir) 

# Needed to change taskbar icon
if platform.system() == 'Windows':
    myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

 
if __name__ == '__main__':
    from VisualPIC.Views.mainWindow import MainWindow
    #from VisualPIC.Views.testWindow import TestWindow
    import sys
    from PyQt5 import QtWidgets
    from PyQt5.Qt import Qt, QStyleFactory, QFont
    import os

    # Enable scaling for high DPI displays
    #os.putenv("QT_AUTO_SCREEN_SCALE_FACTOR","1");
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setStyle(QStyleFactory.create('Fusion'))
    
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
    