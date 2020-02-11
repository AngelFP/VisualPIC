# Try to import openPMD-viewer (required for openPMD data)
try:
    from openpmd_viewer import OpenPMDTimeSeries
    openpmd_installed = True
except ImportError:
    openpmd_installed = False
    
    
class OpenPMDTimeSeriesSingleton():
    """Class implementing an OpenPMDTimeSeries as singleton"""
    ts_instance = None
    
    def __init__(self, path_to_dir, check_all_files=True, reset=False):
        if OpenPMDTimeSeriesSingleton.ts_instance is None or reset == True:
            OpenPMDTimeSeriesSingleton.ts_instance = OpenPMDTimeSeries(
                path_to_dir, check_all_files)

    def __getattr__(self, name):
        return getattr(self.ts_instance, name)
