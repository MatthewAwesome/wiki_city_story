import pandas as pd
import plotly.express as px
import numpy as np
import plotly.io as pio

# Load the data from the CSV file
data = pd.read_csv('data/wikidata_cleaned.csv')

# Size column is used to size the markers based on the population. 
data['size'] = np.sqrt(data['population'])+2

# Define a color map for the continents.
color_map = {
    'Asia': '#A033D0',  # neon pink
    'Africa': '#00FFA7',  # bright turquoise
    'Europe': '#FFA07A',  # bright orange
    'North America': '#FF00F3',  # bright purple
    'Oceania': 'lightgray',
    'South America': '#00D4FF'  # bright blue
}

# Create the plot
fig = px.scatter(data, x='year', y='population', color='continent',size='size',
                 labels={'year':'Inception Year', 'population':'Population (City)'},
                 title='How Cities Emerge over Space and Time',
                 hover_data={'city': True, 'country': True, 'continent': True, 'year': True,'population': True,'size': False}, 
                 color_discrete_map=color_map,
                 custom_data=data[['city', 'country','continent', 'year','population']])

# Update the layout
fig.update_layout(legend_title_text='<b>Continent</b>',
    plot_bgcolor='rgb(26, 26, 36)',
    paper_bgcolor='rgb(20, 20, 30)',
    title=dict(
        text='<b>Emergence of Cities over Space and Time</b>',
        y=0.9,
        x=0.5,
        xanchor='center',
        yanchor='top',
        font=dict(
            size=24,
            color='lightgray'
        )
    ),
    font=dict(
        family="Droid Sans,sans-serif", 
        color="lightgray",
    ), 
    legend=dict(
        x=0.01,  
        y=0.01,
        bgcolor='rgb(26, 26, 36)',  
        font=dict(
            size=14  
        ), 
        borderwidth=1,  # Set the border width
        bordercolor='lightgray',  # Set the border color
    )
)

# Update the axes
fig.update_xaxes(title_text='<b>Inception Year</b>', 
    tickvals=[-10000, -2000, 0, 500, 1000, 1500, 2000],
    ticktext=['10000 BC','2000 BC', '0', '500', '1000', '1500', '2000'],
    range=[-1000, 2100],
    showgrid=False,
    showline=False,
    linewidth=0.5,
    linecolor='lightgray',
    zeroline=False,
    showticklabels=True,
    tickfont=dict(
        size=16, 
        color='lightgray'
    ),
    title_font=dict(
        size=20, 
        color='lightgray'
    )
)

fig.update_yaxes(title_text='<b>Population</b>',
    type='log',
    showgrid=False,
    showline=False, 
    showticklabels=True,
    tickfont=dict(
        size=16, 
        color='lightgray'
    ),
    title_font=dict(
        size=20, 
        color='lightgray'
    ), 
    range=[1,8],
)

# Update the markers and the hover template. 
fig.update_traces(
    marker=dict(line=dict(width=0), opacity=0.86),
    hovertemplate="<br>City: %{customdata[0]}<br>Country: %{customdata[1]}<br>Continent: %{customdata[2]}<br>Year Established: %{customdata[3]}<br>Population: %{customdata[4]}<br><extra></extra>"
)

# Save as html:
pio.write_html(fig, 'index.html')                  
# Show the plot
fig.show()