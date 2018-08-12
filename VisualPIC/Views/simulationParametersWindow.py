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


class SimulationParametersWindow(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(SimulationParametersWindow, self).__init__(parent)

        self.mainWindow = parent
        self.supportedSimulationCodes = ["Osiris", "HiPACE", "openPMD"]
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

        self.code_layouts = QtWidgets.QVBoxLayout(self)
        self.code_layouts.setObjectName("code_layouts")
        self.verticalLayout.addLayout(self.code_layouts)

        # Osiris layout
        self.osirisWidget = QtWidgets.QWidget()
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
        self.code_layouts.addWidget(self.osirisWidget)

        # HiPACE layout
        self.hiPACEWidget = QtWidgets.QWidget()
        self.hiPACEVerticalLayout = QtWidgets.QVBoxLayout(self.hiPACEWidget)
        self.hiPACEVerticalLayout.setObjectName("hiPACEVerticalLayout")
        """
        Add here your controls to the hiPACEVerticalLayout
        """
        self.hiPACEHorizontalLayout = QtWidgets.QHBoxLayout()
        self.hiPACEHorizontalLayout.setObjectName("hiPACEHorizontalLayout")
        self.hiPACELabel = QtWidgets.QLabel(self)
        self.hiPACELabel.setObjectName("hiPACELabel")
        self.hiPACEHorizontalLayout.addWidget(self.hiPACELabel)
        self.hiPACEPlasmaDensity_lineEdit = QtWidgets.QLineEdit(self)
        self.hiPACEPlasmaDensity_lineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.hiPACEPlasmaDensity_lineEdit.setObjectName("hiPACEPlasmaDensity_lineEdit")
        self.hiPACEHorizontalLayout.addWidget(self.hiPACEPlasmaDensity_lineEdit)
        self.hiPACEVerticalLayout.addLayout(self.hiPACEHorizontalLayout)
        self.code_layouts.addWidget(self.hiPACEWidget)

        # openPMD layout
        self.openPMDWidget = QtWidgets.QWidget()
        self.openPMDVerticalLayout = QtWidgets.QVBoxLayout(self.openPMDWidget)
        self.openPMDVerticalLayout.setObjectName("openPMDVerticalLayout")
        self.openPMDHorizontalLayout = QtWidgets.QHBoxLayout()
        self.openPMDHorizontalLayout.setObjectName("openPMDHorizontalLayout")
        self.openPMDVerticalLayout.addLayout(self.openPMDHorizontalLayout)
        self.openPMDHorizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.openPMDHorizontalLayout_4.setObjectName("openPMDHorizontalLayout_4")
        self.openPMDLaserInSimulation_checkBox = QtWidgets.QCheckBox(self)
        self.openPMDLaserInSimulation_checkBox.setObjectName("openPMDLaserInSimulation_checkBox")
        self.openPMDHorizontalLayout_4.addWidget(self.openPMDLaserInSimulation_checkBox)
        self.openPMDVerticalLayout.addLayout(self.openPMDHorizontalLayout_4)
        self.openPMDHorizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.openPMDHorizontalLayout_2.setObjectName("openPMDHorizontalLayout_2")
        self.openPMDLabel_2 = QtWidgets.QLabel(self)
        self.openPMDLabel_2.setObjectName("openPMDLabel_2")
        self.openPMDHorizontalLayout_2.addWidget(self.openPMDLabel_2)
        self.openPMDLaserWavelength_lineEdit = QtWidgets.QLineEdit(self)
        self.openPMDLaserWavelength_lineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.openPMDLaserWavelength_lineEdit.setObjectName("openPMDLaserWavelength_lineEdit")
        self.openPMDHorizontalLayout_2.addWidget(self.openPMDLaserWavelength_lineEdit)
        self.openPMDVerticalLayout.addLayout(self.openPMDHorizontalLayout_2)
        self.code_layouts.addWidget(self.openPMDWidget)

        # General
        self.accept_Button = QtWidgets.QPushButton(self)
        self.accept_Button.setObjectName("accept_Button")
        self.verticalLayout.addWidget(self.accept_Button)

        self.SetUpUI()
        self.registerUiEvents()

        QtCore.QMetaObject.connectSlotsByName(self)

    def SetUpUI(self):
        simParams = self.mainWindow.data_container.get_simulation_parameters()

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

        # HiPACE
        self.hiPACELabel.setText("Plasma density (10<sup>18</sup> cm<sup>-3</sup>):")
        if (len(simParams) == 0) or (simParams["SimulationCode"] != "HiPACE"):
            self.hiPACEPlasmaDensity_lineEdit.setText("0.1")
        elif simParams["SimulationCode"] == "HiPACE":
            self.hiPACEPlasmaDensity_lineEdit.setText(str(simParams["n_p"]))

        # openPMD
        self.openPMDLabel_2.setText("Laser wavelength (nm):")
        self.openPMDLaserInSimulation_checkBox.setText("Laser in simulation.")
        if (len(simParams) == 0) or (simParams["SimulationCode"] != "openPMD"):
            self.openPMDLaserWavelength_lineEdit.setText("800")
            self.openPMDLaserInSimulation_checkBox.setChecked(True)
        elif simParams["SimulationCode"] == "openPMD":
            self.openPMDLaserWavelength_lineEdit.setText(str(simParams["lambda_l"]))
            self.openPMDLaserInSimulation_checkBox.setChecked(simParams["isLaser"])

        # Default code options
        self.hiPACEWidget.setVisible(False)
        self.openPMDWidget.setVisible(False)

    def registerUiEvents(self):
        # General
        self.accept_Button.clicked.connect(self.acceptButton_clicked)
        self.simulationCode_comboBox.currentIndexChanged.connect(self.simulationCodeComboBox_IndexChanged)
        # Osiris
        self.osirisLaserInSimulation_checkBox.toggled.connect(self.osirisLaserInSimulationCheckBox_StatusChanged)
        # openPMD
        self.openPMDLaserInSimulation_checkBox.toggled.connect(self.openPMDLaserInSimulationCheckBox_StatusChanged)

    def simulationCodeComboBox_IndexChanged(self):
        if self.simulationCode_comboBox.currentText() == "Osiris":
            self.openPMDWidget.setVisible(False)
            self.hiPACEWidget.setVisible(False)
            self.osirisWidget.setVisible(True)
        elif self.simulationCode_comboBox.currentText() == "HiPACE":
            self.openPMDWidget.setVisible(False)
            self.hiPACEWidget.setVisible(True)
            self.osirisWidget.setVisible(False)
        elif self.simulationCode_comboBox.currentText() == "openPMD":
            self.openPMDWidget.setVisible(True)
            self.hiPACEWidget.setVisible(False)
            self.osirisWidget.setVisible(False)

    def acceptButton_clicked(self):
        self.set_simulation_parameters()

    def osirisLaserInSimulationCheckBox_StatusChanged(self):
        status = self.osirisLaserInSimulation_checkBox.isChecked()
        self.osirisLaserWavelength_lineEdit.setEnabled(status)
        self.osirisLabel_2.setEnabled(status)

    def openPMDLaserInSimulationCheckBox_StatusChanged(self):
        status = self.openPMDLaserInSimulation_checkBox.isChecked()
        self.openPMDLaserWavelength_lineEdit.setEnabled(status)
        self.openPMDLabel_2.setEnabled(status)

    def set_simulation_parameters(self):
        simulationCode = self.simulationCode_comboBox.currentText()
        simParams = dict()
        simParams["SimulationCode"] = simulationCode
        if simulationCode == "Osiris" or simulationCode == "openPMD":
            simParams["n_p"] = float(self.osirisPlasmaDensity_lineEdit.text())
            simParams["isLaser"] = self.osirisLaserInSimulation_checkBox.isChecked()
            if simParams["isLaser"]:
                simParams["lambda_l"] = float(self.osirisLaserWavelength_lineEdit.text())
        elif simulationCode == "HiPACE":
            simParams["n_p"] = float(self.hiPACEPlasmaDensity_lineEdit.text())
        elif simulationCode == "openPMD":
            simParams["isLaser"] = self.openPMDLaserInSimulation_checkBox.isChecked()
            if simParams["isLaser"]:
                simParams["lambda_l"] = float(self.openPMDLaserWavelength_lineEdit.text())

        self.mainWindow.data_container.set_simulation_parameters(simParams)
        self.close()
