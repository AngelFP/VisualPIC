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

from PyQt5 import QtCore, QtWidgets


class SimulationParametersWindow(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(SimulationParametersWindow, self).__init__(parent)
        
        self.mainWindow = parent
        self.supportedSimulationCodes = ["Osiris", "HiPACE"]
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.simulationCode_comboBox = QtWidgets.QComboBox(self)
        self.simulationCode_comboBox.setObjectName("simulationCode_comboBox")
        self.horizontalLayout.addWidget(self.simulationCode_comboBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)

        # Osiris layout
        self.osirisWidget = QtWidgets.QWidget(self)
        self.osirisVerticalLayout = QtWidgets.QVBoxLayout(self.osirisWidget)
        self.osirisVerticalLayout.setObjectName("osirisVerticalLayout")
        self.osirisHorizontalLayout = QtWidgets.QHBoxLayout()
        self.osirisHorizontalLayout.setObjectName("osirisHorizontalLayout")
        self.osirisLabel = QtWidgets.QLabel(self)
        self.osirisLabel.setObjectName("osirisLabel")
        self.osirisHorizontalLayout.addWidget(self.osirisLabel)
        self.osirisPlasmaDensity_lineEdit = QtWidgets.QLineEdit(self)
        self.osirisPlasmaDensity_lineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.osirisPlasmaDensity_lineEdit.setObjectName("osirisPlasmaDensity_lineEdit")
        self.osirisHorizontalLayout.addWidget(self.osirisPlasmaDensity_lineEdit)
        self.osirisVerticalLayout.addLayout(self.osirisHorizontalLayout)
        self.osirisLine = QtWidgets.QFrame(self)
        self.osirisLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.osirisLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.osirisLine.setObjectName("osirisLine")
        self.osirisVerticalLayout.addWidget(self.osirisLine)
        self.osirisHorizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.osirisHorizontalLayout_4.setObjectName("osirisHorizontalLayout_4")
        self.osirisLaserInSimulation_checkBox = QtWidgets.QCheckBox(self)
        self.osirisLaserInSimulation_checkBox.setObjectName("osirisLaserInSimulation_checkBox")
        self.osirisHorizontalLayout_4.addWidget(self.osirisLaserInSimulation_checkBox)
        self.osirisVerticalLayout.addLayout(self.osirisHorizontalLayout_4)
        self.osirisHorizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.osirisHorizontalLayout_2.setObjectName("osirisHorizontalLayout_2")
        self.osirisLabel_2 = QtWidgets.QLabel(self)
        self.osirisLabel_2.setObjectName("osirisLabel_2")
        self.osirisHorizontalLayout_2.addWidget(self.osirisLabel_2)
        self.osirisLaserWavelength_lineEdit = QtWidgets.QLineEdit(self)
        self.osirisLaserWavelength_lineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.osirisLaserWavelength_lineEdit.setObjectName("osirisLaserWavelength_lineEdit")
        self.osirisHorizontalLayout_2.addWidget(self.osirisLaserWavelength_lineEdit)
        self.osirisVerticalLayout.addLayout(self.osirisHorizontalLayout_2)
        self.verticalLayout.addWidget(self.osirisWidget)

        # HiPACE layout
        self.hiPACEWidget = QtWidgets.QWidget(self)
        self.hiPACEVerticalLayout = QtWidgets.QVBoxLayout(self.hiPACEWidget)
        self.hiPACEVerticalLayout.setObjectName("hiPACEVerticalLayout")
        """
        Add here your controls to the hiPACEVerticalLayout
        """
        self.verticalLayout.addWidget(self.hiPACEWidget)

        # General
        self.accept_Button = QtWidgets.QPushButton(self)
        self.accept_Button.setObjectName("accept_Button")
        self.verticalLayout.addWidget(self.accept_Button)

        self.SetUpUI()
        self.registerUiEvents()

        QtCore.QMetaObject.connectSlotsByName(self)

    def SetUpUI(self):
        simParams = self.mainWindow.dataContainer.GetSimulationParameters()
        # General
        self.setWindowTitle("Simulation Parameters")
        self.label.setText("Simulation code:")
        self.simulationCode_comboBox.addItems(self.supportedSimulationCodes)
        self.accept_Button.setText("Accept")
        # Osiris
        self.osirisLabel.setText("Plasma density (10<sup>18</sup> cm<sup>-3</sup>):")
        self.osirisLabel_2.setText("Laser wavelength (nm):")
        self.osirisLaserInSimulation_checkBox.setText("Laser in simulation.")
        if (len(simParams) == 0) or (simParams["SimulationCode"] != "Osiris"):
            self.osirisPlasmaDensity_lineEdit.setText("0.1")
            self.osirisLaserWavelength_lineEdit.setText("800")
            self.osirisLaserInSimulation_checkBox.setChecked(True)
        elif simParams["SimulationCode"] == "Osiris":
            self.osirisPlasmaDensity_lineEdit.setText(str(simParams["n_p"]))
            self.osirisLaserWavelength_lineEdit.setText(str(simParams["lambda_l"]))
            self.osirisLaserInSimulation_checkBox.setChecked(simParams["isLaser"])
        
    def registerUiEvents(self):
        # General
        self.accept_Button.clicked.connect(self.acceptButton_clicked)
        self.simulationCode_comboBox.currentIndexChanged.connect(self.simulationCodeComboBox_IndexChanged)
        # Osiris
        self.osirisLaserInSimulation_checkBox.toggled.connect(self.osirisLaserInSimulationCheckBox_StatusChanged)

    def simulationCodeComboBox_IndexChanged(self):
        if self.simulationCode_comboBox.currentText() == "Osiris":
            self.osirisWidget.setVisible(True)
            self.hiPACEWidget.setVisible(False)
        elif self.simulationCode_comboBox.currentText() == "HiPACE":
            self.osirisWidget.setVisible(False)
            self.hiPACEWidget.setVisible(True)

    def acceptButton_clicked(self):
        self.SetSimulationParameters()

    def osirisLaserInSimulationCheckBox_StatusChanged(self):
        status = self.osirisLaserInSimulation_checkBox.isChecked()
        self.osirisLaserWavelength_lineEdit.setEnabled(status)
        self.osirisLabel_2.setEnabled(status)

    def SetSimulationParameters(self):
        simulationCode = self.simulationCode_comboBox.currentText()
        simParams = dict()
        simParams["SimulationCode"] = simulationCode
        if simulationCode == "Osiris":
            simParams["n_p"] = float(self.osirisPlasmaDensity_lineEdit.text())
            simParams["isLaser"] = self.osirisLaserInSimulation_checkBox.isChecked()
            if simParams["isLaser"]:
                simParams["lambda_l"] = float(self.osirisLaserWavelength_lineEdit.text())
        self.mainWindow.dataContainer.SetSimulationParameters(simParams)
        self.close()
