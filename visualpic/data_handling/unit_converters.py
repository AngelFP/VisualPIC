"""
This file is part of VisualPIC.

The module contains the definitions of the different unit converters.

Copyright 2016-2020, Angel Ferran Pousa.
License: GNU GPL-3.0.
"""

import warnings

import numpy as np
import scipy.constants as ct
import aptools.plasma_accel.general_equations as ge


length_conversion = {'km': 1e-3,
                     'mm': 1e3,
                     'um': 1e6,
                     'nm': 1e9}


time_conversion = {'ms': 1e3,
                   'us': 1e6,
                   'ns': 1e9,
                   'ps': 1e12,
                   'fs': 1e15,
                   'as': 1e18}


momentum_conversion = {'MeV/c': 1e-6 * ct.m_e*ct.c**2/ct.e,
                       'GeV/c': 1e-9 * ct.m_e*ct.c**2/ct.e}


angle_conversion = {'mrad': 1e3,
                    'urad': 1e6}


charge_conversion = {'nC': 1e9,
                     'pC': 1e12,
                     'fC': 1e15}


efield_conversion = {'GV/m': 1e-9,
                     'MV/m': 1e-6,
                     'T': 1/ct.c}


bfield_conversion = {'MT': 1e-6,
                     'V/m': ct.c,
                     'MV/m': ct.c * 1e-6,
                     'GV/m': ct.c * 1e-9}


efieldgradient_conversion = {'GV/m^2': 1e-9,
                             'T/m': 1/ct.c,
                             'MT/m': 1/ct.c * 1e-6}


bfieldgradient_conversion = {'MT/m': 1e-6,
                             'V/m^2': ct.c,
                             'MV/m^2': ct.c * 1e-6,
                             'GV/m^2': ct.c * 1e-9}


intensity_conversion = {'W/cm^2': 1e-4}


potential_conversion = {'m_e*c^2/e': 1 / ((ct.m_e * ct.c**2) / ct.e),
                        'kV': 1e-3,
                        'MV': 1e-6}


class UnitConverter():
    def __init__(self):
        """ Initialize unit converter. """
        # For convenience, due to their common use, the momentum units 'm_e*c'
        # are also considered SI units.
        self.conversion_factors = {'m': length_conversion,
                                   's': time_conversion,
                                   'rad': angle_conversion,
                                   'C': charge_conversion,
                                   'V/m': efield_conversion,
                                   'T': bfield_conversion,
                                   'V/m^2': efieldgradient_conversion,
                                   'T/m': bfieldgradient_conversion,
                                   'm_e*c': momentum_conversion,
                                   'W/m^2': intensity_conversion,
                                   'V': potential_conversion}

        self.si_units = list(self.conversion_factors.keys())

    def convert_field_units(self, field_data, field_md,
                            target_field_units=None, target_axes_units=None,
                            axes_to_convert=None, target_time_units=None):
        convert_field = target_field_units is not None
        # Dimmensionless fields will not be converted.
        if convert_field and field_md['field']['units'] == '':
            convert_field = False
            warnings.warn('Field is dimmensionless. '
                          'No field unit conversion will be performed.')
        convert_axes = target_axes_units is not None
        convert_time = target_time_units is not None

        if convert_axes:
            field_axes = field_md['field']['axis_labels']
            # If no particular axes are specified, assume all.
            if axes_to_convert is None:
                axes_to_convert = field_axes
            # It units are not a list, assume they apply to all axes.
            if not isinstance(target_axes_units, list):
                target_axes_units = [target_axes_units] * len(axes_to_convert)
            # Check that length of axes to convert and units match.
            if len(target_axes_units) != len(axes_to_convert):
                raise ValueError("Length of 'target_axes_units' and "
                                 "'axes_to_convert' do not match")

        # convert to SI units the desired data (field and/or axis and/or time)
        if convert_field or convert_axes or convert_time:
            field_data, field_md = self.convert_field_to_si_units(
                field_data, field_md, convert_field, convert_axes,
                axes_to_convert, convert_time)

        # convert field data to desired units
        if convert_field and (target_field_units != 'SI' and
                              target_field_units not in self.si_units):
            field_units = field_md['field']['units']
            field_data = self.convert_data(field_data, field_units,
                                           target_field_units)
            field_md['field']['units'] = target_field_units

        # convert axes data to desired units
        if convert_axes:
            for axis, target_units in zip(axes_to_convert, target_axes_units):
                if target_units != 'SI' and target_units not in self.si_units:
                    axis_md = field_md['axis'][axis]
                    axis_units = axis_md['units']
                    for data in ['array', 'spacing', 'min', 'max']:
                        if data in axis_md:
                            axis_md[data] = self.convert_data(
                                axis_md[data], axis_units, target_units)
                    axis_md['units'] = target_units

        # convert time data to desired units
        if convert_time and (target_time_units != 'SI' and
                             target_time_units not in self.si_units):
            time_units = field_md['time']['units']
            time_value = field_md['time']['value']
            time_value = self.convert_data(time_value, time_units,
                                           target_time_units)
            field_md['time']['value'] = time_value
            field_md['time']['units'] = target_time_units

        return field_data, field_md

    def convert_particle_data_units(self, data_dict, target_data_units=None,
                                    target_time_units=None):
        for var_name, var_items in data_dict.items():
            var_data, var_md = var_items
            # Convert data units
            if target_data_units is not None:
                var_target_units = target_data_units[var_name]
                if var_target_units is not None:
                    var_units = var_md['units']
                    # convert to SI
                    if var_units not in self.si_units:
                        var_data, var_units = self.convert_data_to_si(
                            var_data, var_units, var_md)
                        var_md['units'] = var_units
                    # convert to desired units
                    if (var_target_units != 'SI' and
                            var_target_units not in self.si_units):
                        var_data = self.convert_data(var_data, var_units,
                                                     var_target_units)
                        var_md['units'] = var_target_units
                    data_dict[var_name] = (var_data, var_md)
            # Convert time units
            if target_time_units is not None:
                time_units = var_md['time']['units']
                time_value = var_md['time']['value']
                # Convert to SI
                if time_units not in self.si_units:
                    time_value, time_units = self.convert_data_to_si(
                        time_value, time_units)
                    var_md['time']['units'] = time_units
                # convert to desired units
                if (target_time_units != 'SI' and
                        target_time_units not in self.si_units):
                    time_value = self.convert_data(time_value, time_units,
                                                   target_time_units)
                    var_md['time']['units'] = target_time_units
                var_md['time']['value'] = time_value
        return data_dict

    def convert_data(self, data, si_units, target_units):
        possible_units = self.get_possible_unit_conversions(si_units)
        if target_units in possible_units:
            conv_factor = self.conversion_factors[si_units][target_units]
            return data * conv_factor
        else:
            error_str = ('Not possible to convert {} to {}.'
                         ' Possible units are {}').format(
                             si_units, target_units, str(possible_units))
            raise ValueError(error_str)

    def get_possible_unit_conversions(self, si_units):
        return [*self.conversion_factors[si_units].keys()]

    def convert_field_to_si_units(self, field_data, field_md,
                                  convert_field=True, convert_axes=True,
                                  axes_to_convert=[], convert_time=True):
        if convert_field:
            field_units = field_md['field']['units']
            if field_units not in self.si_units:
                field_data, field_units = self.convert_data_to_si(
                    field_data, field_units, field_md)
                field_md['field']['units'] = field_units

        if convert_axes:
            for axis in axes_to_convert:
                axis_md = field_md['axis'][axis]
                axis_units = axis_md['units']
                if axis_units not in self.si_units:
                    for data in ['array', 'spacing', 'min', 'max']:
                        if data in axis_md:
                            axis_md[data], new_units = self.convert_data_to_si(
                                axis_md[data], axis_units, field_md)
                    field_md['axis'][axis]['units'] = new_units

        if convert_time:
            time_units = field_md['time']['units']
            time_value = field_md['time']['value']
            if time_units not in self.si_units:
                time_value, time_units = self.convert_data_to_si(
                    time_value, time_units, field_md)
                field_md['time']['value'] = time_value
                field_md['time']['units'] = time_units

        return field_data, field_md

    def convert_data_to_si(self, data, data_units, metadata=None):
        # Has to be implemented for each simulation. Returs data and
        # data_units in SI.
        raise NotImplementedError


class OpenPMDUnitConverter(UnitConverter):
    def convert_data_to_si(self, data, data_units, metadata=None):
        return data, data_units


class OsirisUnitConverter(UnitConverter):
    def __init__(self, plasma_density=None):
        self.plasma_density = plasma_density
        if plasma_density is not None:
            w_p = ge.plasma_frequency(plasma_density*1e-6)
            E_0 = ge.plasma_cold_non_relativisct_wave_breaking_field(
                plasma_density*1e-6)
            self.osiris_unit_conversion = {
                '1/\\omega_p': [1./w_p, 's'],
                'c/\\omega_p': [ct.c/w_p, 'm'],
                'm_ec\\omega_pe^{-1}': [E_0, 'V/m'],
                # 'e\\omega_p^3/c^3': [(w_p/ct.c)**3, '1/m^3'],
                'e\\omega_p^3/c^3': [ct.e * self.plasma_density, 'C/m^3'],
                'm_ec': [1., 'm_e*c']
            }
        else:
            self.osiris_unit_conversion = None
        super().__init__()

    def convert_data_to_si(self, data, data_units, metadata=None):
        if self.osiris_unit_conversion is not None:
            if data_units in self.osiris_unit_conversion:
                conv_factor, si_units = self.osiris_unit_conversion[data_units]
            elif data_units == 'e':
                n_cells = metadata['grid']['resolution']
                sim_size = metadata['grid']['size']
                cell_vol = np.prod(sim_size/n_cells)
                s_d = ge.plasma_skin_depth(self.plasma_density*1e-6)
                conv_factor = cell_vol * self.plasma_density * s_d**3 * ct.e
                si_units = 'C'
            else:
                raise ValueError('Unsupported units: {}.'.format(data_units))
            return data*conv_factor, si_units

        else:
            raise ValueError('Could not perform unit conversion.'
                             ' Plasma density value not provided.')


class HiPACEUnitConverter(UnitConverter):
    def __init__(self, plasma_density=None):
        self.plasma_density = plasma_density
        if plasma_density is not None:
            w_p = ge.plasma_frequency(plasma_density*1e-6)
            E_0 = ge.plasma_cold_non_relativisct_wave_breaking_field(
                plasma_density*1e-6)
            self.hipace_unit_conversion = {
                '1/\\omega_p': [1/w_p, 's'],
                'c/\\omega_p': [ct.c/w_p, 'm'],
                'E_0': [E_0, 'V/m'],
                'n_0': [ct.e * self.plasma_density, 'C/m^3'],
                'm_ec': [ct.m_e*ct.c, 'J*s/m']
            }
        else:
            self.hipace_unit_conversion = None
        super().__init__()

    def convert_data_to_si(self, data, data_units, metadata=None):
        if self.hipace_unit_conversion is not None:
            if data_units in self.hipace_unit_conversion:
                conv_factor, si_units = self.hipace_unit_conversion[data_units]
            elif data_units == 'qnorm':
                n_cells = metadata['grid']['resolution']
                sim_size = metadata['grid']['size']
                cell_vol = np.prod(sim_size/n_cells)
                s_d = ge.plasma_skin_depth(self.plasma_density*1e-6)
                conv_factor = cell_vol * self.plasma_density * s_d**3 * ct.e
                si_units = 'C'
            else:
                raise ValueError('Unsupported units: {}.'.format(data_units))
            return data*conv_factor, si_units

        else:
            raise ValueError('Could not perform unit conversion.'
                             ' Plasma density value not provided.')
