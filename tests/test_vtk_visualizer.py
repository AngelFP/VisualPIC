from visualpic import DataContainer, VTKVisualizer


def test_vtk_visualizer():
    """Make a field and particle render, and save it to file."""
    data_path = "./test_data/example-3d/hdf5"
    diags = DataContainer("openpmd", data_path)
    diags.load_data()
    vis = VTKVisualizer(use_qt=True)
    rho = diags.get_field("rho")
    elec = diags.get_species("electrons")
    vis.add_field(rho)
    vis.add_species(elec)
    vis.render_to_file(
        vis.available_time_steps[0],
        "./test_render_3d.png",
        resolution=[400, 400],
        ts_is_index=False,
    )


if __name__ == "__main__":
    test_vtk_visualizer()
