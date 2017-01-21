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


import os
import inspect
import ctypes
import platform
import sys
from PyQt5.QtWidgets import QApplication, QSplashScreen, QLabel, QVBoxLayout, QProgressBar
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSize
from PyQt5.Qt import Qt, QStyleFactory, QFont


# Add VisualPIC folder to python path, so that folders can be called as modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir) 


# Needed to change taskbar icon on Windows
if platform.system() == 'Windows':
    myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

 
if __name__ == '__main__':
    # Enable scaling for high DPI displays
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    
    app = QApplication(sys.argv)

    # Splash screen (loading heavy imports)
    screenGeometry = app.desktop().screenGeometry()
    splashPic = QPixmap("Icons/logo_horizontal.png")
    splashWidth = 550
    splashHeight = 150
    splashLabel = QLabel()
    splashLabel.setPixmap(splashPic)
    splashLabel.setScaledContents(True)
    splashLabel.setMaximumSize(QSize(splashWidth,splashHeight))
    splashLabel.setMinimumSize(QSize(splashWidth,splashHeight))
    splash = QSplashScreen()
    splashLayout = QVBoxLayout()
    splashLayout.setContentsMargins(0,0,0,0)
    splashLayout.setSpacing(0)
    splashLayout.addWidget(splashLabel)
    splashProgressBar = QProgressBar()
    splashProgressBar.setMaximumSize(QSize(splashWidth,20))
    splashProgressBar.setMinimumSize(QSize(splashWidth,20))
    splashLayout.addWidget(splashProgressBar)
    splash.setLayout(splashLayout)
    x = (screenGeometry.width()-splashLabel.width()) / 2;
    y = (screenGeometry.height()-splashLabel.height()) / 2;
    splash.move(x,y)
    splash.show()
    import matplotlib
    splashProgressBar.setValue(20)
    matplotlib.use('Qt5agg')
    splashProgressBar.setValue(40)
    from matplotlib import rcParams
    splashProgressBar.setValue(60)
    rcParams['figure.dpi'] = 80
    splashProgressBar.setValue(80)
    from VisualPIC.Views.mainWindow import MainWindow
    splashProgressBar.setValue(100)
    
    mainWindow = MainWindow()
    x = (screenGeometry.width()-mainWindow.width()) / 2;
    y = (screenGeometry.height()-mainWindow.height()) / 2 -20;
    mainWindow.move(x, y);
    
    mainWindow.show()
    splash.finish(mainWindow)
    sys.exit(app.exec_())
    