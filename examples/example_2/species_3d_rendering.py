"""
This is a simple example showing the basics of 3D rendering a particle species.

The sample data can be downloaded from:
'https://desycloud.desy.de/index.php/s/2BzxAr55ycP8eez'.

"""

import visualpic as vp


# Start by loading the simulation data into a data container
sim_folder_path = '/your/path/to/osiris_sample_data/MS/'
sim_code = 'Osiris'
dc = vp.DataContainer(sim_code, sim_folder_path, plasma_density=1e23)
dc.load_data()


def test_1():
    """Basic example. Only default parameters."""
    print(dc.get_list_of_species())
    witness_beam = dc.get_species('witness-beam')
    vis = vp.VTKVisualizer()
    vis.add_species(witness_beam)
    vis.show()


def test_2():
    """Scale longitudinal dimension and change species color."""
    witness_beam = dc.get_species('witness-beam')
    vis = vp.VTKVisualizer(scale_z=5)
    vis.add_species(witness_beam, color='tab:orange')
    vis.show()


def test_3():
    """Color particles according to their charge."""
    witness_beam = dc.get_species('witness-beam')
    vis = vp.VTKVisualizer(scale_z=5)
    vis.add_species(witness_beam, color_according_to='q')
    vis.show()


def test_4():
    """Scale and color particles according to their charge."""
    witness_beam = dc.get_species('witness-beam')
    vis = vp.VTKVisualizer(scale_z=5)
    vis.add_species(witness_beam, color_according_to='q',
                    scale_with_charge=True)
    vis.show()


def test_5():
    """Trim half of the particle beam and change colormap."""
    witness_beam = dc.get_species('witness-beam')
    vis = vp.VTKVisualizer(scale_z=5)
    vis.add_species(witness_beam, xtrim=[-1, 0], color_according_to='q',
                    cmap='inferno_r', scale_with_charge=True)
    vis.show()


def test_6():
    """
    Add the species 4 times. Each time trimming a different quadrant and with
    a different colormap
    
    """
    witness_beam = dc.get_species('witness-beam')
    vis = vp.VTKVisualizer(scale_z=5, show_cube_axes=False,
                           show_bounding_box=False)
    vis.add_species(witness_beam, xtrim=[-1, 0], ytrim=[-1, 0],
                    color_according_to='q', scale_with_charge=True,
                    cmap='viridis_r')
    vis.add_species(witness_beam, xtrim=[0, 1], ytrim=[-1, 0],
                    color_according_to='q', scale_with_charge=True,
                    cmap='inferno_r')
    vis.add_species(witness_beam, xtrim=[0, 1], ytrim=[0, 1],
                    color_according_to='q', scale_with_charge=True,
                    cmap='plasma_r')
    vis.add_species(witness_beam, xtrim=[-1, 0], ytrim=[0, 1],
                    color_according_to='q', scale_with_charge=True,
                    cmap='Oranges')
    vis.show()


test_1()
# test_2()
# test_3()
# test_4()
# test_5()
# test_6()