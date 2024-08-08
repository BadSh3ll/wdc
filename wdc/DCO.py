from DBC import DBC
from exceptions.ErrorMessage import ErrorMessage
import requests
from typing import List

class AxisSubset:
    def __init__(self, operation: str, *values):
        # Initialize a list to hold formatted values
        formatted_values = []
        for value in values:
            # Format string values with quotes, convert others to string directly
            if isinstance(value, str):
                formatted_values.append(f'"{value}"')  # Add quotes around string values
            else:
                formatted_values.append(str(value))  # Convert non-string values to strings

        count = len(formatted_values)  # Count the number of provided values

        self.query = ""  # Initialize an empty query string

        # Raise an error if no parameters are provided
        if count < 1:
            raise ValueError(ErrorMessage.missing_paramethers)
        elif count == 1:
            # Format query for a single value
            self.query = f'{operation}({formatted_values[0]})'
        else:
            # Format query for multiple values, joining them with colons
            self.query = f'{operation}({":".join(formatted_values)})'


class DCO:
    '''
        DCO class will create the datacube object in order to manage query building
    '''

    class Format:
        '''
            Format class defines supported output formats as class constants
        '''
        png = "image/png"
        csv = "text/csv"

    
    def __init__(self, dbc: 'DBC'):
        '''
            Initialization of the datacube object 

            Arguments:
                self: self@DBC
                dbc: database connector
        '''
        self.__dbc = dbc  # Database connector
        self.__variable = ""  # The variable/coverage name to select
        self.__for_queries = []  # List of variables/coverages to include in "for" clause
        self.__subset_query = ""  # Holds subset-specific query
        self.__where_query = ""  # Holds the conditional filter expression
        self.__format_query = ""  # Specifies the desired output format
        self.__arithmetic_operation_query = ""  # Holds any arithmetic operations
        self.__custom_encode = ""  # Contains custom encoding commands if used
    
    def basic_query(self):
        '''
            Construct a basic query that returns 1 for each pixel.

            Argumenst:
                self: self@DCO
        '''
        return f"for $c in ({self.__variable}) return 1"

    def select(self, variable: str, datacubes: list) -> 'DCO':
        '''
            Select a main variable for operations

            Arguments:
                self: self@DBC
                variable (str): main variable selected for the operation
                datacubes (list): list of datacubes
        '''
        # Store the main variable name to be used in queries
        self.__variable = variable
        # Build a "for" clause from the given variable name and list of datacubes
        self.__for_queries.append(f"{variable} in ({', '.join(datacubes)})")
        return self  # Return self for chaining methods

    def where(self, expression: str) -> 'DCO':
        '''
            Define a filtering condition.

            Arguments:
                self: self@DBC
                expression (str): filtering expression
        '''
        # Find the position of the first dollar sign in the expression
        index_of_dollar = expression.find('$')
        # Ensure a variable is specified after the dollar sign
        if index_of_dollar == -1 or index_of_dollar + 1 >= len(expression):
            raise ValueError(ErrorMessage.variable_not_defined)

        # Extract the variable (e.g., $c) and verify that it's currently selected
        variable = expression[index_of_dollar:index_of_dollar + 2]
        if variable != self.__variable:
            raise ValueError(ErrorMessage.variable_not_defined)

        # Store the "where" query expression for later execution
        self.__where_query = expression
        return self

    def subset(self, variable: str, axis_subsets: List[AxisSubset]) -> 'DCO':
        '''
             Define subset conditions

             Arguments:
                self: self@DBC
                variable (str): data that will be subsetted
                axis_subsets (List[AxisSubset]): list of AxisSubset objects
        '''
        # Ensure that the specified variable matches the current selection
        if self.__variable != variable:
            raise ValueError(ErrorMessage.variable_not_defined)

        # Construct a list of subset queries from the given AxisSubset objects
        subset_queries = [str(axis_subset.query) for axis_subset in axis_subsets]
        # Combine the variable name with the subset queries to form a full query
        subset_query = f"{variable}[{', '.join(subset_queries)}]"

        # Store the subset query to be used later
        self.__subset_query = subset_query
        return self

    def set_format(self, format: str) -> 'DCO':
        '''
            Set the output format 

            Arguments:
                self: self@DBC
                format (str): desired format
        '''
        self.__format_query = format
        return self

    def custom_encode(self, custom_encode: str) -> 'DCO':
        '''
            Set a custom encoding expression

            Arguments:
                self: self@DBC
                custom_encode (str): encoding
        '''
        self.__custom_encode = custom_encode
        return self

    def max(self) -> 'DCO':
        '''
            Maximum value calculation

            Arguments:
                self: self@DBC
        '''
        # Check if any arithmetic operation is already pending
        if self.__arithmetic_operation_query:
            raise ValueError(ErrorMessage.operation_is_already_pending)
        # Set the query to calculate the maximum value
        self.__arithmetic_operation_query = "max(0)"
        return self

    def min(self) -> 'DCO':
        '''
            Minimum value calculation

            Arguments:
                self: self@DBC
        '''
        # Check if any arithmetic operation is already pending
        if self.__arithmetic_operation_query:
            raise ValueError(ErrorMessage.operation_is_already_pending)
        # Set the query to calculate the minimum value
        self.__arithmetic_operation_query = "min(0)"
        return self

    def sum(self) -> 'DCO':
        '''
            Calculate sum of values

            Arguments:
                self: self@DBC
        '''
        # Check if any arithmetic operation is already pending
        if self.__arithmetic_operation_query:
            raise ValueError(ErrorMessage.operation_is_already_pending)
        # Set the query to calculate the sum of values
        self.__arithmetic_operation_query = "sum(0)"
        return self

    def count(self) -> 'DCO':
        '''
            Count the number of cells

            Arguments:
                self: self@DBC
        '''
        # Check if any arithmetic operation is already pending
        if self.__arithmetic_operation_query:
            raise ValueError(ErrorMessage.operation_is_already_pending)
        # Set the query to count the number of data cells
        self.__arithmetic_operation_query = "cellCount(0)"
        return self

    def avg(self) -> 'DCO':
        '''
            Calculate average of values

            Arguments:
                self: self@DBC
        '''
        # Check if any arithmetic operation is already pending
        if self.__arithmetic_operation_query:
            raise ValueError(ErrorMessage.operation_is_already_pending)
        # Set the query to calculate the average of values
        self.__arithmetic_operation_query = "avg(0)"
        return self

    def transform_data(self, transformation: str) -> 'DCO':
        '''
            Transform data based on a given expression

            Arguments:
                self: self@DBC
                transformation (str): transformation expression
        '''
        # Find the first dollar sign indicating the variable in the expression
        index_of_dollar = transformation.find('$')
        # Ensure a variable name follows the dollar sign
        if index_of_dollar == -1 or index_of_dollar + 1 >= len(transformation):
            raise ValueError(ErrorMessage.variable_not_defined)

        # Extract the variable and confirm it's the same as the selected one
        variable = transformation[index_of_dollar:index_of_dollar + 2]
        if variable != self.__variable:
            raise ValueError(ErrorMessage.variable_not_defined)

        # If no subset query exists, use the transformation directly
        if self.__subset_query == "":
            self.__subset_query = transformation
        else:
            # Otherwise, replace the variable name in the transformation with the subset query
            self.__subset_query = transformation.replace(variable, self.__subset_query)

        return self

    def execute(self) -> bytes:
        '''
            Execute the constructed query and return the result

            Arguments:
                self:self@DBC
        '''
        # Raise an error if no variable has been defined
        if not self.__variable:
            raise ValueError("Variable not defined.")

        # Begin constructing the query with a "for" clause using all selected variables
        query = f"for {', '.join(self.__for_queries)}\n"

        # Append the appropriate encoding or arithmetic operation to the query
        if self.__custom_encode:
            # If custom encoding is specified, use it directly in the query
            query += f'return encode({self.__custom_encode.replace("$c", self.__subset_query)}, "{self.__format_query}")'
        elif self.__arithmetic_operation_query:
            # If an arithmetic operation is pending, replace "0" with the subset query
            query += f'return {self.__arithmetic_operation_query.replace("0", self.__subset_query)}'
        elif self.__subset_query:
            # If only a subset query exists, include it with encoding
            query += f'return encode({self.__subset_query}, "{self.__format_query}")'
        else:
            raise ValueError("No operation specified.")

        # Execute the constructed query using the DBC's execute_query method
        return self.__dbc.execute_query(query)

    def construct_gradient_image(self, variable: str) -> str:
        '''
            Construct a gradient image query

            Arguments:
                self: self@DBC
                variable: data on which the gardient image is based
        '''
        # Set the selected variable to the provided value
        self.__variable = variable

        # Use a custom coverage encoding expression to create a gradient image
        self.__custom_encode = """
            coverage myCoverage over
                $p x(0:200),
                $q y(0:200)
            values $p + $q
        """

        # Set the output format to PNG
        self.__format_query = DCO.Format.png

        # Return the constructed query
        return self.__custom_encode
    
    def transform_to_1d(self, variable: str, axis_subsets: list[AxisSubset]) -> bytes:
        '''
            Transform data to 1D

            Arguments:
                self: self@DBC
                variable (str): data which will be transformed to 1d
                axis_subsets (list[AxisSubset]): list of AxisSubset objects
        '''
        # Ensure the specified variable matches the current selection
        if self.__variable != variable:
            raise ValueError("Variable not defined.")
        
        # Construct a list of queries from the AxisSubset objects
        subset_queries = [str(axis_subset.query) for axis_subset in axis_subsets]
        # Form a full subset query by combining the variable with these queries
        self.__subset_query = f"{variable}[{', '.join(subset_queries)}]"
        
        # Set the output format to CSV and execute the query
        return self.set_format(DCO.Format.csv).execute()
    
    def transform_3d_to_2d(self, variable: str, axis_subsets: List[AxisSubset], dimension_to_collapse: str) -> bytes:
        '''
            Transform 3D data to 2D

            Arguments:
                self: self@DCO
                variable (str): data which will be transformed
                axis_subsets (List[AxisSubset]): list of AxisSubset objects
                dimension_to_collapse (str): dimension to collapse (e.g., 'x', 'y', or 'z').
        '''
        if self.__variable != variable:
            raise ValueError("Variable not defined.")
        
        # Validate the dimension to collapse
        valid_dimensions=['x', 'y', 'z']
        if dimension_to_collapse.lower() not in valid_dimensions:
            raise ValueError("Invalid dimension to collapse. Choose 'x', 'y', or 'z'.")
        dimension_index=valid_dimensions.index(dimension_to_collapse.lower())
        subset_queries = [str(axis_subset.query) for axis_subset in axis_subsets]
        combined_subset_query=''
        for i, query in enumerate(subset_queries):
            if i != dimension_index:
                combined_subset_query += query + ','
        combined_subset_query=combined_subset_query.rstrip(',')
        self.__subset_query = f"{variable}[{combined_subset_query}]"
        return self.set_format(DCO.Format.csv).execute()

    
    def celsius_to_kelvin(self, variable: str, axis_subsets: list[AxisSubset]) -> bytes:
        '''
            Convert Celsius to Kelvin

            Arguments:
                self: self@DBC
                variable (str): variable for which the conversion is performed
                axis_subsets (list[AxisSubset]): list of AxisSubset objects
        '''
        # Ensure the specified variable matches the current selection
        if self.__variable != variable:
            raise ValueError("Variable not defined.")
        
        # Build a list of subset queries from the given AxisSubset objects
        subset_queries = [str(axis_subset.query) for axis_subset in axis_subsets]
        # Form a complete subset query by combining the variable and queries
        self.__subset_query = f"{variable}[{', '.join(subset_queries)}]"
        
        # Set the format to CSV and execute the query
        return self.set_format(DCO.Format.csv).execute()
    
    def clip_with_polygon(self, variable: str, polygon_coords: List[tuple]) -> 'DCO':
        '''
            Clips data using a polygonal boundary

            Arguments:
                self: self@DBC
                variable (str): data to be clipped
                polygon_coords (List[tuple]): coordinates of the polygon vertices
        '''
        # Ensure the main variable is already selected
        if not self.__variable:
            raise ValueError(ErrorMessage.variable_not_defined)

        # Format the polygon coordinates into a string of space-separated pairs
        polygon_str = ", ".join([f"{coord[0]} {coord[1]}" for coord in polygon_coords])
        polygon_query = f"POLYGON(({polygon_str}))"

        # Construct the clip query using the variable and polygon
        clip_query = f"clip(c, {polygon_query})"

        # Add the return statement with proper encoding to the final query
        query = f"for c in ({variable})\n"
        query += f"return encode({clip_query}, \"image/png\", \"{{\\\"nodata\\\": [0]}}\")"

        # Execute the constructed query through the DBC's execute_query method
        return self.__dbc.execute_query(query)

    def greater_than_query(self, variable: str, axis_subsets: List[AxisSubset], value: float) -> bytes:
        '''
            Counts the number of data cells greater than the specified value

            Arguments:
                self: self@DBC
                variable (str): data that will be compared
                axis_subsets (List[AxisSubset]): list of AxisSubset objects
                value (float): the threshold for comparison
        '''
        # Ensure that the given variable matches the current selection
        if not self.__variable or self.__variable != variable:
            raise ValueError(f"Variable '{variable}' not selected. Use select method first.")

        # Create a list of subset queries from the provided AxisSubset objects
        subset_queries = [subset.query for subset in axis_subsets]
        # Build a complete subset query by combining the variable and queries
        subset_query = f"{variable}[{', '.join(subset_queries)}]"

        # Form the greater-than condition with the variable, subsets, and specified value
        greater_than_expression = f'{subset_query} > {value}'

        # Construct the query with a "for" clause and count operation
        query = f"for {', '.join(self.__for_queries)} return count({greater_than_expression})"

        # Execute the query via the DBC's execute_query method
        return self.__dbc.execute_query(query)
    
    def selectMultVar(self, variables: list, datacubes: list) -> 'DCO':
        '''
            Selects multiple variables for operations on datacubes

            Arguments:
                self: self@DBC
                variables (list): variables that will be selected for the operations
                datacubes (list): datacubes associated with each variable 
        '''
        self.__variables = variables
        for variable, datacube in zip(variables, datacubes):
            self.__for_queries.append(f"{variable} in ({datacube})")
        return self

    def subset_to_variables(self, variables: List[str], axis_subsets: List[AxisSubset]) -> 'DCO':
        '''
            Creates subset queries for multiple variables

            Arguments:
                self: self@DCO
                variables (List[str]): list of variable for which subset queries are created
                axis_subsets (List[AxisSubset]): list of AxisSubset objects 
        '''
        for var in variables:
            if var not in self.__variables:
                raise ValueError(ErrorMessage.variable_not_defined)
    
        subset_queries = []
        for var in variables:
            subset_query = f"{var}[{', '.join(str(axis_subset.query) for axis_subset in axis_subsets)}]"
            subset_queries.append(subset_query)
    
        self.__subset_query = ', '.join(subset_queries)
    
        return self

    def only_subset(self, axis_subsets: List[AxisSubset]) -> 'DCO':
        '''
            Specifies a subset query

            Arguments:
                self: self@DCO
                axis_subsets (List[AxisSubset]): list of AxisSubset objects
        '''
        subset_query = f"[{', '.join(str(axis_subset.query) for axis_subset in axis_subsets)}]"
        self.__subset_query = f"{subset_query}"
        
        return self


    def executeMultVar(self):
        '''
            Executes a query involving multiple variables

            Arguments:
                self: self@DCO
        '''
        if len(self.__variables) == 0:
            raise ValueError(ErrorMessage.variable_not_defined)
        
        if len(self.__for_queries) == 0:
            raise ErrorMessage.structure_not_defined
        datacubes_query = ', '.join(datacubes for datacubes in self.__for_queries)
        query = f"for {datacubes_query}\nreturn"
    
        if self.__where_query != "":
             query += f'where {self.__where_query} \n'

        if self.__custom_encode != "" and self.__format_query != "":
             query += f'\nencode({self.__custom_encode.replace(self.__variable, self.__subset_query)}, "{self.__format_query}")'
        elif self.__format_query != "":
             query += f'\nencode({self.__subset_query}, "{self.__format_query}")'
        else:
             if self.__arithmetic_operation_query != "":
                 query += f'\n{self.__arithmetic_operation_query}'
             else:
                 query += f'\n{self.__subset_query}'
                 
        return self.__dbc.execute_query(query)
    
    def calculate_difference(self):
        '''
            Calculates the difference between two variables from different coverages

            Arguments:
                self: self@DCO
        '''
        if len(self.__variables) != 2:
            raise ValueError(ErrorMessage.invalid_operation)
            
        variable1 = self.__variables[0]
        variable2 = self.__variables[1]
    
        if variable1 == variable2:
            raise ValueError(ErrorMessage.invalid_operation)
    
        self.__arithmetic_operation_query = f"{variable1}{self.__subset_query} - {variable2}{self.__subset_query}"
        
        return self

    def calculate_Sum(self):
        '''
            Calculates the sum between two variables from different coverages

            Arguments:
                self: self@DCO
        '''
        if len(self.__variables) != 2:
            raise ValueError(ErrorMessage.invalid_operation)
                
        variable1 = self.__variables[0]
        variable2 = self.__variables[1]
        
        if variable1 == variable2:
            raise ValueError(ErrorMessage.invalid_operation)
        
        self.__arithmetic_operation_query = f"{variable1}{self.__subset_query} + {variable2}{self.__subset_query}"
        return self

    def calculate_Avg(self):
        '''
            Calculates the average between two variables from different coverages

            Arguments:
                self: self@DCO
        '''
        if len(self.__variables) != 2:
            raise ValueError(ErrorMessage.invalid_operation)
                
        variable1 = self.__variables[0]
        variable2 = self.__variables[1]
        
        if variable1 == variable2:
            raise ValueError(ErrorMessage.invalid_operation)
        
        self.__arithmetic_operation_query = f"({variable1}{self.__subset_query} + {variable2}{self.__subset_query})/2"
            
        return self

    def calculate_Product(self):
        '''
            Calculates the product between two variables from different coverages

            Arguments:
                self: self@DCO
        '''
        if len(self.__variables) != 2:
          raise ValueError(ErrorMessage.invalid_operation)
                
        variable1 = self.__variables[0]
        variable2 = self.__variables[1]
        
        if variable1 == variable2:
            raise ValueError(ErrorMessage.invalid_operation)
        
        self.__arithmetic_operation_query = f"{variable1}{self.__subset_query} * {variable2}{self.__subset_query}"
            
        return self

    def calculate_Ratio(self):
        '''
            Calculates the ratio between two variables from different coverages

            Arguments:
                self: self@DCO
        '''
        if len(self.__variables) != 2:
            raise ValueError(ErrorMessage.invalid_operation)
                
        variable1 = self.__variables[0]
        variable2 = self.__variables[1]
        
        if variable1 == variable2:
            raise ValueError(ErrorMessage.invalid_operation)
        
        self.__arithmetic_operation_query = f"{variable1}{self.__subset_query} / {variable2}{self.__subset_query}"
            
        return self

    def aggregate(self, operation: str) -> 'DCO':
        '''
        Method to apply aggregation functions to your variable.
        
        Arguments:
            self: self@DCO
            operation: aggregate operation you choose (available: min, max, avg, count, sum)
        '''
        if self.arithmetic_operation_query!="":
            raise requests.RequestException(f"error: operation already pending")
        self.arithmetic_operation_query=f"{operation}(0)"
        return self
