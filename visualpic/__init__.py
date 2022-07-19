__version__ = "0.5.0"


# make main classes directly available
from .data_handling.data_container import DataContainer
from .visualization.vtk_visualizer import VTKVisualizer


__all__ = ['DataContainer', 'VTKVisualizer']
