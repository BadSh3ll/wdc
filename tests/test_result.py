import unittest
from wdc.DCO import AxisSubset, DCO
from wdc.DBC import DBC

class TestActualResults(unittest.TestCase):
    def setUp(self):
        dbc = DBC("https://ows.rasdaman.org/rasdaman/ows")
        self.dco = DCO(dbc)
    def test_aggregate_min(self):
        self.dco.select("$c", ["AvgLandTemp"])
        self.dco.subset(variable="$c", 
                      axis_subsets=[AxisSubset('ansi', '2013-07', '2015-04'),
                                    AxisSubset('Lat', 54.08),
                                    AxisSubset('Long', 8.80)])

        min_res = self.dco.min().execute()
        self.assertEqual(min_res, b'1.4566929')
        
    def test_aggregate_max(self):
        self.dco.select("$c", ["AvgLandTemp"])
        self.dco.subset(variable="$c", 
                      axis_subsets=[AxisSubset('ansi', '2013-07', '2015-04'),
                                    AxisSubset('Lat', 54.08),
                                    AxisSubset('Long', 8.80)])

        max_res = self.dco.max().execute()
        self.assertEqual(max_res, b'23.779528')
        
    def test_aggregate_sum(self):
        self.dco.select("$c", ["AvgLandTemp"])
        self.dco.subset(variable="$c", 
                      axis_subsets=[AxisSubset('ansi', '2013-07', '2015-04'),
                                    AxisSubset('Lat', 54.08),
                                    AxisSubset('Long', 8.80)])

        sum_res = self.dco.sum().execute()
        self.assertEqual(sum_res, b'253.34645688533783')
        
    def test_aggregate_avg(self):
        self.dco.select("$c", ["AvgLandTemp"])
        self.dco.subset(variable="$c", 
                      axis_subsets=[AxisSubset('ansi', '2013-07', '2015-04'),
                                    AxisSubset('Lat', 54.08),
                                    AxisSubset('Long', 8.80)])

        mean_res = self.dco.avg().execute()
        self.assertEqual(mean_res, b'11.515748040242629')
        
    def test_aggregate_count(self):
        self.dco.select("$c", ["AvgLandTemp"])
        self.dco.subset(variable="$c", 
                    axis_subsets=[AxisSubset('ansi', '2013-07', '2015-04'),
                                AxisSubset('Lat', 54.08, 56),
                                AxisSubset('Long', 8.80, 10)])
        count_res = self.dco.count().execute()
        self.assertEqual(count_res, b'53')

if __name__ == '__main__':
    unittest.main()