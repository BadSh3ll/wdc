import unittest
import requests
from wdc.DCO import DCO
from wdc.DBC import DBC

class TestDBC(unittest.TestCase):
    def setUp(self):
        self.dbc=DBC("https://ows.rasdaman.org/rasdaman/ows")
        self.dco=DCO(self.dbc)
    
    def test_successful_connection(self):
        #tests the successful connection to the server
        response=self.dbc.connection()
        self.assertEqual(response.status_code, 200)

    def test_invalid_connection(self):
        #tests error handling for invalid url
        invalid="https://os.rasdamn.org/rasdamn/ows"
        self.dbc=DBC(invalid)
        with self.assertRaises(requests.RequestException):
            self.dbc.connection()

    def test_execute_query_failure(self):
        #tests error handling for invalid query
        invalid_query='notaquery'
        response=self.dbc.execute_query(invalid_query)
        self.assertIsNone(response)

    def test_execute_query_success(self):
        #tests successful query
        query='for $c in (AvgLandTemp) return $c[Lat(27.09), Long(21.02), ansi("2010-11")]'
        response=self.dbc.execute_query(query)
        self.assertIsNotNone(response)
    
    def test_get_capabilites_output(self):
        request=self.dbc
        response=request.get_capabilities()
        self.assertEqual(response.status_code, 200, "error get_capabilities") 

    def test_describe_coverage_output(self):
        request=self.dbc
        coverage="S2_L2A_32631_B08_10m"
        response=request.describe_coverage(coverage)
        self.assertEqual(response.status_code, 200, "error in describe_coverage")

    def test_get_subset_coverage_output(self):
        request=self.dbc
        coverage="S2_L2A_32631_B08_10m"
        subsets=["ansi(\"2021-04-06\")", "E(670000, 730000)", "N(4990200,5015220)"]
        response=request.get_subset_coverage(coverage, subsets, "jpeg")
        self.assertEqual(response.status_code, 200, "error in get_subset_coverage") 

if __name__ == '__main__':
    unittest.main()