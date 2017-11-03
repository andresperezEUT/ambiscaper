# from scaper.ambisonics import r128stats, get_integrated_lufs
# import numpy as np
# import os
# import pytest
# from scaper.scaper_exceptions import ScaperError
# from pkg_resources import resource_filename


import numpy as np
import pytest
from scaper.ambisonics import _validate_ambisonics_order
from scaper.ambisonics import get_number_of_ambisonics_channels
from scaper.ambisonics import _validate_angle
from scaper.ambisonics import get_ambisonics_coefs
from scaper.scaper_exceptions import ScaperError


def test_validate_ambisonics_order():

    def __test_bad_ambisonics_order(order):
        pytest.raises(ScaperError, _validate_ambisonics_order,
                      order)

    bad_order_values = [-1, 1.5, '1']
    for bov in bad_order_values:
        __test_bad_ambisonics_order(bov)

def test_get_number_of_ambisonics_channels():

    # some known values
    orders = [0,1,2,3,4,5]
    numchannels = [1,4,9,16,25,36]
    for i,j in enumerate(orders):
        assert numchannels[i] == get_number_of_ambisonics_channels(orders[i])


def test_validate_angle():

    def __test_bad_angle(angle):
        pytest.raises(ScaperError,_validate_angle,angle)

    # not a number
    bad_angle_values = ['1', None]
    for bav in bad_angle_values:
        __test_bad_angle(bav)


def test_get_ambisonics_coefs():

    order = 1

    # X axis
    azimuth = 0
    elevation = 0
    coefs = np.array([1,0,0,1])
    assert np.allclose(coefs,get_ambisonics_coefs(azimuth,elevation,order))

    azimuth = np.pi
    coefs = np.array([1, 0, 0, -1])
    assert np.allclose(coefs, get_ambisonics_coefs(azimuth, elevation, order))

    # Y axis
    azimuth = np.pi/2
    elevation = 0
    coefs = np.array([1,1,0,0])
    assert np.allclose(coefs,get_ambisonics_coefs(azimuth,elevation,order))

    azimuth = -np.pi / 2
    coefs = np.array([1, -1, 0, 0])
    assert np.allclose(coefs, get_ambisonics_coefs(azimuth, elevation, order))

    # Z axis
    azimuth = np.pi/2
    elevation = np.pi/2
    coefs = np.array([1,0,1,0])
    assert np.allclose(coefs,get_ambisonics_coefs(azimuth,elevation,order))

    elevation = -np.pi / 2
    coefs = np.array([1, 0, -1, 0])
    assert np.allclose(coefs, get_ambisonics_coefs(azimuth, elevation, order))

    order = 2

    # X azis
    azimuth = 0
    elevation = 0
    coefs = np.array([1, 0,0,1, 0,0,-0.5,0,0.866025])
    assert np.allclose(coefs, get_ambisonics_coefs(azimuth, elevation, order))

    azimuth = np.pi
    coefs = np.array([1, 0,0,-1, 0,0,-0.5,0,0.866025])
    assert np.allclose(coefs, get_ambisonics_coefs(azimuth, elevation, order))

    # Y axis
    azimuth = np.pi/2
    elevation = 0
    coefs = np.array([1,1,0,0, 0,0,-0.5,0,-0.866025])
    assert np.allclose(coefs,get_ambisonics_coefs(azimuth,elevation,order))

    azimuth = -np.pi / 2
    coefs = np.array([1,-1,0,0, 0,0,-0.5,0,-0.866025])
    assert np.allclose(coefs, get_ambisonics_coefs(azimuth, elevation, order))

    # Z axis
    azimuth = np.pi/2
    elevation = np.pi/2
    coefs = np.array([1,0,1,0, 0,0,1,0,0])
    assert np.allclose(coefs,get_ambisonics_coefs(azimuth,elevation,order))

    elevation = -np.pi / 2
    coefs = np.array([1,0,-1,0, 0,0,1,0,0])
    assert np.allclose(coefs, get_ambisonics_coefs(azimuth, elevation, order))

    order = 3

    # X azis
    azimuth = 0
    elevation = 0
    coefs = np.array([1, 0,0,1, 0,0,-0.5,0,0.866025, 0,0,0,0,-0.612372,0,0.790569])
    assert np.allclose(coefs, get_ambisonics_coefs(azimuth, elevation, order))

    azimuth = np.pi
    coefs = np.array([1, 0,0,-1, 0,0,-0.5,0,0.866025, 0,0,0,0,0.612372,0,-0.790569])
    assert np.allclose(coefs, get_ambisonics_coefs(azimuth, elevation, order))

    # Y axis
    azimuth = np.pi/2
    elevation = 0
    coefs = np.array([1,1,0,0, 0,0,-0.5,0,-0.866025, -0.790569,0,-0.612372,0,0,0,0])
    assert np.allclose(coefs,get_ambisonics_coefs(azimuth,elevation,order))

    azimuth = -np.pi / 2
    coefs = np.array([1,-1,0,0, 0,0,-0.5,0,-0.866025, 0.790569,0,0.612372,0,0,0,0])
    assert np.allclose(coefs, get_ambisonics_coefs(azimuth, elevation, order))

    # Z axis
    azimuth = np.pi/2
    elevation = np.pi/2
    coefs = np.array([1,0,1,0, 0,0,1,0,0, 0,0,0,1,0,0,0])
    assert np.allclose(coefs,get_ambisonics_coefs(azimuth,elevation,order))

    elevation = -np.pi / 2
    coefs = np.array([1,0,-1,0, 0,0,1,0,0,0,0,0,-1,0,0,0])
    assert np.allclose(coefs, get_ambisonics_coefs(azimuth, elevation, order))


    # random positions - tolerance set to 1e-6, probably enough for practical applications
    order = 3

    azimuth = 3.810994
    elevation = 1.279957
    coefs = np.array([1,-0.177937,0.958003,-0.224873,0.069305,-0.295253,0.876656,-0.373134,0.016373,-0.016886,0.148462,-0.391055,0.761063,-0.494206,0.035074,0.007896])
    assert np.allclose(coefs, get_ambisonics_coefs(azimuth, elevation, order),atol=1e-6)

    azimuth = 6.062336
    elevation = 0.794509
    coefs = np.array([1.,-0.153480,0.713520,0.683618,-0.181729,-0.189678,0.263666,0.844851,0.384322,-0.167255,-0.289945,-0.145261,-0.162128,0.647013,0.613178,0.214377])
    assert np.allclose(coefs, get_ambisonics_coefs(azimuth, elevation, order),atol=1e-6)

    azimuth = 0.685470
    elevation = -0.236262
    coefs = np.array([1.,0.615451,-0.234070,0.752616,0.802283,-0.249517,-0.417817,-0.305127,0.162511,0.642505,-0.419912,-0.273640,0.319044,-0.334626,-0.085058,-0.339093])
    assert np.allclose(coefs, get_ambisonics_coefs(azimuth, elevation, order),atol=1e-6)

