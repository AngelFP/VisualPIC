""" This module defines the `vpic` command line utility. """

import os
import argparse

from visualpic import DataContainer, MplVisualizer


def vpic():
    """
    Command-line utility for quick visualization of simulation data using
    the matplotlib backend.
    """
    # Define possible fields to plot.
    possible_fields = [
        'Ex', 'Ey', 'Ez', 'Er', 'Et', 'Bx', 'By', 'Bz', 'Br', 'Bt',
        'Jx', 'Jy', 'Jz', 'Jr', 'Jt', 'rho', 'a_mod', 'a_phase']

    # Define possible species components to show.
    possible_species_components = [
        'x', 'y', 'z', 'px', 'py', 'pz', 'q']

    # Parse input arguments from the command line.
    args = parse_arguments(possible_fields, possible_species_components)

    # Get list of fields to show.
    field_names = []
    for field in possible_fields:
        if vars(args)[field]:
            field_names.append(field)

    # Get list of components to show (currently, only none or 2 ar supported).
    component_names = []
    for component in possible_species_components:
        if vars(args)[component]:
            component_names.append(component)

    # Get absolute path to simulation folder.
    abs_path = os.path.abspath(args.path)

    # Load the data.
    dc = DataContainer(args.code, abs_path)
    dc.load_data()

    # Get field objects.
    fields = []
    for name in field_names:
        fld = dc.get_field(name)
        fields.append(fld)

    # Get species object.
    if len(component_names) > 0:
        if len(component_names) != 2:
            raise ValueError('Exactly two species components should be given')
        if args.species is not None:
            species_name = args.species
        else:
            species_list = dc.get_list_of_species()
            species_name = species_list[0]
        species = dc.get_species(species_name)

    # Visualize data
    vis = MplVisualizer()
    if len(fields) > 0:
        vis.field_plot(fields, stacked=False)
    if len(component_names) > 0:
        vis.particle_plot(species, x=component_names[0], y=component_names[1])
    vis.show()


def parse_arguments(possible_fields, possible_species_components):
    """ Parse input arguments for `vpic` """
    # Initialize parser.
    parser = argparse.ArgumentParser(
        description='Visualize a field or particle species'
    )

    # Add simulation path as optional positional argument.
    parser.add_argument(
        'path',
        type=str,
        nargs='?',
        default='.',
        help='the path to the data folder'
    )

    # Add simulation code name as optional argument.
    parser.add_argument(
        '-c',
        '--code',
        default='openpmd',
        help='code name for the data format (openpmd, osiris, or hipace)'
    )

    # Add species name as optional argument.
    parser.add_argument(
        '-s',
        '--species',
        help='name of the particle species to visualize'
    )

    # Add possible fields and species components as optional arguments.
    for field in possible_fields:
        parser.add_argument('-' + field, action='store_true')
    for component in possible_species_components:
        parser.add_argument('-' + component, action='store_true')

    return parser.parse_args()
