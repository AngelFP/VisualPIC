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


from PyQt5 import QtCore, QtWidgets
import os
from PIL import Image
import numpy as np
from matplotlib.animation import FuncAnimation


class CreateAnimationWindow(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(CreateAnimationWindow, self).__init__(parent)
        
        self.mainWindow = parent
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_4 = QtWidgets.QLabel(self)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.firstStep_lineEdit = QtWidgets.QLineEdit(self)
        self.firstStep_lineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.firstStep_lineEdit.setObjectName("firstStep_lineEdit")
        self.horizontalLayout.addWidget(self.firstStep_lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.lastStep_lineEdit = QtWidgets.QLineEdit(self)
        self.lastStep_lineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lastStep_lineEdit.setObjectName("lastStep_lineEdit")
        self.horizontalLayout_2.addWidget(self.lastStep_lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.frequency_lineEdit = QtWidgets.QLineEdit(self)
        self.frequency_lineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.frequency_lineEdit.setObjectName("frequency_lineEdit")
        self.horizontalLayout_3.addWidget(self.frequency_lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.onlySnaps_checkBox = QtWidgets.QCheckBox(self)
        self.onlySnaps_checkBox.setObjectName("onlySnaps_checkBox")
        self.horizontalLayout_4.addWidget(self.onlySnaps_checkBox)
        self.makeVideo_checkBox = QtWidgets.QCheckBox(self)
        self.makeVideo_checkBox.setObjectName("makeVideo_checkBox")
        self.horizontalLayout_4.addWidget(self.makeVideo_checkBox)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.label_5 = QtWidgets.QLabel(self)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.frameTime_radioButton = QtWidgets.QRadioButton(self)
        self.frameTime_radioButton.setChecked(True)
        self.frameTime_radioButton.setObjectName("frameTime_radioButton")
        self.horizontalLayout_5.addWidget(self.frameTime_radioButton)
        self.totalTime_radioButton = QtWidgets.QRadioButton(self)
        self.totalTime_radioButton.setObjectName("totalTime_radioButton")
        self.horizontalLayout_5.addWidget(self.totalTime_radioButton)
        self.gifTime_lineEdit = QtWidgets.QLineEdit(self)
        self.gifTime_lineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.gifTime_lineEdit.setObjectName("gifTime_lineEdit")
        self.horizontalLayout_5.addWidget(self.gifTime_lineEdit)
        self.label_6 = QtWidgets.QLabel(self)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_5.addWidget(self.label_6)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.line2 = QtWidgets.QFrame(self)
        self.line2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line2.setObjectName("line2")
        self.verticalLayout.addWidget(self.line2)
        self.label_7 = QtWidgets.QLabel(self)
        self.label_7.setObjectName("label_7")
        self.verticalLayout.addWidget(self.label_7)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.saveTo_lineEdit = QtWidgets.QLineEdit(self)
        self.saveTo_lineEdit.setObjectName("saveTo_lineEdit")
        self.horizontalLayout_3.addWidget(self.saveTo_lineEdit)
        self.browse_Button = QtWidgets.QPushButton(self)
        self.browse_Button.setObjectName("browse_Button")
        self.horizontalLayout_3.addWidget(self.browse_Button)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.label_8 = QtWidgets.QLabel(self)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_4.addWidget(self.label_8)
        self.fileName_lineEdit = QtWidgets.QLineEdit(self)
        self.fileName_lineEdit.setObjectName("fileName_lineEdit")
        self.horizontalLayout_4.addWidget(self.fileName_lineEdit)
        self.create_Button = QtWidgets.QPushButton(self)
        self.create_Button.setObjectName("create_Button")
        self.verticalLayout.addWidget(self.create_Button)
        
        self._inputFilter = InputFilter(parent)
        self.isFirstRun = True
        self.hasAlreadyRun = False

        self.SetUpUI()
        self.registerUiEvents()

        QtCore.QMetaObject.connectSlotsByName(self)

    def SetUpUI(self):
        self.setWindowTitle("Create Snapshots and Animation")
        self.label_4.setText("Snapshots:")
        self.label.setText("First time step:")
        self.label_2.setText("Last time step:")
        self.label_3.setText("Step size:")
        self.firstStep_lineEdit.setText(str(self.mainWindow.time_steps[0]))
        self.lastStep_lineEdit.setText(str(self.mainWindow.time_steps[-1]))
        self.frequency_lineEdit.setText("1")
        self.onlySnaps_checkBox.setText("Create snapshots.")
        self.makeVideo_checkBox.setText("Create video.")
        self.label_5.setText("Framerate:")
        self.frameTime_radioButton.setText("Time between frames")
        self.totalTime_radioButton.setText("Total time")
        self.gifTime_lineEdit.setText("0.1")
        self.label_6.setText("[s]")
        self.label_7.setText("Save to:")
        self.label_8.setText("File name:")
        self.create_Button.setText("Create")
        self.browse_Button.setText("Browse")
        self.saveTo_lineEdit.setText(str(self.mainWindow.folderLocation_lineEdit.text()) + "/Animation")
        self.fileName_lineEdit.setText("movie")
        self.onlySnaps_checkBox.setChecked(True)
        self.makeVideo_checkBox.setChecked(True)
        
    def registerUiEvents(self):
        self.firstStep_lineEdit.installEventFilter(self._inputFilter)
        self.lastStep_lineEdit.installEventFilter(self._inputFilter)
        self.create_Button.clicked.connect(self.createButton_clicked)
        self.browse_Button.clicked.connect(self.OpenFolderDialog)
        #self.onlySnaps_checkBox.toggled.connect(self.onlySnapsCheckBox_StatusChanged)
        self.makeVideo_checkBox.toggled.connect(self.makeVideoCheckBox_StatusChanged)

    def OpenFolderDialog(self):
        folderPath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Save animation to:", self.saveTo_lineEdit.text()))
        if folderPath != "":
            self.saveTo_lineEdit.setText(folderPath)

    def createButton_clicked(self):
        self.createAnimation()
    
    def makeVideoCheckBox_StatusChanged(self):
        if self.makeVideo_checkBox.checkState():
            self.frameTime_radioButton.setEnabled(True)
            self.totalTime_radioButton.setEnabled(True)
            self.gifTime_lineEdit.setEnabled(True)
        else:
            self.frameTime_radioButton.setEnabled(False)
            self.totalTime_radioButton.setEnabled(False)
            self.gifTime_lineEdit.setEnabled(False)

    # The animation function seems to be called twice sometimes for some reason, but the video is only created on the first run.
    def init(self):
        if not self.hasAlreadyRun:
            self.isFirstRun = True
            self.hasAlreadyRun = True
            print("Creating animation...")
        else:
            print("Animation completed.")
            self.isFirstRun = False

    def animation_function(self, step):
        if self.isFirstRun:
            self.mainWindow.timeStep_Slider.setValue(step)
            self.mainWindow.MakePlots()
            if self.onlySnaps_checkBox.isChecked():
                movieName = self.fileName_lineEdit.text()
                framesDir = self.saveTo_lineEdit.text() + "/" + movieName + "_frames"
                frameNameAndPath = framesDir + "/" + movieName + "_frame_" + str(step).zfill(6)
                if not os.path.exists(framesDir):
                    os.makedirs(framesDir)
                self.mainWindow.figure.savefig(frameNameAndPath)
            print(step)

    def createAnimation(self):
        self.hasAlreadyRun = False
        simulationTimeSteps = self.mainWindow.time_steps
        firstTimeStep = int(self.firstStep_lineEdit.text())
        firstIndex = np.where(simulationTimeSteps == firstTimeStep)[0][0]
        lastTimeStep = int(self.lastStep_lineEdit.text())
        lastIndex = np.where(simulationTimeSteps == lastTimeStep)[0][0]
        freq = int(self.frequency_lineEdit.text())
        animDir = self.saveTo_lineEdit.text()
        fileName = self.fileName_lineEdit.text() + ".mp4"
        nameAndPath = animDir + "/" + fileName
        if self.makeVideo_checkBox.isChecked():
            # Calculate time between frames
            if self.frameTime_radioButton.isChecked():
                time = float(self.gifTime_lineEdit.text()) * 1000
            else:
                numberOfSteps = len(simulationTimeSteps[firstIndex:lastIndex+1:freq])
                time = float(self.gifTime_lineEdit.text()) / numberOfSteps * 1000
            # Make animation
            ani = FuncAnimation(self.mainWindow.figure, self.animation_function, frames=simulationTimeSteps[firstIndex:lastIndex+1:freq], init_func=self.init, interval = time, repeat=False)
            ani.save(nameAndPath)
        else:
            for i in simulationTimeSteps[firstIndex:lastIndex+1:freq]:
                self.mainWindow.timeStep_Slider.setValue(i)
                self.mainWindow.MakePlots()
                movieName = self.fileName_lineEdit.text()
                framesDir = self.saveTo_lineEdit.text() + "/" + movieName + "_frames"
                frameNameAndPath = framesDir + "/" + movieName + "_frame_" + str(i).zfill(6)
                if not os.path.exists(framesDir):
                    os.makedirs(framesDir)
                self.mainWindow.figure.savefig(frameNameAndPath)


class InputFilter(QtCore.QObject):

    def __init__(self, mainWindow):
        super(InputFilter,self).__init__()
        self.mainWindow = mainWindow

    def eventFilter(self, widget, event):
        # FocusOut event
        try:
            if event.type() == QtCore.QEvent.FocusOut:
                # do custom stuff
                step = int(widget.text())
                time_steps = self.mainWindow.time_steps
                if step not in time_steps:
                    higherTimeSteps = np.where(time_steps > step)[0]
                    if len(higherTimeSteps) == 0:
                        closestHigher = time_steps[0]
                    else:
                        closestHigher = time_steps[np.where(time_steps > step)[0][0]]
                    lowerTimeSteps = np.where(time_steps < step)[0]
                    if len(lowerTimeSteps) == 0:
                        closestLower = time_steps[-1]
                    else:
                        closestLower = time_steps[np.where(time_steps < step)[0][-1]]
                    if abs(step-closestHigher) < abs(step-closestLower):
                        widget.setText(str(closestHigher))
                    else:
                        widget.setText(str(closestLower))
        except:
            pass
        # return False so that the widget will also handle the event
        # otherwise it won't focus out
        return False