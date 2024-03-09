import scipy.constants as ct
from visualpic import DataContainer


# Intensity
def calculate_intensity(data_list, sim_geometry, sim_params):
    """Recipe to calculate intensity as a derived field."""
    if sim_geometry == "1d":
        Ez = data_list[0]
        E2 = Ez**2
    elif sim_geometry == "2dcartesian":
        Ez, Ex = data_list
        E2 = Ez**2 + Ex**2
    elif sim_geometry == "3dcartesian":
        Ez, Ex, Ey = data_list
        E2 = Ez**2 + Ex**2 + Ey**2
    elif sim_geometry == "cylindrical":
        raise NotImplementedError
    elif sim_geometry == "thetaMode":
        Ez, Er, Et = data_list
        E2 = Ez**2 + Er**2 + Et**2
    return ct.c * ct.epsilon_0 / 2 * E2


intensity = {
    "name": "I",
    "units": "W/m^2",
    "requirements": {
        "1d": ["Ez"],
        "2dcartesian": ["Ez", "Ex"],
        "3dcartesian": ["Ez", "Ex", "Ey"],
        "cylindrical": ["Ez", "Er"],
        "thetaMode": ["Ez", "Er", "Et"],
    },
    "recipe": calculate_intensity,
}


def test_data_container():
    """Test basic functionality of the DataContainer using sample data."""
    data_path = "./test_data/example-3d/hdf5"
    diags = DataContainer("openpmd", data_path)
    diags.load_data()
    diags.add_derived_field(intensity)

    available_fields = diags.get_list_of_fields()
    available_species = diags.get_list_of_species()
    assert set(["Ex", "Ey", "Ez", "rho", "I"]).issubset(available_fields)
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
            assert set(["q", "m", "x", "y", "z", "px", "py", "pz", "w"]).issubset(comps)
            sp_data = species.get_data(
                time_step=it, components_list=comps, data_units="SI", time_units="SI"
            )
            sp_data = species.get_data(it)


if __name__ == "__main__":
    test_data_container()
