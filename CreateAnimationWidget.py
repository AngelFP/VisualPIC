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
import os
import images2gif
from PIL import Image
import numpy as np


class CreateAnimationWidget(QtGui.QDialog):
    def __init__(self,parent=None):
        
        super(CreateAnimationWidget, self).__init__(parent)
        
        self.mainWindow = parent
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_4 = QtGui.QLabel(self)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(self)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.firstStep_lineEdit = QtGui.QLineEdit(self)
        self.firstStep_lineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.firstStep_lineEdit.setObjectName("firstStep_lineEdit")
        self.horizontalLayout.addWidget(self.firstStep_lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.lastStep_lineEdit = QtGui.QLineEdit(self)
        self.lastStep_lineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lastStep_lineEdit.setObjectName("lastStep_lineEdit")
        self.horizontalLayout_2.addWidget(self.lastStep_lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtGui.QLabel(self)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.frequency_lineEdit = QtGui.QLineEdit(self)
        self.frequency_lineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.frequency_lineEdit.setObjectName("frequency_lineEdit")
        self.horizontalLayout_3.addWidget(self.frequency_lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.onlySnaps_checkBox = QtGui.QCheckBox(self)
        self.onlySnaps_checkBox.setObjectName("onlySnaps_checkBox")
        self.horizontalLayout_4.addWidget(self.onlySnaps_checkBox)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.line = QtGui.QFrame(self)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.label_5 = QtGui.QLabel(self)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.frameTime_radioButton = QtGui.QRadioButton(self)
        self.frameTime_radioButton.setChecked(True)
        self.frameTime_radioButton.setObjectName("frameTime_radioButton")
        self.horizontalLayout_5.addWidget(self.frameTime_radioButton)
        self.totalTime_radioButton = QtGui.QRadioButton(self)
        self.totalTime_radioButton.setObjectName("totalTime_radioButton")
        self.horizontalLayout_5.addWidget(self.totalTime_radioButton)
        self.gifTime_lineEdit = QtGui.QLineEdit(self)
        self.gifTime_lineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.gifTime_lineEdit.setObjectName("gifTime_lineEdit")
        self.horizontalLayout_5.addWidget(self.gifTime_lineEdit)
        self.label_6 = QtGui.QLabel(self)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_5.addWidget(self.label_6)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.create_Button = QtGui.QPushButton(self)
        self.create_Button.setObjectName("create_Button")
        self.verticalLayout.addWidget(self.create_Button)

        self.retranslateUi()
        self.registerUiEvents()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle("Create Animation")
        self.label_4.setText("Snapshots:")
        self.label.setText("First time step:")
        self.label_2.setText("Last time step:")
        self.label_3.setText("Frequency:")
        self.firstStep_lineEdit.setText("0")
        self.lastStep_lineEdit.setText(str(self.mainWindow.availableData.GetNumberOfTimeSteps()-1))
        self.frequency_lineEdit.setText("1")
        self.onlySnaps_checkBox.setText("Create only snapshots")
        self.label_5.setText("Gif properties:")
        self.frameTime_radioButton.setText("Time between frames")
        self.totalTime_radioButton.setText("Total time")
        self.gifTime_lineEdit.setText("0.1")
        self.label_6.setText("[s]")
        self.create_Button.setText("Create")
        
    def registerUiEvents(self):
        self.create_Button.clicked.connect(self.createButton_clicked)
        self.onlySnaps_checkBox.toggled.connect(self.onlySnapsCheckBox_StatusChanged)
    
    def createButton_clicked(self):
        self.createAnimation()
    
    def onlySnapsCheckBox_StatusChanged(self):
        if self.onlySnaps_checkBox.checkState():
            self.frameTime_radioButton.setEnabled(False)
            self.totalTime_radioButton.setEnabled(False)
            self.gifTime_lineEdit.setEnabled(False)
        else:
            self.frameTime_radioButton.setEnabled(True)
            self.totalTime_radioButton.setEnabled(True)
            self.gifTime_lineEdit.setEnabled(True)
    
    def createAnimation(self):
        totalSimulationTimeSteps = self.mainWindow.availableData.GetNumberOfTimeSteps()
        firstTimeStep = int(self.firstStep_lineEdit.text())
        lastTimeStep = int(self.lastStep_lineEdit.text())
        freq = int(self.frequency_lineEdit.text())
        animDir = self.mainWindow.folderLocation_lineEdit.text() + "/Animation"
        charLen = len(str(totalSimulationTimeSteps))
        file_paths = list()
        if not os.path.exists(animDir):
            os.makedirs(animDir)
        for i in np.arange(firstTimeStep,lastTimeStep + 1,freq):
            self.mainWindow.timeStep_Slider.setValue(i)
            self.mainWindow.PlotFields()
            fileName = animDir + "/frame" + str(i).zfill(charLen)
            self.mainWindow.figure.savefig(fileName)
            file_paths.append(fileName + ".png")
        
        
        if not self.onlySnaps_checkBox.checkState():
                
            images = [Image.open(fn) for fn in file_paths]
            filename = animDir + "/animation.GIF"
            
            if self.frameTime_radioButton.isChecked():
                time = float(self.gifTime_lineEdit.text())
            else:
                numberOfSteps = lastTimeStep - firstTimeStep
                time = float(self.gifTime_lineEdit.text()) / numberOfSteps
            images2gif.writeGif(filename, images, duration=time)

