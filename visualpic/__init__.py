__version__ = "0.5.2"


# make main classes directly available
from .data_handling.data_container import DataContainer
from .visualization import VTKVisualizer, MplVisualizer


__all__ = ['DataContainer', 'VTKVisualizer', 'MplVisualizer']
