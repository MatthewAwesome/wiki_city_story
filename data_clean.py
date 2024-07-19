# A script to clean the data from the Wikidata API response.
import pandas as pd
import urllib
import pycountry
import pycountry_convert as pc


data = pd.read_csv('data/wikidata_results.csv')

# A mapping from country names to continents: 
custom_mapping = {
    'State of Palestine': 'Asia',
    'Syria': 'Asia',
    'Turkey': 'Asia',
    'Muhammad in Medina': 'Asia',
    'Umayyad Caliphate': 'Asia',
    'Rashidun Caliphate': 'Asia',
    'Russia': 'Europe',
    "People's Republic of China": 'Asia',
    'Mandatory Palestine': 'Asia',
    'Ancient Rome': 'Europe',
    'Persarmenia': 'Asia',
    'Sasanian Armenia': 'Asia',
    'South Korea': 'Asia',
    'Czech Republic': 'Europe',
    'United States of America': 'North America',
    'Ramey state': 'North America',  # Assuming "Ramey state" is unknown
    'Kingdom of England': 'Europe',
    'Republic of Ireland': 'Europe',
    'Kingdom of Denmark': 'Europe',
    'nan': 'Unknown',
    'United Arab Republic': 'Asia',
    'Israeli-occupied territories': 'Asia',
    'South Ossetia': 'Asia',
    'Holy Roman Empire': 'Europe',
    'Moldova': 'Europe',
    'São Tomé and Príncipe': 'Africa',
    'Venezuela': 'South America',
    'East Timor': 'Asia',
    'Transnistria': 'Europe',
    'Bolivia': 'South America',
    'Austria-Hungary': 'Europe',
    'Austrian Empire': 'Europe',
    'Kingdom of Hungary': 'Europe',
    'Kingdom of Romania': 'Europe',
    'First Hungarian Republic': 'Europe',
    'Socialist Republic of Romania': 'Europe',
    "Romanian People's Republic": 'Europe',
    'Russian Empire': 'Europe',
    'Taiwan': 'Asia',
    'United States Virgin Islands': 'North America',
    'The Bahamas': 'North America',
    'Iran': 'Asia',
    'Spanish Empire': 'Europe',
    'Soviet Union': 'Europe',
    'Vietnam': 'Asia',
    'North Korea': 'Asia',
    'The Gambia': 'Africa',
    'Rhodesia': 'Africa',
    'Southern Rhodesia': 'Africa',
    'Zimbabwe Rhodesia': 'Africa',
    'Confederate States': 'North America',
    'British Raj': 'Asia',
    'Tanzania': 'Africa',
    'Western Sahara': 'Africa',
    'Democratic Republic of the Congo': 'Africa',
    'Republic of the Congo': 'Africa',
    'Ivory Coast': 'Africa',
    'West Bank': 'Asia',
    'Sahrawi Arab Democratic Republic': 'Africa',
    'Golan Heights': 'Asia'
}
# Function to extract coordinates from the wiki data response:
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

def get_continent(country_name):
    try:
        if country_name in custom_mapping:
            return custom_mapping[country_name]
        country = pycountry.countries.get(name=country_name)
        if not country:
            return None
        country_alpha2 = country.alpha_2
        country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
        return continent_name
    except Exception as e:
        print(f"Error getting continent for: {country_name}")
        print(str(e))
        return None

# Apply the function to the 'date' column and invert the result
mask = ~data['date'].apply(is_url)

# Filter the DataFrame using the mask
data = data[mask]

# Create a mask for rows where 'city' matches the form of a wikidata item
mask = data['city'].str.contains('^Q\d+$', regex=True)

# Invert the mask using the '~' operator, then use it to select rows
data = data[~mask]

# We are going to make a year filed from the date field
data['year'] = data['date'].apply(extract_year)

data = data.drop_duplicates(subset='city', keep='first')

# Now we want to see if we have entries for which we have a country by not a continent, 
# we will then grab the continent associated with the country. 
mask = data['continent'].isnull() & ~data['country'].isnull()
data.loc[mask, 'continent'] = data.loc[mask, 'country'].apply(get_continent)

# And filling in the last blank: 
data.loc[data['city'] == 'Tenochtitlan', 'country'] = 'Mexico'
data.loc[data['city'] == 'Tenochtitlan', 'continent'] = 'North America'


#And do some continent merging: 

# Merge 'Eurasia' with 'Asia'
data['continent'] = data['continent'].replace('Eurasia', 'Asia')

# Merge Americas into South America
data['continent'] = data['continent'].replace('Americas', 'South America')

# Merge 'Australian continent', 'Insular Oceania', and 'Oceania' into 'Oceania'
data['continent'] = data['continent'].replace(['Australian continent', 'Insular Oceania'], 'Oceania')

# Print the count of countries associated with each continent
print(data.groupby('continent').size())

# Can we do a count of countries associated with each continent?
print(data.groupby('continent').size())

mask = data['continent'] == 'Americas'

# Print the 'country' column for these rows
print(data.loc[mask])

# Print the total number of rows: 
print(data.shape[0])
# Now lets save the data to a new CSV file
data.to_csv('wikidata_cleaned.csv', index=False)