import unittest

from MulensModel.mulenstime import MulensTime

def test_get_date_zeropoint_1():
    test_data = MulensTime(date_fmt="jd")
    assert test_data.zeropoint == 0.

def test_get_date_zeropoint_2():
    test_data = MulensTime(date_fmt="hjd")
    assert test_data.zeropoint == 0.

def test_get_date_zeropoint_3():
    test_data = MulensTime(date_fmt="jdprime")
    assert test_data.zeropoint == 2450000.

def test_get_date_zeropoint_4():
    test_data = MulensTime(date_fmt="hjdprime")
    assert test_data.zeropoint == 2450000.

def test_get_date_zeropoint_5():
    test_data = MulensTime(date_fmt="mjd")
    assert test_data.zeropoint == 2400000.5

def test_zeropoint_8():
    test_data1 = MulensTime(date_fmt="rjd")
    test_data2 = MulensTime(date_fmt="rhjd")
    assert test_data1.zeropoint == 2400000.
    assert test_data2.zeropoint == 2400000.

class GetDateZeropointBadInput(unittest.TestCase):
    def test_get_date_zeropoint_6(self):
        with self.assertRaises(ValueError):
            test_data = MulensTime(date_fmt="Potato")

    def test_get_date_zeropoint_7(self):
        with self.assertRaises(ValueError):
            test_data = MulensTime(date_fmt="JD")

