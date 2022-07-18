import matplotlib.pyplot as plt
from visualpic.helper_functions import get_common_timesteps


class Subplot():
    """Base class for a figure subplots.
    """
    def __init__(self, datasets, rc_params={}):
        if not isinstance(datasets, list):
            datasets = [datasets]
        self._datasets = datasets
        self.rc_params = rc_params

    def get_available_timesteps(self):
        return get_common_timesteps(self._datasets)

    def plot(self, timestep, subplot_spec, fig):
        with plt.rc_context(self.rc_params):
            self._make_plot(timestep, subplot_spec, fig)

    def _make_plot(self, timestep, subplot_spec, fig):
        raise NotImplementedError()
