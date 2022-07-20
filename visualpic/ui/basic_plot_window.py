"""
This file is part of VisualPIC.

The module contains the class for the basic Qt window for the matplotlib
visualizer.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""


from pkg_resources import resource_filename
import platform
import ctypes

import numpy as np
from PyQt5.Qt import Qt, QStyleFactory
from PyQt5 import QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from visualpic.helper_functions import (
    get_closest_timestep, get_next_timestep, get_previous_timestep)

# code for proper scaling in high-DPI screens. Move this somewhere else once \
# final UI is implemented.
if platform.system() == 'Windows':
    myappid = 'visualpic'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    ctypes.windll.user32.SetProcessDPIAware()
# Enable scaling for high DPI displays
QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setStyle(QStyleFactory.create('Fusion'))


class BasicPlotWindow(QtWidgets.QMainWindow):

    """Basic Qt window for interactive visualization matplotlib plots."""

    def __init__(self, vp_figure, mpl_visualizer, parent=None):
        super().__init__(parent=parent)
        self.vp_figure = vp_figure
        self.mpl_vis = mpl_visualizer
        self.available_timesteps = self.vp_figure.get_available_timesteps()
        self.timestep_change_callbacks = []
        self.setup_interface()
        self.register_ui_events()
        self.show()

    def setup_interface(self):
        self.resize(600, 400)
        self.setWindowTitle('VisualPIC - 2D Viewer')
        icon_path = resource_filename('visualpic.ui.icons',
                                      'vp_logo_sq_blue.png')
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.frame = QtWidgets.QFrame()
        self.vl = QtWidgets.QVBoxLayout()
        self.dialog_dict = {}
        self.settings_dialog = None

        self.figure_canvas = FigureCanvasQTAgg(self.vp_figure._mpl_figure)
        self.vl.addWidget(self.figure_canvas)

        self.hl = QtWidgets.QHBoxLayout()
        self.timestep_line_edit = QtWidgets.QLineEdit()
        self.timestep_line_edit.setReadOnly(True)
        self.timestep_line_edit.setAlignment(Qt.AlignCenter)
        self.timestep_line_edit.setText(str(self.vp_figure._current_timestep))
        self.timestep_line_edit.setMaximumWidth(50)
        self.hl.addWidget(self.timestep_line_edit)
        self.prev_button = QtWidgets.QPushButton()
        prev_icon_path = resource_filename('visualpic.ui.icons',
                                           'left_arrow.png')
        self.prev_button.setIcon(QtGui.QIcon(prev_icon_path))
        if len(self.available_timesteps) == 0:
            self.prev_button.setEnabled(False)
        self.hl.addWidget(self.prev_button)
        self.next_button = QtWidgets.QPushButton()
        next_icon_path = resource_filename('visualpic.ui.icons',
                                           'right_arrow.png')
        self.next_button.setIcon(QtGui.QIcon(next_icon_path))
        if len(self.available_timesteps) == 0:
            self.next_button.setEnabled(False)
        self.hl.addWidget(self.next_button)
        self.timestep_slider = QtWidgets.QSlider(Qt.Horizontal)
        if len(self.available_timesteps) > 0:
            self.timestep_slider.setRange(np.min(self.available_timesteps),
                                          np.max(self.available_timesteps))
            self.timestep_slider.setValue(self.vp_figure._current_timestep)
        else:
            self.timestep_slider.setEnabled(False)
        self.hl.addWidget(self.timestep_slider)

        self.vl.addLayout(self.hl)
        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

    def register_ui_events(self):
        self.timestep_slider.sliderReleased.connect(
            self.timestep_slider_released)
        self.timestep_slider.valueChanged.connect(
            self.timestep_slider_value_changed)
        self.prev_button.clicked.connect(self.prev_button_clicked)
        self.next_button.clicked.connect(self.next_button_clicked)

    def prev_button_clicked(self):
        current_ts = self.timestep_slider.value()
        prev_ts = get_previous_timestep(current_ts, self.available_timesteps)
        if prev_ts != current_ts:
            self.timestep_slider.setValue(prev_ts)
        self.vp_figure.generate(prev_ts, False)
        self.figure_canvas.draw()
        # self.render_timestep(prev_ts)

    def next_button_clicked(self):
        current_ts = self.timestep_slider.value()
        next_ts = get_next_timestep(current_ts, self.available_timesteps)
        if next_ts != current_ts:
            self.timestep_slider.setValue(next_ts)
        self.vp_figure.generate(next_ts, False)
        self.figure_canvas.draw()
        # self.render_timestep(next_ts)

    def timestep_slider_released(self):
        value = self.timestep_slider.value()
        value = get_closest_timestep(value, self.available_timesteps)
        self.timestep_slider.setValue(value)
        self.vp_figure.generate(value, False)
        self.figure_canvas.draw()
        # self.render_timestep(value)

    def timestep_slider_value_changed(self, value):
        self.timestep_line_edit.setText(str(value))
