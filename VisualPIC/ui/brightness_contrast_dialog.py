from PyQt5.Qt import Qt
from PyQt5 import QtWidgets


class BrightnessContrastDialog(QtWidgets.QDialog):

    """Basic dialog for editing the brightness and contrast of the render."""

    def __init__(self, vtk_visualizer, parent=None):
        super().__init__(parent=parent)
        self.vtk_vis = vtk_visualizer
        self.setup_interface()
        self.register_ui_events()

    def setup_interface(self):
        self.vl = QtWidgets.QVBoxLayout()

        self.brightness_title_label = QtWidgets.QLabel()
        self.brightness_title_label.setText('Brightness:')
        self.vl.addWidget(self.brightness_title_label)
        self.hl_1 = QtWidgets.QHBoxLayout()
        current_brightness = self.vtk_vis.get_brightness()
        self.brightness_label = QtWidgets.QLabel()
        self.brightness_label.setText('{:0.2f}'.format(current_brightness))
        self.brightness_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(current_brightness*100)
        self.hl_1.addWidget(self.brightness_label)
        self.hl_1.addWidget(self.brightness_slider)
        self.vl.addLayout(self.hl_1)
        
        self.contrast_title_label = QtWidgets.QLabel()
        self.contrast_title_label.setText('Contrast:')
        self.vl.addWidget(self.contrast_title_label)
        self.hl_2 = QtWidgets.QHBoxLayout()
        current_contrast = self.vtk_vis.get_contrast()
        self.contrast_label = QtWidgets.QLabel()
        self.contrast_label.setText('{:0.2f}'.format(current_contrast))
        self.contrast_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(current_contrast*100)
        self.hl_2.addWidget(self.contrast_label)
        self.hl_2.addWidget(self.contrast_slider)
        self.vl.addLayout(self.hl_2)

        self.setLayout(self.vl)

    def register_ui_events(self):
        self.brightness_slider.valueChanged.connect(
            self.brightness_slider_value_changed)
        self.contrast_slider.valueChanged.connect(
            self.contrast_slider_value_changed)

    def brightness_slider_value_changed(self, brightness_value):
        self.brightness_label.setText('{:0.2f}'.format(brightness_value/100))
        self.vtk_vis.set_brightness(brightness_value/100)
        self.parent().interactor.Render()

    def contrast_slider_value_changed(self, contrast_value):
        self.contrast_label.setText('{:0.2f}'.format(contrast_value/100))
        self.vtk_vis.set_contrast(contrast_value/100)
        self.parent().interactor.Render()
