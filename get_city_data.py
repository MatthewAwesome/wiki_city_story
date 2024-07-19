import requests
import time
import csv

# Function to extract coordinates from the wiki data response: 
def extract_coordinates(wkt_literal):
    # Remove 'Point(' and ')' from the string and split into longitude and latitude
    try:
        point = wkt_literal.replace('Point(', '').replace(')', '').split()
        return {
            'longitude': float(point[0]),
            'latitude': float(point[1])
        }
    except:
        print(f"Error extracting coordinates from: {wkt_literal}")
        return {'longitude': None, 'latitude': None}

# function to clean the response and extract the data we care about: 
def clean_data(raw_item):
    # The coordinates are tricky, so we grab the first, .
    coordinates = extract_coordinates(raw_item['coordinates']['value'])
    return {
        'wikidata_item': raw_item['city']['value'].split('/')[-1],  # Extract the QID
        'city': raw_item['cityLabel']['value'],
        'longitude': coordinates['longitude'],
        'latitude': coordinates['latitude'],
        'date': raw_item['earliest_inception']['value'] if 'earliest_inception' in raw_item else None,
        'population': int(float(raw_item['latest_population']['value'])) if 'latest_population' in raw_item else None,
        'continent': raw_item['continentLabel']['value'] if 'continentLabel' in raw_item else None,
        'country': raw_item['countryLabel']['value'] if 'countryLabel' in raw_item else None
    }


def fetch_wikidata(offset, limit):
    url = 'https://query.wikidata.org/sparql'
    query = f"""
    SELECT DISTINCT ?city ?cityLabel ?coordinates ?earliest_inception ?latest_population ?continentLabel ?countryLabel
    WHERE {{
      ?city wdt:P31/wdt:P279* wd:Q515.  # Ensure the entity is a city or subclass of city
      ?city wdt:P625 ?coordinates.      # Retrieve coordinates

      OPTIONAL {{
        ?city wdt:P1082 ?population.   # Retrieve population if available
      }}
      OPTIONAL {{
        ?city wdt:P571 ?inception_date.  # Retrieve inception date if available
      }}

        OPTIONAL {{
            ?city wdt:P30 ?continent.      # Retrieve continent if available
        }}
        OPTIONAL {{
            ?city wdt:P17 ?country.        # Retrieve country if available
        }}


      BIND(IF(bound(?inception_date), ?inception_date, "") AS ?earliest_inception)
      BIND(IF(bound(?population), ?population, "") AS ?latest_population)

      FILTER(bound(?population) && bound(?inception_date))  # Filter out results where either inception date or population is null

      {{
        SELECT DISTINCT ?city (MIN(?inception_date) AS ?earliest_inception) (MAX(?population) AS ?latest_population)
        WHERE {{
          ?city wdt:P31/wdt:P279* wd:Q515.  # Ensure the entity is a city or subclass of city

          OPTIONAL {{
            ?city wdt:P1082 ?population.   # Retrieve population if available
          }}
          OPTIONAL {{
            ?city wdt:P571 ?inception_date.  # Retrieve inception date if available
          }}

          FILTER(bound(?population) && bound(?inception_date))  # Filter out results where either inception date or population is null
        }}
        GROUP BY ?city
      }}

      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    ORDER BY ASC(?earliest_inception)
    LIMIT {limit} OFFSET {offset} # Limit the number of results
    """
    response = requests.get(url, params={'query': query}, headers={'Accept': 'application/sparql-results+json'})
    response.raise_for_status()
    return response.json()

def fetch_all_data(max_items, batch_size=1000):
    results = []
    offset = 0

    while offset < max_items:
        print(f"Fetching items {offset} to {offset + batch_size}")
        raw_data = fetch_wikidata(offset, batch_size)
        # Check to make sure we ahve results 
        if raw_data and (not raw_data['results']['bindings'] or len(raw_data['results']['bindings']) == 0):
            break
        cleaned_data = [clean_data(item) for item in raw_data['results']['bindings']]
        results.extend(cleaned_data)


        offset += batch_size
        time.sleep(1)  # Be polite and avoid hammering the server

    return results

# Define the maximum number of items to fetch
MAX_ITEMS = 10000  # Example: Fetch up to 10,000 items

# Fetch all data
all_data = fetch_all_data(MAX_ITEMS)

# Print the number of items fetched
print(f"Total items fetched: {len(all_data)}")

# Save the results to a CSV file
csv_file = 'data/wikidata_results.csv'
with open(csv_file, 'w', newline='') as csvfile:
    fieldnames = ['wikidata_item', 'city', 'longitude', 'latitude', 'date', 'population', 'continent', 'country']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for data in all_data:
        writer.writerow(data)

print(f"Data saved to {csv_file}")

# Old function: 
# def fetch_wikidata(offset, limit):
#     url = 'https://query.wikidata.org/sparql'
#     query = f"""
#     SELECT DISTINCT ?item ?itemLabel ?coordinate ?date ?maxPopulation WHERE {{
#       ?item wdt:P31 wd:Q515 ;             # Items that are instances of "city"
#             wdt:P625 ?coordinate .        # Items with coordinates

#     OPTIONAL {{
#         ?item wdt:P571 ?inceptionDate .
#     }}

#     OPTIONAL {{
#         ?item wdt:P5716 ?foundingDate .
#     }}

#     BIND(MIN(COALESCE(?inceptionDate, ?foundingDate)) AS ?date)

#       {{
#         SELECT ?item (MAX(?population) AS ?maxPopulation) WHERE {{
#           ?item p:P1082 ?statement .
#           ?statement ps:P1082 ?population ;
#                      pq:P585 ?populationDate .
#         }}
#         GROUP BY ?item
#       }}

#       FILTER(BOUND(?date) && BOUND(?maxPopulation))  # Filter to only include items with both date and population available

#       SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
#     }}
#     GROUP BY ?item ?itemLabel ?coordinate ?date ?maxPopulation
#     ORDER BY ASC(?date)
#     LIMIT {limit} OFFSET {offset}
#     """
#     headers = {'Accept': 'application/json'}
#     response = requests.get(url, params={'query': query}, headers=headers)
#     response.raise_for_status()  # Raise an HTTPError on bad responses
#     return response.json()