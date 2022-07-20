""" This module defines the `vpic3d` command line utility. """

import os
import argparse

from visualpic import DataContainer, VTKVisualizer


def vpic3d():
    """
    Command-line utility for quick visualization of simulation data using
    the VTK backend.
    """
    # Define possible fields to plot.
    possible_fields = [
        'Ex', 'Ey', 'Ez', 'Er', 'Et', 'Bx', 'By', 'Bz', 'Br', 'Bt',
        'Jx', 'Jy', 'Jz', 'Jr', 'Jt', 'rho', 'a_mod', 'a_phase']

    # Parse input arguments from the command line.
    args = parse_arguments(possible_fields)

    # Get list of fields to show.
    field_names = []
    for field in possible_fields:
        if vars(args)[field]:
            field_names.append(field)

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
    species_list = []
    if args.species is not None:
        for species_name in args.species:
            species_list.append(dc.get_species(species_name))

    # Visualize data
    vis = VTKVisualizer()
    for field in fields:
        vis.add_field(field)
    for species in species_list:
        vis.add_species(species)
    vis.show()


def parse_arguments(possible_fields):
    """ Parse input arguments for `vpic3d` """
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

    # Add list of species names as optional argument.
    parser.add_argument(
        '-s',
        '--species',
        nargs='+',
        help='list of names of the particle species to visualize'
    )

    # Add possible fields as optional arguments.
    for field in possible_fields:
        parser.add_argument('-' + field, action='store_true')

    return parser.parse_args()
