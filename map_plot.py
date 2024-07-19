import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import plotly.express as px
import urllib
import numpy as np
import plotly.graph_objects as go

px.set_mapbox_access_token('pk.eyJ1IjoibWF0dGhld2VsbGlzIiwiYSI6ImNseW93cXFoaDA5eHkya3ExZzYzZDNwbWcifQ.kNGbZ1kZ6vPPPgBiYSDuMw')

# Load the data from the CSV file
data = pd.read_csv('data/wikidata_results.csv')

# Function to check if a string is a valid URL
def is_url(s):
    try:
        result = urllib.parse.urlparse(s)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
    
def extract_year(date_str):
    # Check if the date string is empty or just a '-'

    # Check if the year is negative
    is_negative = date_str.startswith('-')

    # And if we hvae a negative, let's remove the negative sign by slicing the string
    if is_negative:
        date_str = date_str[1:]

    # Split the string to get the year
    year_str = date_str.split('-')[0]

    # Convert the year to an integer
    year = int(year_str)

    # If the year is negative, multiply by -1
    if is_negative:
        year *= -1

    # If the year is less than -10000, set it to -10000
    if year < -10000:
        year = -10000

    return year

# Apply the function to the 'date' column and invert the result
mask = ~data['date'].apply(is_url)

# Filter the DataFrame using the mask
data = data[mask]

# We are going to make a year filed from the date field

data['year'] = data['date'].apply(extract_year)

data['population'] = np.log1p(data['population'])

data['radius'] = np.cbrt(data['population']) + 1


# Create a density heatmap
fig = px.density_mapbox(data, lat='latitude', lon='longitude', z='population', radius=data['radius'],
                        center=dict(lat=-10, lon=20), zoom=1.2,
                        mapbox_style="dark",
                        color_continuous_scale=["#000000", "#FF00FF", "#ADD8E6"], 
                        color_continuous_midpoint=data['population'].median(), 
                        animation_group='year')

# Show the plot
fig.show()
# Plot the data as a heatmap
# scatter = ax.scatter(gdf['longitude'], gdf['latitude'], c=gdf['population'], cmap='viridis')

# # Add a colorbar
# fig.colorbar(scatter, ax=ax, label='Population')

# # Show the plot
# plt.show()

# # Convert the 'date' column to datetime
# data['date'] = pd.to_datetime(data['date'])

# # Extract the year and convert BCE years to negative
# data['year'] = data['date'].apply(lambda x: -x.year if x.year > 0 else x.year)

# # Convert the DataFrame to a GeoDataFrame
# # The longitude and latitude columns are converted to a point geometry
# gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.longitude, data.latitude))

# # Sort the data by year
# gdf = gdf.sort_values('year')

# # Create a figure
# fig, ax = plt.subplots()

# # Function to update the plot for each year
# def update(year):
#     ax.clear()
#     gdf[gdf['year'] <= year].plot(ax=ax)
#     ax.set_title(f'Cities up to year {year}')

# # Create the animation
# ani = animation.FuncAnimation(fig, update, frames=range(gdf['year'].min(), gdf['year'].max() + 1), repeat=True)

# # Show the plot
# plt.show()