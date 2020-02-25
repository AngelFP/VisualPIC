import vtk
from PyQt5 import QtCore, QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class BasicRenderWindow(QtWidgets.QMainWindow):

    """Basic Qt window for intercative visualization of 3D renders."""

    def __init__(self, vtk_render_window, interactor, parent=None):
        super().__init__(parent=parent)
        self.frame = QtWidgets.QFrame()
        self.vl = QtWidgets.QVBoxLayout()
        self.vtk_widget = QVTKRenderWindowInteractor(
            self.frame, rw=vtk_render_window, iren=interactor)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        self.interactor.Initialize()
        self.vl.addWidget(self.vtk_widget)
        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)
        self.show()

    def closeEvent(self, *args, **kwargs):
        """ This fixes bug described in 
        (http://vtk.1045678.n5.nabble.com/Multiple-vtkRenderWindows-Error-
        during-cleanup-wglMakeCurrent-failed-in-Clean-tt5747036.html)
        """
        self.vtk_widget.GetRenderWindow().Finalize()
        super(BasicRenderWindow, self).closeEvent(*args, **kwargs)
