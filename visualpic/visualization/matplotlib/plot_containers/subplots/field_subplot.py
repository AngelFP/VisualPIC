from .subplot import Subplot
from visualpic.visualization.matplotlib.plot_types import field_plot


class FieldSubplot(Subplot):
    """Class defining a field subplot.
    """

    def __init__(
            self, fields, field_units=None, axes_units=None, time_units=None,
            slice_dir=None, slice_pos=0.5, m='all', theta=0, vmin=None,
            vmax=None, cmap=None, stacked=True, cbar=True):

        # Convert necessary arguments into lists
        if not isinstance(fields, list):
            fields = [fields]
        if not isinstance(field_units, list):
            field_units = [field_units] * len(fields)
        if not isinstance(slice_pos, list):
            slice_pos = [slice_pos] * len(fields)
        if not isinstance(m, list):
            m = [m] * len(fields)
        if not isinstance(theta, list):
            theta = [theta] * len(fields)

        self._field_arguments = []
        for i in range(len(fields)):
            self._field_arguments.append(
                {
                    'field_units': field_units[i],
                    'axes_units': axes_units,
                    'time_units': time_units,
                    'slice_i': slice_pos[i],
                    'slice_dir_i': slice_dir,
                    'm': m[i],
                    'theta': theta[i]
                })
        self._plot_arguments = {
            'vmin': vmin,
            'vmax': vmax,
            'cmap': cmap,
            'cbar': cbar,
            'stacked': stacked
        }
        super().__init__(fields)

    def _make_plot(self, timestep, subplot_spec, fig):
        field_data = []
        field_name = []
        field_units = []
        for field, field_args in zip(self._datasets, self._field_arguments):
            fld_data, fld_md = field.get_data(timestep, **field_args)
            field_data.append(fld_data)
            field_name.append(field.get_name())
            field_units.append(fld_md['field']['units'])
        axis_labels = fld_md['field']['axis_labels'][::-1]
        x_units = fld_md['axis'][axis_labels[0]]['units']
        y_units = fld_md['axis'][axis_labels[1]]['units']
        x_label = '${}$ [${}$]'.format(axis_labels[0], x_units)
        y_label = '${}$ [${}$]'.format(axis_labels[1], y_units)
        x_min = fld_md['axis'][axis_labels[0]]['array'][0]
        x_max = fld_md['axis'][axis_labels[0]]['array'][-1]
        y_min = fld_md['axis'][axis_labels[1]]['array'][0]
        y_max = fld_md['axis'][axis_labels[1]]['array'][-1]
        field_plot(field_data, field_name=field_name, field_units=field_units,
                   extent=[x_min, x_max, y_min, y_max], xlabel=x_label,
                   ylabel=y_label,
                   subplot_spec=subplot_spec, fig=fig, **self._plot_arguments)
