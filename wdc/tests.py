import unittest
from unittest.mock import MagicMock, patch
import requests
from DCO import AxisSubset, DCO
from DBC import DBC

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

class TestDCO(unittest.TestCase):
    def setUp(self):
        # Create a MagicMock to simulate database behavior
        self.mock_dbc = MagicMock()
        # Initialize the DCO object with the mocked database
        self.dco = DCO(self.mock_dbc)
    
    def test_basic_query(self):
        expected_query="for $c in (AverageChloroColorScaled) return 1"
        self.dco._DCO__variable="AverageChloroColorScaled"
        actual_query=self.dco.basic_query()
        self.assertEqual(actual_query, expected_query)

    def test_select(self):
        # Test the select method with a variable and datacube list
        result = self.dco.select("variable", ["datacube1", "datacube2"])
        # Assert that the returned object is still the DCO instance
        self.assertIs(result, self.dco)
        # Check that the internal variable and query data are correct
        self.assertEqual(self.dco._DCO__variable, "variable")
        self.assertEqual(self.dco._DCO__for_queries, ["variable in (datacube1, datacube2)"])

    def test_where_success(self):
        # Test the where method when the selection is valid
        self.dco.select("$v", ["datacube1"])
        self.dco.where("$v > 10")
        # Verify that the internal where query matches the expected condition
        self.assertEqual(self.dco._DCO__where_query, "$v > 10")

    def test_where_fail(self):
        # Check that a ValueError is raised if where is used without a valid selection
        with self.assertRaises(ValueError):
            self.dco.where("$variable > 10")

    def test_subset_success(self):
        # Test the subset method when a valid variable is selected
        self.dco.select("$v", ["datacube1"])
        self.dco.subset("$v", [AxisSubset('ansi', '2014-11', '2015-5')])
        # Verify that the subset query is formed correctly
        self.assertEqual(self.dco._DCO__subset_query, '$v[ansi("2014-11":"2015-5")]')

    def test_subset_fail(self):
        # Ensure that a ValueError is raised when trying to subset an invalid variable
        self.dco.select("$v", ["datacube1"])
        with self.assertRaises(ValueError):
            self.dco.subset("$c", [AxisSubset('ansi', '2014-11', '2015-5')])

    def test_construct_gradient_image(self):
        # Mock the database query execution
        self.dco.select("$c", ["AvgLandTemp"])

        # Set the expected query string
        expected_query = """
            coverage myCoverage over
                $p x(0:200),
                $q y(0:200)
            values $p + $q
        """

        # Mock the execute_query method to return the expected query string
        self.dco._DCO__dbc.execute_query.return_value = expected_query

        # Call the method under test
        query = self.dco.construct_gradient_image(variable="$c")
        
        # Assert that the generated query matches the expected query
        self.assertEqual(query.strip(), expected_query.strip())

    def test_transform_to_1d(self):
        # Mock the database query execution to return a byte string of numeric values
        self.mock_dbc.execute_query.return_value = b"2.834646,4.488189,11.10236,20.19685,21.02362,21.29921,25.98425,24.33071,22.12598,16.06299,8.897637,2.283465"
        
        # Set up the selection and axis subsets for the transformation
        self.dco.select("$c", ["AvgLandTemp"])
        axis_subsets = [
            AxisSubset('ansi', '2014-01', '2014-12'),
            AxisSubset('Lat', 53.08),
            AxisSubset('Long', 8.80)
        ]
        
        # Call the transform_to_1d method with the variable and axis subsets
        result = self.dco.transform_to_1d(variable="$c", axis_subsets=axis_subsets)
        
        # Decode the bytes to a UTF-8 string for comparison
        result = result.decode('utf-8')
        
        # Assert that the result matches the expected string
        self.assertEqual(result, "2.834646,4.488189,11.10236,20.19685,21.02362,21.29921,25.98425,24.33071,22.12598,16.06299,8.897637,2.283465")
        
        # Ensure the database query was called exactly once
        self.mock_dbc.execute_query.assert_called_once()

    def test_celsius_to_kelvin(self):
        # Mock the database query execution to return a byte string of numeric values
        self.mock_dbc.execute_query.return_value = b"1.732283,2.283465,10.55118,13.85827,17.99213,19.64567,23.77953,18.54331"
        
        # Set up the selection and axis subsets for temperature conversion
        self.dco.select("$c", ["AvgLandTemp"])
        axis_subsets = [
            AxisSubset('ansi', '2014-01', '2014-08'),
            AxisSubset('Lat', 54.08),
            AxisSubset('Long', 8.80)
        ]
        
        # Call the transform_to_1d method with the variable and axis subsets
        result = self.dco.transform_to_1d(variable="$c", axis_subsets=axis_subsets)
        
        # Decode the bytes to a UTF-8 string for comparison
        result = result.decode('utf-8')
        
        # Assert that the result matches the expected string
        self.assertEqual(result, "1.732283,2.283465,10.55118,13.85827,17.99213,19.64567,23.77953,18.54331")
        
        # Ensure the database query was called exactly once
        self.mock_dbc.execute_query.assert_called_once()

    def test_clip_with_polygon(self):
        # Mock the database query execution
        self.dco.select("$c", ["AvgLandTemp"])

        # Set the expected query string
        expected_query = '''
        for c in (AvgLandTemp)
        return encode(
                clip(c, POLYGON((-12.3829 132.0117, -33.4314 120.4102, -18.8127 148.5352, -22.7559 118.4766, -36.3151 143.7891)))
                , "image/png", "{{\"nodata\": [0]}}")'''
                

        # Mock the execute_query method to return the expected query string
        self.dco._DCO__dbc.execute_query.return_value = expected_query

        # Call the method under test
        query = self.dco.clip_with_polygon(variable="$c", polygon_coords=[(-12.3829, 132.0117), (-33.4314, 120.4102), (-18.8127, 148.5352), (-22.7559, 118.4766), (-36.3151, 143.7891)])

        # Assert that the generated query matches the expected query
        self.assertEqual(query.strip(), expected_query.strip())

    def test_greater_than_query(self):
        # Mock the database query execution to return a byte string result
        self.mock_dbc.execute_query.return_value = b"7"
        
        # Set up the selection and axis subsets for the threshold comparison
        self.dco.select("$c", ["AvgLandTemp"])
        axis_subsets = [
            AxisSubset('ansi', '2014-01', '2014-12'),
            AxisSubset('Lat', 53.08),
            AxisSubset('Long', 8.80)
        ]
        threshold = 15
        
        # Call the greater_than_query method with the variable, axis subsets, and threshold value
        result = self.dco.greater_than_query(variable="$c", axis_subsets=axis_subsets, value=threshold)
        
        # Decode the bytes to a UTF-8 string for comparison
        result = result.decode('utf-8')
        
        # Assert that the result matches the expected string
        self.assertEqual(result, "7")
        
        # Ensure the database query was called exactly once
        self.mock_dbc.execute_query.assert_called_once()

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
    unittest.main(verbosity=2)
