import vtk
from PyQt5.Qt import Qt
from PyQt5 import QtCore, QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from VisualPIC.ui.setup_field_volume_window import SetupFieldVolumeWindow
from VisualPIC.ui.brightness_contrast_dialog import BrightnessContrastDialog


class BasicRenderWindow(QtWidgets.QMainWindow):

    """Basic Qt window for interactive visualization of 3D renders."""

    def __init__(self, vtk_visualizer, parent=None):
        super().__init__(parent=parent)
        self.vtk_vis = vtk_visualizer
        self.setup_interface()
        self.register_ui_events()
        self.show()

    def setup_interface(self):
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
        self.timestep_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.hl.addWidget(self.timestep_slider)
        self.edit_fields_button = QtWidgets.QPushButton()
        self.edit_fields_button.setText('Edit fields')
        self.settings_button = QtWidgets.QPushButton()
        self.settings_button.setText('Settings')
        self.hl.addWidget(self.edit_fields_button)
        self.hl.addWidget(self.settings_button)
        
        self.vl.addLayout(self.hl)
        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

    def register_ui_events(self):
        self.edit_fields_button.clicked.connect(self.edit_fields_button_clicked)
        self.settings_button.clicked.connect(self.settings_button_clicked)

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

    def closeEvent(self, *args, **kwargs):
        """ This fixes bug described in 
        (http://vtk.1045678.n5.nabble.com/Multiple-vtkRenderWindows-Error-
        during-cleanup-wglMakeCurrent-failed-in-Clean-tt5747036.html)
        """
        self.vtk_widget.GetRenderWindow().Finalize()
        super(BasicRenderWindow, self).closeEvent(*args, **kwargs)
