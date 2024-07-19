import plotly.io as pio
import imageio
import numpy as np
import pandas as pd
import plotly.express as px
import urllib

# Prep the data: 
px.set_mapbox_access_token('pk.eyJ1IjoibWF0dGhld2VsbGlzIiwiYSI6ImNseW93cXFoaDA5eHkya3ExZzYzZDNwbWcifQ.kNGbZ1kZ6vPPPgBiYSDuMw')

# Load the data from the CSV file
data = pd.read_csv('wikidata_results.csv')

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

# Create an empty list to store the frames
frames = []

# Loop over the unique years in your data, jumping by 100 every iteration
# Loop over the unique years in your data, jumping by 100 every iteration
for year in range(-2000, 1800, 100):
    # Filter your data to include only the data up to and including that year
    year_data = data[data['year'] <= year].copy()  # Use .copy() here

    year_data['population'] = np.log1p(year_data['population'])

    year_data['radius'] = np.cbrt(year_data['population']) + 1

    # Create a density heatmap for that year's data
    fig = px.density_mapbox(year_data, lat='latitude', lon='longitude', z='population', radius=year_data['radius'],
                            center=dict(lat=20, lon=0), zoom=1.05,
                            mapbox_style="dark",
                            color_continuous_scale="Mint")

    # Remove the colorbar
    fig.update_layout(
        coloraxis_showscale=False,
        autosize=False,
        width=1008,
        height=608,
        margin=dict(l=10, r=10, b=50, t=50, pad=5)
    )

    # Add annotation for the year
    fig.add_annotation(
        x=0.5,  # Centered along the x-axis
        y=0.95,  # Near the top of the y-axis
        xref="paper",
        yref="paper",
        text="Year: " + str(year),
        showarrow=False,
        font=dict(
            size=20,
            color="white"
        ),
        bgcolor="black",
        opacity=0.8,
        xanchor="center",  # Center the text at the x position
        yanchor="top"  # Anchor the text at the top at the y position
    )

    # Save the figure as a .png image
    pio.write_image(fig, f'frame_{year}.png')

    # Append the image to your list of frames
    frames.append(imageio.imread(f'frame_{year}.png'))

for year in range(1800, max(data['year'])+1, 10):
    # Filter your data to include only the data up to and including that year
    year_data = data[data['year'] <= year].copy()  # Use .copy() here

    year_data['population'] = np.log1p(year_data['population'])

    year_data['radius'] = np.cbrt(year_data['population']) + 1

    # Create a density heatmap for that year's data
    fig = px.density_mapbox(year_data, lat='latitude', lon='longitude', z='population', radius=year_data['radius'],
                            center=dict(lat=20, lon=0), zoom=1.05,
                            mapbox_style="dark",
                            color_continuous_scale="Mint")

    # Remove the colorbar
    fig.update_layout(
        coloraxis_showscale=False,
        autosize=False,
        width=1008,
        height=608,
        margin=dict(l=10, r=10, b=50, t=50, pad=5)
    )

        # Add annotation for the year
    fig.add_annotation(
        x=0.5,  # Centered along the x-axis
        y=0.95,  # Near the top of the y-axis
        xref="paper",
        yref="paper",
        text="Year: " + str(year),
        showarrow=False,
        font=dict(
            size=20,
            color="white"
        ),
        bgcolor="black",
        opacity=0.8,
        xanchor="center",  # Center the text at the x position
        yanchor="top"  # Anchor the text at the top at the y position
    )

    # Save the figure as a .png image
    pio.write_image(fig, f'frame_{year}.png')

    # Append the image to your list of frames
    frames.append(imageio.imread(f'frame_{year}.png'))

# After the loop, use imageio to compile the frames into a video
imageio.mimsave('animation.mp4', frames, fps=10)