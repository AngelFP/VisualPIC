"""
This is a simple example showing how to visualize the 3D fields in a
simulation. In this case, the normalized vector potential 'a' and the plasma
density 'rho'.

The sample data can be downloaded from:
'https://github.com/openPMD/openPMD-example-datasets'.

"""

import visualpic as vp

# Start by loading the simulation data into a data container
sim_folder_path = '/your/path/to/example-thetaMode/hdf5/'
sim_code = 'openPMD'
dc = vp.DataContainer(sim_code, sim_folder_path)
dc.load_data()

# A list of all available fields in the can be displayed
print(dc.get_list_of_fields())

# Get the fields to be visualized
rho = dc.get_field('rho')
a = dc.get_field('a')

# Create visualizer and add the desired fields
vis = vp.VTKVisualizer()
vis.add_field(rho)
vis.add_field(a)

# Start visualization
vis.show()
