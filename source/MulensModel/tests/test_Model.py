import numpy as np
import unittest
from astropy import units as u

from MulensModel.model import Model
from MulensModel.modelparameters import ModelParameters
from MulensModel.mulensdata import MulensData

def test_model_PSPL_1():
    """tests basic evaluation of Paczynski model"""
    t_0 = 5379.57091
    u_0 = 0.52298
    t_E = 17.94002
    times = np.array([t_0-2.5*t_E, t_0, t_0+t_E])
    data = MulensData(data_list=[times, times*0., times*0.])
    model = Model(t_0=t_0, u_0=u_0, t_E=t_E)
    model.u_0 = u_0
    model.t_E = t_E
    model.set_datasets([data])
    np.testing.assert_almost_equal(model.data_magnification, [
            np.array([1.028720763, 2.10290259, 1.26317278])], 
            err_msg="PSPL model returns wrong values")

def test_model_init_1():
    """tests if basic parameters of Model.__init__() are properly passed"""
    t_0 = 5432.10987
    u_0 = 0.001
    t_E = 123.456
    rho = 0.0123
    m = Model(t_0=t_0, u_0=u_0, t_E=t_E, rho=rho)
    np.testing.assert_almost_equal(m.t_0, t_0, err_msg='t_0 not set properly')
    np.testing.assert_almost_equal(m.u_0, u_0, err_msg='u_0 not set properly')
    np.testing.assert_almost_equal(m.t_E, t_E, err_msg='t_E not set properly')
    np.testing.assert_almost_equal(m.rho, rho, err_msg='rho not set properly')

class TestModel(unittest.TestCase):
    def test_negative_t_E(self):
        with self.assertRaises(ValueError):
            m = Model(t_E=-100.)

def test_model_parallax_definition():
    model_1 = Model()
    model_1.pi_E = (0.1, 0.2)
    assert model_1.pi_E_N == 0.1
    assert model_1.pi_E_E == 0.2

    model_2 = Model()
    model_2.pi_E_N = 0.3
    model_2.pi_E_E = 0.4
    assert model_2.pi_E_N == 0.3
    assert model_2.pi_E_E == 0.4

    model_3 = Model(pi_E=(0.5, 0.6))
    assert model_3.pi_E_N == 0.5
    assert model_3.pi_E_E == 0.6

    model_4 = Model(pi_E_N=0.7, pi_E_E=0.8)
    assert model_4.pi_E_N == 0.7
    assert model_4.pi_E_E == 0.8

def test_coords_transformation():
    """this was tested using http://ned.ipac.caltech.edu/forms/calculator.html"""
    coords = "17:54:32.1 -30:12:34.0"
    model = Model(coords=coords)

    np.testing.assert_almost_equal(model.galactic_l.value, 359.90100049-360., decimal=4)
    np.testing.assert_almost_equal(model.galactic_b.value, -2.31694073, decimal=3)

    np.testing.assert_almost_equal(model.ecliptic_lon.value, 268.81102051, decimal=1)
    np.testing.assert_almost_equal(model.ecliptic_lat.value, -6.77579203, decimal=2)


def test_init_parameters():
    """are parameters properly passed between Model and ModelParameters?"""
    t_0 = 6141.593
    u_0 = 0.5425
    t_E = 62.63*u.day
    params = ModelParameters(t_0=t_0, u_0=u_0, t_E=t_E)
    model = Model(parameters=params)
    np.testing.assert_almost_equal(model.t_0, t_0)
    np.testing.assert_almost_equal(model.u_0, u_0)
    np.testing.assert_almost_equal(model.t_E, t_E.value)

def test_BLPS_01():
    """simple binary lens with point source"""
    params = ModelParameters(t_0=6141.593, u_0=0.5425, t_E=62.63*u.day, alpha=49.58*u.deg, s=1.3500, q=0.00578)
    model = Model(parameters=params)
    t = np.array([6112.5])
    data = MulensData(data_list=[t, t*0.+16., t*0.+0.01])
    model.set_datasets([data])
    m = model.data_magnification[0][0]
    np.testing.assert_almost_equal(m, 4.691830781584699) # This value comes from early version of this code.
    # np.testing.assert_almost_equal(m, 4.710563917) # This value comes from Andy's getbinp().
   
