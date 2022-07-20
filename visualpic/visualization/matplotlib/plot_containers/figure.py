import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from visualpic.helper_functions import get_common_array_elements


class VPFigure():
    """
    Class defining a VisualPIC figure. Mainly a wrapper around a matplotlib
    Figure.
    """
    def __init__(self, rc_params={}, **kwargs):
        self._subplot_list = []
        with plt.rc_context(rc_params):
            self._mpl_figure = Figure(tight_layout=True)
        self._current_timestep = -1

    def add_subplot(self, subplot):
        self._subplot_list.append(subplot)
        self.available_time_steps = self.get_available_timesteps()

    def generate(self, timestep, ts_is_index):
        if ts_is_index:
            self._current_timestep = self.available_time_steps[timestep]
        else:
            if timestep not in self.available_time_steps:
                raise ValueError(
                    'Time step {} is not available.'.format(timestep))
            self._current_timestep = timestep
        self._mpl_figure.clear()
        gs = self._mpl_figure.add_gridspec(1, len(self._subplot_list))

        for i, subplot in enumerate(self._subplot_list):
            # ax = self._mpl_figure.add_subplot(gs[i])
            subplot.plot(self._current_timestep, gs[i], self._mpl_figure)
        # self._mpl_figure.tight_layout()

    def get_available_timesteps(self):
        ts_list = []
        for subplot in self._subplot_list:
            ts_list.append(subplot.get_available_timesteps())
        return get_common_array_elements(ts_list)
