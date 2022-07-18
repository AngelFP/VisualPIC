"""
This file is part of VisualPIC.

The module contains the class for the Qt dialog for editing the visual settings
of a particle species.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""


from PyQt5 import QtWidgets


class SetupScatterSpeciesDialog(QtWidgets.QDialog):

    """Basic dialog for editing the visual settings of a species."""

    def __init__(self, species, parent=None):
        super().__init__(parent=parent)
        self.species = species
        self.style_handler = species.style_handler
        self.main_window = parent
        self.setup_interface()
        self.register_ui_events()

    def showEvent(self, *args, **kwargs):
        self.register_time_step_events()
        super(SetupScatterSpeciesDialog, self).showEvent(*args, **kwargs)

    def closeEvent(self, *args, **kwargs):
        self.unregister_time_step_events()
        super(SetupScatterSpeciesDialog, self).closeEvent(*args, **kwargs)

    def setup_interface(self):
        self.setWindowTitle(
            'Edit species ({})'.format(self.species.get_name()))
        self.vl = QtWidgets.QVBoxLayout()

        # Color
        self.hl_1 = QtWidgets.QHBoxLayout()
        self.color_label = QtWidgets.QLabel('Color:')
        self.color_combobox = QtWidgets.QComboBox()
        self.possible_colors = self.style_handler.get_mpl_colors(
            only_basic=True)
        current_color = self.species.get_color()
        if current_color in self.possible_colors:
            color_idx = self.possible_colors.index(current_color)
            self.custom_color = None
        else:
            color_idx = 0
            self.possible_colors.insert(0, 'custom')
            self.custom_color = current_color
        self.color_combobox.addItems(self.possible_colors)
        self.color_combobox.setCurrentIndex(color_idx)
        self.hl_1.addWidget(self.color_label)
        self.hl_1.addWidget(self.color_combobox)
        self.vl.addLayout(self.hl_1)
        self.separator_1 = QtWidgets.QFrame()
        self.separator_1.setFrameShape(QtWidgets.QFrame.HLine)
        self.separator_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.vl.addWidget(self.separator_1)

        # Colormap
        self.hl_2 = QtWidgets.QHBoxLayout()
        self.color_according_checkbox = QtWidgets.QCheckBox(
            'Color according to:')
        self.color_variable_combobox = QtWidgets.QComboBox()
        self.av_comps = self.species.species.get_list_of_available_components()
        self.color_variable_combobox.addItems(self.av_comps)
        color_var = self.species.get_color_according_to()
        using_cmap = color_var is not None
        if using_cmap:
            self.color_variable_combobox.setCurrentIndex(
                self.av_comps.index(color_var))
        self.hl_2.addWidget(self.color_according_checkbox)
        self.hl_2.addWidget(self.color_variable_combobox)
        self.vl.addLayout(self.hl_2)
        self.hl_3 = QtWidgets.QHBoxLayout()
        self.cmap_label = QtWidgets.QLabel('Colormap:')
        self.cmap_combobox = QtWidgets.QComboBox()
        self.possible_cmaps = self.style_handler.get_available_cmaps()
        current_cmap = self.species.get_colormap()
        current_cmap_name = current_cmap.get_name()
        if current_cmap_name in self.possible_cmaps:
            cmap_idx = self.possible_cmaps.index(current_cmap_name)
            self.custom_cmap = None
        else:
            cmap_idx = 0
            self.possible_cmaps.insert(0, 'custom')
            self.custom_cmap = current_cmap
        self.cmap_combobox.addItems(self.possible_cmaps)
        self.cmap_combobox.setCurrentIndex(cmap_idx)
        self.hl_3.addWidget(self.cmap_label)
        self.hl_3.addWidget(self.cmap_combobox)
        self.vl.addLayout(self.hl_3)
        self.hl_4 = QtWidgets.QHBoxLayout()
        self.vmin_label = QtWidgets.QLabel('vmin:')
        self.vmin_lineedit = QtWidgets.QLineEdit()
        self.vmax_label = QtWidgets.QLabel('vmax:')
        self.vmax_lineedit = QtWidgets.QLineEdit()
        self.set_range_lineedits()
        self.set_range_button = QtWidgets.QPushButton('Set range')
        self.hl_4.addWidget(self.vmin_label)
        self.hl_4.addWidget(self.vmin_lineedit)
        self.hl_4.addWidget(self.vmax_label)
        self.hl_4.addWidget(self.vmax_lineedit)
        self.hl_4.addWidget(self.set_range_button)
        self.vl.addLayout(self.hl_4)
        self.set_using_colormap(using_cmap)
        self.separator_2 = QtWidgets.QFrame()
        self.separator_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.separator_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.vl.addWidget(self.separator_2)

        # Size
        self.hl_5 = QtWidgets.QHBoxLayout()
        self.size_label = QtWidgets.QLabel()
        self.size_label.setText('Particle size:')
        self.size_spinbox = QtWidgets.QDoubleSpinBox()
        self.size_spinbox.setMaximum(10)
        self.size_spinbox.setMinimum(0.1)
        self.size_spinbox.setSingleStep(0.1)
        self.size_spinbox.setValue(self.species.get_size())
        self.hl_5.addWidget(self.size_label)
        self.hl_5.addWidget(self.size_spinbox)
        self.vl.addLayout(self.hl_5)
        self.size_scale_checkbox = QtWidgets.QCheckBox(
            'Scale size with particle charge')
        self.size_scale_checkbox.setChecked(
            self.species.get_scale_with_charge())
        self.vl.addWidget(self.size_scale_checkbox)
        self.setLayout(self.vl)

    def register_ui_events(self):
        self.color_combobox.currentIndexChanged.connect(
            self.color_combobox_index_changed)
        self.color_according_checkbox.stateChanged.connect(
            self.color_according_checkbox_changed)
        self.color_variable_combobox.currentTextChanged.connect(
            self.color_variable_combobox_text_changed)
        self.cmap_combobox.currentTextChanged.connect(
            self.cmap_combobox_text_changed)
        self.size_spinbox.valueChanged.connect(
            self.size_spinbox_value_changed)
        self.size_scale_checkbox.stateChanged.connect(
            self.size_scale_checkbox_changed)
        self.set_range_button.clicked.connect(self.set_range_button_clicked)

    def color_combobox_index_changed(self, idx):
        selected_color = self.possible_colors[idx]
        self.species.set_color(selected_color)
        self.update_render()

    def color_according_checkbox_changed(self, checked):
        self.set_using_colormap(checked)
        if checked:
            current_color_var = self.color_variable_combobox.currentText()
            self.species.set_color_according_to(current_color_var)
            self.species.update_data(self.species.get_current_timestep())
        else:
            self.species.set_color_according_to(None)
        self.main_window.vtk_vis.draw_colorbars()
        self.update_render()

    def color_variable_combobox_text_changed(self, var_name):
        self.species.set_color_according_to(var_name)
        self.species.update_data(self.species.get_current_timestep())
        self.main_window.vtk_vis.draw_colorbars()
        self.set_range_lineedits()
        self.update_render()

    def cmap_combobox_text_changed(self, cmap_name):
        if cmap_name == 'custom':
            cmap = self.custom_cmap
        else:
            cmap = self.style_handler.get_cmap(cmap_name)
        self.species.set_colormap(cmap)
        self.update_render()

    def size_spinbox_value_changed(self, value):
        self.species.set_size(value)
        self.update_render()

    def size_scale_checkbox_changed(self, scale):
        self.species.set_scale_with_charge(scale)
        if scale:
            self.species.update_data(self.species.get_current_timestep())
        self.update_render()

    def set_range_button_clicked(self):
        try:
            vmin = float(self.vmin_lineedit.text())
        except:
            vmin = None
        try:
            vmax = float(self.vmax_lineedit.text())
        except:
            vmax = None
        self.species.set_colormap_range(vmin, vmax)
        self.species.update_data(self.species.get_current_timestep())
        self.update_render()

    def set_range_lineedits(self, *args):
        vmin, vmax = self.species.get_colormap_range()
        if vmin is not None:
            self.vmin_lineedit.setText(format(vmin, '.2e'))
        if vmax is not None:
            self.vmax_lineedit.setText(format(vmax, '.2e'))

    def set_using_colormap(self, using_colormap):
        self.color_label.setEnabled(not using_colormap)
        self.color_combobox.setEnabled(not using_colormap)
        self.color_according_checkbox.setChecked(using_colormap)
        self.color_variable_combobox.setEnabled(using_colormap)
        self.cmap_combobox.setEnabled(using_colormap)
        self.cmap_label.setEnabled(using_colormap)
        self.vmin_label.setEnabled(using_colormap)
        self.vmin_lineedit.setEnabled(using_colormap)
        self.vmax_label.setEnabled(using_colormap)
        self.vmax_lineedit.setEnabled(using_colormap)
        self.set_range_button.setEnabled(using_colormap)

    def update_render(self):
        self.main_window.interactor.Render()

    def register_time_step_events(self):
        self.main_window.add_timestep_change_callback(self.set_range_lineedits)

    def unregister_time_step_events(self):
        self.main_window.remove_timestep_change_callback(
            self.set_range_lineedits)
