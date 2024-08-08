import unittest
from unittest.mock import MagicMock
from wdc.DCO import AxisSubset, DCO

class TestAxisSubset(unittest.TestCase):
    def setUp(self):
        # Placeholder for any test setup, currently not needed
        pass

    def test_axis_subset_query_three_params(self):
        # Test the AxisSubset creation with three parameters
        axis_subset = AxisSubset("operation", 1, 2, 3)
        self.assertEqual(axis_subset.query, "operation(1:2:3)")

    def test_axis_subset_query_two_str_params(self):
        # Test the AxisSubset creation with two string parameters
        axis_subset = AxisSubset("operation", "1", "2")
        self.assertEqual(axis_subset.query, 'operation("1":"2")')

    def test_axis_subset_query_one_str_param(self):
        # Test the AxisSubset creation with a single string parameter
        axis_subset = AxisSubset("operation", "1")
        self.assertEqual(axis_subset.query, 'operation("1")')
        
    def test_axis_subset_of_dco(self):
        dco = DCO(MagicMock())
        dco.select("$c", ["AvgLandTemp"])
        dco.subset(variable="$c", 
                      axis_subsets=[AxisSubset('ansi', '2013-08'),
                                    AxisSubset('Lat', 25, 90),
                                    AxisSubset('Long', -30, 55)])
        self.assertEqual(dco.__dict__['_DCO__subset_query'], '$c[ansi("2013-08"), Lat(25:90), Long(-30:55)]')

if __name__ == '__main__':
    unittest.main()