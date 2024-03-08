from visualpic import DataContainer


def test_data_container():
    """Test basic functionality of the DataContainer using sample data."""
    data_path = "./test_data/example-3d/hdf5"
    diags = DataContainer("openpmd", data_path)
    diags.load_data()
    available_fields = diags.get_list_of_fields()
    available_species = diags.get_list_of_species()
    assert available_fields == ["Ex", "Ey", "Ez", "rho", "I", "A", "a"]
    assert available_species == ["electrons"]
    assert diags.get_list_of_species(required_data=["x"]) == ["electrons"]
    assert diags.get_list_of_species(required_data=["magic"]) == []
    for f_name in available_fields:
        field = diags.get_field(f_name)
        assert field.get_geometry() == "3dcartesian"
        its = field.timesteps
        for it in its:
            fld_data, md = field.get_data(time_step=it)
    for sp in available_species:
        species = diags.get_species(sp)
        for it in species.timesteps:
            comps = species.get_list_of_available_components()
            assert comps == ["q", "m", "x", "y", "z", "px", "py", "pz", "w", "x_prime"]
            sp_data, md = species.get_data(it)


if __name__ == "__main__":
    test_data_container()
