import requests
from owslib.wcs import WebCoverageService
from owslib.wcs import wcs201

class DBC:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.wcs = WebCoverageService(self.endpoint, version='2.0.1')

    def execute_query(self, query):
        '''
            Method to execute WCPS query
        
            Arguments:
                self: self@DBC
                query: the query given by the user
        '''
        try:
            response = requests.post(self.endpoint, data={'query': query}, verify=True)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

    def get_coverages(self):
        try:
            result = ""
            i = 1
            for coverage in self.wcs.contents.keys():
                result += f"{i} - {coverage}\n"
                i += 1

            return result
        except Exception as e:
            print(f"Error: {e}")
    
    def get_subset_coverage(self, coverage_id:str, subsets:list, encode=None):
        '''
            Method that returns an encoded subset coverage with defined subsets 

            Arguments:
                self: self@DBC
                coverage_id (str): coverage id 
                subsets (list): list of coverage subsets
                encode (str):the result format needed by user
        '''
        request_url=self.endpoint+ "&REQUEST=GetCoverage"
        request_url+=f"&COVERAGEID={coverage_id}"
        for subset in subsets:
            request_url+=f"&SUBSET={subset}"
        # if econding is specified modify the url
        if not encode is None:
            request_url+=f"&FORMAT={encode}"
        response=requests.get(request_url, verify=False)
        return response
    
    def describe_coverage(self, coverage_id):
        '''
            Method that returns XML-encoded description of a specific coverage
    
            Arguments:
                self: self@DBC
                coverage_id: coverage id 
        '''
        try:
            coverage = self.wcs.contents[f"{coverage_id}"]
            result = {
                "axis_labels": coverage.grid.axislabels,
                "dimension": coverage.grid.dimension,
                "low_limits": coverage.grid.lowlimits,
                "high_limits": coverage.grid.highlimits
            }
            return result
        except Exception as e:
            print(f"Error: {e}")
    
    def connection(self):
        '''
            Tests the connection with the server and provides the status code in case of the failure

            Arguments:
                self: self@DBC
        '''
        try:                      
            response=requests.get(self.endpoint)
            if response.status_code==200:
                print(f"successful connection")
            else:
                print(f"connection failed: {response.status_code}")
                raise requests.RequestException(f"connection failed: {response.status_code}")
            return response
        except requests.RequestException as e:
            print(f"connection failed: {e}")
            raise 

    def get_capabilities(self):
        ''' 
            Method that returns an XML description of service capabilities

            Arguments:
                self: self@DBC
        '''
        request_url=self.endpoint+"&request=GetCapabilities"
        response=requests.get(request_url, verify=False)
        return response