from wdc.DBC import DBC
from wdc.DCO import DCO, AxisSubset
from matplotlib import pyplot as plt
from matplotlib import colors
import numpy as np
import netCDF4 as nc
from IPython.display import display
from PIL import Image
import io

if __name__ == "__main__":
    # Initialize the DBC object with the server URL for accessing WCPS data
    dbc = DBC("https://ows.rasdaman.org/rasdaman/ows")
    # Print out the available coverages from the data source
    print(dbc.get_coverages())  

    # Create a new DCO instance for data manipulation
    dco = DCO(dbc)

    # Select the desired variable "AvgLandTemp" and subset the data to a specific time period
    dco.select("$c", ["AvgLandTemp"]).subset(variable='$c', 
                                            axis_subsets=[AxisSubset('ansi', '2015-05')])
    # Set the output format to PNG
    dco.set_format('image/png')
    # Execute the query and retrieve the resulting image data
    output = dco.execute()
    
    # Open and display the image using the Pillow library
    img = Image.open(io.BytesIO(output))
    img.show()

    # Create another DCO instance to apply custom encoding logic
    dco2 = DCO(dbc)

    # Select the "AvgLandTemp" variable and define a custom color mapping with a switch statement
    dco2.select("$c", ["AvgLandTemp"])
    dco2.custom_encode('''
                    switch
                        case $c = 99999
                            return {red: 255; green: 255; blue: 255}
                        case 18 > $c
                            return {red: 0; green: 0; blue: 255}
                        case 23 > $c
                            return {red: 255; green: 255; blue: 0}
                        case 30 > $c
                            return {red: 255; green: 140; blue: 0}
                        default return {red: 255; green: 255; blue: 255}
                       ''')
    # Subset the data to specific latitudes, longitudes, and time periods
    dco2.subset(variable="$c", axis_subsets=[AxisSubset('ansi', '2015-05'),
                                            AxisSubset('Lat', 25, 90),
                                            AxisSubset('Long', -30, 55)])
    # Set the output format to PNG and execute the query to get the image
    dco2.set_format('image/png')
    output2 = dco2.execute()
    img2 = Image.open(io.BytesIO(output2))
    img2.show()

    # Create a third DCO instance to count data points within a given time range
    dco3 = DCO(dbc)
    dco3.select("$c", ["AvgLandTemp"])
    # Apply the count operation and subset the data based on a time and geographical range
    dco3.count().subset(variable="$c", 
                      axis_subsets=[AxisSubset('ansi', '2013-07', '2015-04'),
                                    AxisSubset('Lat', 54.08),
                                    AxisSubset('Long', 8.80)])
    # Execute the query and print the count result
    output3 = dco3.execute()
    print(output3)

    # Create a fourth DCO instance to generate a gradient image
    dco4 = DCO(dbc)
    dco4.select("$c", ["AverageChloroColor"])
    # Construct a gradient image based on the given variable
    dco4.construct_gradient_image(variable="$c")
    dco4.set_format('image/png')
    output4 = dco4.execute()
    img4 = Image.open(io.BytesIO(output4))
    img4.show() 

    # Create a fifth DCO instance and select the "AvgLandTemp" variable
    dco5 = DCO(dbc)
    dco5.select("$c", ["AvgLandTemp"])
    # Provide the relevant AxisSubset objects for temperature data
    axis_subsets = [
        AxisSubset('Lat', 54.08),
        AxisSubset('Long', 8.80),
        AxisSubset('ansi', '2014-01', '2014-08')
    ]
    # Convert temperatures from Celsius to Kelvin and decode the byte output
    output5 = dco5.celsius_to_kelvin(variable="$c", axis_subsets=axis_subsets)
    output5 = output5.decode()
    print(output5)

    # Create a sixth DCO instance to perform polygon-based clipping
    dco6 = DCO(dbc)
    dco6.select("$c", ["AvgLandTemp"])
    # Define polygon coordinates for clipping the data
    polygon_coords = [
        (-12.3829, 132.0117),
        (-33.4314, 120.4102),
        (-18.8127, 148.5352),
        (-22.7559, 118.4766),
        (-36.3151, 143.7891) 
    ]
    # Clip data using the polygon coordinates and retrieve the result as an image
    output6 = dco6.clip_with_polygon(variable="mean_summer_airtemp", polygon_coords=polygon_coords)
    img6 = Image.open(io.BytesIO(output6))
    img6.show()

    # Create a seventh DCO instance for performing a "greater than" query
    dco7 = DCO(dbc)

    # Select the "AvgLandTemp" variable and provide a set of axis subsets
    dco7.select("$c", ["AvgLandTemp"])
    axis_subsets = [
        AxisSubset('Lat', 53.08),
        AxisSubset('Long', 8.80),
        AxisSubset('ansi', '2014-01', '2014-12')   
    ]
    # Specify a threshold value and execute the greater-than query
    threshold = 15
    output7 = dco7.greater_than_query(variable="$c", axis_subsets=axis_subsets, value=threshold)
    output7 = output7.decode()
    print(output7)
