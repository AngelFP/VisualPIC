import vtk
from PyQt5.Qt import Qt
from PyQt5 import QtCore, QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

#from VisualPIC.ui.setup_field_volume_window import SetupFieldVolumeWindow


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

        self.vtk_widget = QVTKRenderWindowInteractor(
            self.frame, rw=self.vtk_vis.window, iren=self.vtk_vis.interactor)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        self.interactor.Initialize()
        self.vl.addWidget(self.vtk_widget)

        self.hl = QtWidgets.QHBoxLayout()
        self.timestep_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.hl.addWidget(self.timestep_slider)
        self.settings_button = QtWidgets.QPushButton()
        self.settings_button.setText('Settings')
        self.hl.addWidget(self.settings_button)
        
        self.vl.addLayout(self.hl)
        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

    def register_ui_events(self):
        self.settings_button.clicked.connect(self.settings_button_clicked)

    def settings_button_clicked(self):
        pass

    def closeEvent(self, *args, **kwargs):
        """ This fixes bug described in 
        (http://vtk.1045678.n5.nabble.com/Multiple-vtkRenderWindows-Error-
        during-cleanup-wglMakeCurrent-failed-in-Clean-tt5747036.html)
        """
        self.vtk_widget.GetRenderWindow().Finalize()
        super(BasicRenderWindow, self).closeEvent(*args, **kwargs)
