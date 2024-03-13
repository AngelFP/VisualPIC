import numpy as np

from visualpic import DataContainer
from visualpic.analysis.laser_analysis import LaserAnalysis


def test_laser_analysis():
    """Test laser analysis in 3D and thetaMode geometry."""
    data_paths = [
        "./test_data/example-3d/hdf5",
        "./test_data/example-thetaMode/hdf5",
    ]
    for path in data_paths:
        diags = DataContainer(path)
        la = LaserAnalysis(diags)
        env = la.get_envelope(field="E")
        env_amp = la.get_envelope_amplitude(field="E")
        env_real = la.get_envelope_real(field="E")
        env_imag = la.get_envelope_imag(field="E")
        env_data = env.get_data(iteration=env.iterations[0])
        env_data_amp = env_amp.get_data(iteration=env.iterations[0])
        env_data_real = env_real.get_data(iteration=env.iterations[0])
        env_data_imag = env_imag.get_data(iteration=env.iterations[0])
        assert env_data.array.dtype == np.dtype(np.complex128)
        np.testing.assert_array_equal(np.abs(env_data), env_data_amp)
        np.testing.assert_array_equal(np.real(env_data), env_data_real)
        np.testing.assert_array_equal(np.imag(env_data), env_data_imag)


if __name__ == "__main__":
    test_laser_analysis()
