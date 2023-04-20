"""
This file is part of VisualPIC.

The module contains the class for the Qt dialog for the render settings.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""


from PyQt5.Qt import Qt
from PyQt5 import QtWidgets


class RenderSettingsDialog(QtWidgets.QDialog):

    """Basic dialog for editing the general settings of the render."""

    def __init__(self, vtk_visualizer, parent=None):
        super().__init__(parent=parent)
        self.vtk_vis = vtk_visualizer
        self.setup_interface()
        self.register_ui_events()

    def setup_interface(self):
        self.setWindowTitle('Settings')
        self.vl = QtWidgets.QVBoxLayout()

        # brightness
        self.brightness_title_label = QtWidgets.QLabel()
        self.brightness_title_label.setText('Brightness:')
        self.vl.addWidget(self.brightness_title_label)
        self.hl_1 = QtWidgets.QHBoxLayout()
        current_brightness = self.vtk_vis.get_brightness()
        self.brightness_label = QtWidgets.QLabel()
        self.brightness_label.setText('{:0.2f}'.format(current_brightness))
        self.brightness_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(int(current_brightness*100))
        self.hl_1.addWidget(self.brightness_label)
        self.hl_1.addWidget(self.brightness_slider)
        self.vl.addLayout(self.hl_1)

        # contrast
        self.contrast_title_label = QtWidgets.QLabel()
        self.contrast_title_label.setText('Contrast:')
        self.vl.addWidget(self.contrast_title_label)
        self.hl_2 = QtWidgets.QHBoxLayout()
        current_contrast = self.vtk_vis.get_contrast()
        self.contrast_label = QtWidgets.QLabel()
        self.contrast_label.setText('{:0.2f}'.format(current_contrast))
        self.contrast_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(int(current_contrast*100))
        self.hl_2.addWidget(self.contrast_label)
        self.hl_2.addWidget(self.contrast_slider)
        self.vl.addLayout(self.hl_2)

        # background
        self.background_title_label = QtWidgets.QLabel()
        self.background_title_label.setText('Background:')
        self.vl.addWidget(self.background_title_label)
        self.hl_3 = QtWidgets.QHBoxLayout()
        self.default_bg_button = QtWidgets.QRadioButton('Default')
        self.hl_3.addWidget(self.default_bg_button)
        self.black_bg_button = QtWidgets.QRadioButton('Black')
        self.hl_3.addWidget(self.black_bg_button)
        self.white_bg_button = QtWidgets.QRadioButton('White')
        self.hl_3.addWidget(self.white_bg_button)
        self.vl.addLayout(self.hl_3)
        current_bg = self.vtk_vis.get_background()
        if current_bg == 'default gradient':
            self.default_bg_button.setChecked(True)
        elif current_bg == 'black':
            self.black_bg_button.setChecked(True)
        elif current_bg == 'white':
            self.white_bg_button.setChecked(True)

        # axes, bbox, colorbars
        self.show_cube_axes_cb = QtWidgets.QCheckBox("Show cube axes")
        self.show_cube_axes_cb.setChecked(
            self.vtk_vis.vis_config['show_cube_axes'])
        self.vl.addWidget(self.show_cube_axes_cb)
        self.show_bbox_cb = QtWidgets.QCheckBox("Show bounding box")
        self.show_bbox_cb.setChecked(
            self.vtk_vis.vis_config['show_bounding_box'])
        self.vl.addWidget(self.show_bbox_cb)
        self.show_cbars_cb = QtWidgets.QCheckBox("Show colorbars")
        self.show_cbars_cb.setChecked(
            self.vtk_vis.vis_config['show_colorbars'])
        self.vl.addWidget(self.show_cbars_cb)

        self.setLayout(self.vl)

    def register_ui_events(self):
        self.brightness_slider.valueChanged.connect(
            self.brightness_slider_value_changed)
        self.contrast_slider.valueChanged.connect(
            self.contrast_slider_value_changed)
        self.default_bg_button.toggled.connect(self.default_bg_toggled)
        self.black_bg_button.toggled.connect(self.black_bg_toggled)
        self.white_bg_button.toggled.connect(self.white_bg_toggled)
        self.show_cube_axes_cb.stateChanged.connect(
            self.show_cube_axes_changed)
        self.show_bbox_cb.stateChanged.connect(self.show_bbox_changed)
        self.show_cbars_cb.stateChanged.connect(self.show_cbars_changed)

    def show_cube_axes_changed(self, value):
        self.vtk_vis.show_cube_axes(value)
        self.update_render()

    def show_bbox_changed(self, value):
        self.vtk_vis.show_bounding_box(value)
        self.update_render()

    def show_cbars_changed(self, value):
        self.vtk_vis.show_colorbars(value)
        self.update_render()

    def default_bg_toggled(self):
        self.vtk_vis.set_background('default gradient')
        self.update_render()

    def black_bg_toggled(self):
        self.vtk_vis.set_background('black')
        self.update_render()

    def white_bg_toggled(self):
        self.vtk_vis.set_background('white')
        self.update_render()

    def brightness_slider_value_changed(self, brightness_value):
        self.brightness_label.setText('{:0.2f}'.format(brightness_value/100))
        self.vtk_vis.set_brightness(brightness_value/100)
        self.update_render()

    def contrast_slider_value_changed(self, contrast_value):
        self.contrast_label.setText('{:0.2f}'.format(contrast_value/100))
        self.vtk_vis.set_contrast(contrast_value/100)
        self.update_render()

    def update_render(self):
        self.parent().interactor.Render()
