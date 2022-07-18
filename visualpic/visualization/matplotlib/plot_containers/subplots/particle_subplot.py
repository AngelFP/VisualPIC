from .subplot import Subplot
from visualpic.visualization.matplotlib.plot_types import particle_plot


class ParticleSubplot(Subplot):
    """Class defining a particle subplot.
    """
    def __init__(
            self, species, x='x', y='y', x_units=None, y_units=None,
            q_units=None, time_units=None, cbar=False):
        self._components = [x, y, 'q']
        self._component_units = [x_units, y_units, q_units]
        self._species_parameters = {
            'components_list': self._components,
            'data_units': self._component_units,
            'time_units': time_units
        }
        self._plot_parameters = {
            'cbar': cbar
        }
        super().__init__(species)

    def _make_plot(self, timestep, subplot_spec, fig):
        species = self._datasets[0]
        data = species.get_data(timestep, **self._species_parameters)
        x_name = self._components[0]
        y_name = self._components[1]
        x, x_md = data[x_name]
        y, y_md = data[y_name]
        x_units = x_md['units']
        y_units = y_md['units']
        if 'q' in self._components:
            q, q_md = data[self._components[2]]
            q_units = q_md['units']
        particle_plot(
            x, y, q, x_name=x_name, y_name=y_name, x_units=x_units,
            y_units=y_units, q_units=q_units, subplot_spec=subplot_spec,
            fig=fig, **self._plot_parameters)
