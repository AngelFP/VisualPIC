from pkg_resources import resource_filename

import vtk
import numpy as np
from PyQt5.Qt import Qt
from PyQt5 import QtCore, QtWidgets, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from VisualPIC.ui.setup_field_volume_window import SetupFieldVolumeWindow
from VisualPIC.ui.brightness_contrast_dialog import BrightnessContrastDialog
from VisualPIC.helper_functions import (
    get_closest_timestep, get_previous_timestep, get_next_timestep)


class BasicRenderWindow(QtWidgets.QMainWindow):

    """Basic Qt window for interactive visualization of 3D renders."""

    def __init__(self, vtk_visualizer, parent=None):
        super().__init__(parent=parent)
        self.vtk_vis = vtk_visualizer
        self.available_timesteps = self.vtk_vis.get_possible_timesteps()
        self.timestep_change_callbacks = []
        self.setup_interface()
        self.register_ui_events()
        self.show()

    def setup_interface(self):
        self.setWindowTitle('VisualPIC - 3D Visualizer')
        icon_path = resource_filename('VisualPIC.ui.icons',
                                      'vp_logo_sq_blue.png')
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.frame = QtWidgets.QFrame()
        self.vl = QtWidgets.QVBoxLayout()
        self.dialog_dict = {}
        self.settings_dialog = None

        self.vtk_widget = QVTKRenderWindowInteractor(
            self.frame, rw=self.vtk_vis.window, iren=self.vtk_vis.interactor)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        self.interactor.Initialize()
        self.vl.addWidget(self.vtk_widget)

        self.hl = QtWidgets.QHBoxLayout()
        self.timestep_line_edit = QtWidgets.QLineEdit()
        self.timestep_line_edit.setReadOnly(True)
        self.timestep_line_edit.setAlignment(Qt.AlignCenter)
        self.timestep_line_edit.setText(str(self.vtk_vis.current_time_step))
        self.timestep_line_edit.setMaximumWidth(50)
        self.hl.addWidget(self.timestep_line_edit)
        self.prev_button = QtWidgets.QPushButton()
        prev_icon_path = resource_filename('VisualPIC.ui.icons',
                                           'left_arrow.png')
        self.prev_button.setIcon(QtGui.QIcon(prev_icon_path))
        self.hl.addWidget(self.prev_button)
        self.next_button = QtWidgets.QPushButton()
        next_icon_path = resource_filename('VisualPIC.ui.icons',
                                           'right_arrow.png')
        self.next_button.setIcon(QtGui.QIcon(next_icon_path))
        self.hl.addWidget(self.next_button)
        self.timestep_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.timestep_slider.setRange(np.min(self.available_timesteps),
                                      np.max(self.available_timesteps))
        self.timestep_slider.setValue(self.vtk_vis.current_time_step)
        self.hl.addWidget(self.timestep_slider)
        self.edit_fields_button = QtWidgets.QPushButton()
        # Icon by Garrett Knoll, from The Noun Project, CC BY 3.0 us,
        # https://commons.wikimedia.org/w/index.php?curid=49665075
        edit_icon_path = resource_filename('VisualPIC.ui.icons', 'edit.svg')
        self.edit_fields_button.setIcon(QtGui.QIcon(edit_icon_path))
        self.hl.addWidget(self.edit_fields_button)
        self.settings_button = QtWidgets.QPushButton()
        # Icon by
        # https://phabricator.wikimedia.org/diffusion/GOJU/browse/master/
        # AUTHORS.txt 
        # - lib/oojs-ui/themes/mediawiki/images/icons/, MIT,
        # https://commons.wikimedia.org/w/index.php?curid=54913197
        settings_icon_path = resource_filename('VisualPIC.ui.icons',
                                               'slider_settings.svg')
        self.settings_button.setIcon(QtGui.QIcon(settings_icon_path))
        self.hl.addWidget(self.settings_button)
        self.save_button = QtWidgets.QPushButton()
        # Icon By Font Awesome by Dave Gandy -
        # https://fortawesome.github.com/Font-Awesome, CC BY-SA 3.0,
        # https://commons.wikimedia.org/w/index.php?curid=24231809
        save_icon_path = resource_filename('VisualPIC.ui.icons', 'save.svg')
        self.save_button.setIcon(QtGui.QIcon(save_icon_path))
        self.hl.addWidget(self.save_button)
        
        self.vl.addLayout(self.hl)
        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

    def register_ui_events(self):
        self.edit_fields_button.clicked.connect(
            self.edit_fields_button_clicked)
        self.settings_button.clicked.connect(self.settings_button_clicked)
        self.prev_button.clicked.connect(self.prev_button_clicked)
        self.next_button.clicked.connect(self.next_button_clicked)
        self.save_button.clicked.connect(self.save_current_render_to_file)
        self.timestep_slider.sliderReleased.connect(
            self.timestep_slider_released)
        self.timestep_slider.valueChanged.connect(
            self.timestep_slider_value_changed)

    def edit_fields_button_clicked(self):
        fld_list = self.vtk_vis.get_list_of_fields()
        fld_name, ok_pressed = QtWidgets.QInputDialog.getItem(
            self, 'Edit field properties', 'Select field:', fld_list, 0, False)
        if ok_pressed:
            if fld_name in self.dialog_dict:
                setup_window = self.dialog_dict[fld_name]
            else:
                fld_idx = fld_list.index(fld_name)
                setup_window = SetupFieldVolumeWindow(
                    self.vtk_vis.volume_field_list[fld_idx], self)
                self.dialog_dict[fld_name] = setup_window
            setup_window.show()

    def settings_button_clicked(self):
        if self.settings_dialog is None:
            self.settings_dialog = BrightnessContrastDialog(self.vtk_vis, self)
        self.settings_dialog.show()

    def prev_button_clicked(self):
        current_ts = self.timestep_slider.value()
        prev_ts = get_previous_timestep(current_ts, self.available_timesteps)
        if prev_ts != current_ts:
            self.timestep_slider.setValue(prev_ts)
        self.render_timestep(prev_ts)

    def next_button_clicked(self):
        current_ts = self.timestep_slider.value()
        next_ts = get_next_timestep(current_ts, self.available_timesteps)
        if next_ts != current_ts:
            self.timestep_slider.setValue(next_ts)
        self.render_timestep(next_ts)

    def timestep_slider_released(self):
        value = self.timestep_slider.value()
        value = get_closest_timestep(value, self.available_timesteps)
        self.timestep_slider.setValue(value)
        self.render_timestep(value)

    def timestep_slider_value_changed(self, value):
        self.timestep_line_edit.setText(str(value))

    def render_timestep(self, timestep):
        self.vtk_vis._make_timestep_render(timestep, ts_is_index=False)
        self.interactor.Render()
        for callback in self.timestep_change_callbacks:
            callback(timestep)

    def add_timestep_change_callback(self, callback):
        if callback not in self.timestep_change_callbacks:
            self.timestep_change_callbacks.append(callback)

    def remove_timestep_change_callback(self, callback):
        if callback in self.timestep_change_callbacks:
            self.timestep_change_callbacks.remove(callback)

    def save_current_render_to_file(self):
        file_path, format = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save current view', '', 'PNG (*.png)')
        if file_path != '':
            window = self.vtk_widget.GetRenderWindow()
            w2if = vtk.vtkWindowToImageFilter()
            w2if.SetInput(window)        
            w2if.Update()
            writer = vtk.vtkPNGWriter()
            writer.SetFileName(file_path)
            writer.SetInputConnection(w2if.GetOutputPort())
            writer.Write()

    def closeEvent(self, *args, **kwargs):
        """ This fixes bug described in 
        (http://vtk.1045678.n5.nabble.com/Multiple-vtkRenderWindows-Error-
        during-cleanup-wglMakeCurrent-failed-in-Clean-tt5747036.html)
        """
        self.vtk_widget.GetRenderWindow().Finalize()
        super(BasicRenderWindow, self).closeEvent(*args, **kwargs)
