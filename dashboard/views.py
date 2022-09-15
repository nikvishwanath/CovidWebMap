from django.shortcuts import render
import folium
from folium import plugins
import psycopg2
import pandas as pd
from decouple import config


def index(request):

    map1 = folium.Map(location=[19, -12],
                      tiles='cartodbpositron', 
                      zoom_start=2
                      )
    
    # Connect to DB.
    conn = psycopg2.connect(
    host = config('DB_HOST'),
    database = config('DB_NAME'),
    user = config('DB_USER'),
    password = config('DB_PASSWORD')
    )
    
    # Dataframe from DB table.  
    df = pd.read_sql("select * from dashboard_data", conn)
    df_covid = pd.DataFrame(df, columns = ['country', 'deaths', 'cases', 'date_updated'])
    
    # Update country names for integration with country shapes json data.  
    df_covid.replace('Tanzania', 'United Republic of Tanzania', inplace=True)
    df_covid.replace('Serbia', 'Republic of Serbia', inplace=True)
    df_covid.replace('North Macedonia', 'Macedonia', inplace=True)
    df_covid.replace('Guinea-Bissau', 'Guinea Bissau', inplace=True)
    df_covid.replace('Bahamas', 'The Bahamas', inplace=True)
    df_covid.replace('Democratic Republic of Congo', 'Democratic Republic of the Congo', inplace=True)
    df_covid.replace('United States', 'United States of America', inplace=True)
    df_covid.replace('Micronesia (country)', 'Micronesia', inplace=True)
    df_covid.replace('Sint Maarten (Dutch Part)', 'Sint Maarten', inplace=True)
    df_covid.replace('Czechia', 'Czech Republic', inplace=True)
    
    # Country geographies.  
    url = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
    country_shapes = f'{url}/world-countries.json'  

    # Create a chloropleth with the deaths from each country.  
    cp = folium.Choropleth(
        geo_data = country_shapes,
        data = df_covid,
        columns = ['country', 'deaths'],
        key_on='feature.properties.name',
        fill_color = 'YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Total Deaths",
        font_color="white"
        
    ).add_to(map1)
    
    df_covid_indexed = df_covid.set_index('country')

    # Iterate through each of the chloropleth objects and add the deaths, cases, and date last updated.  These will be displayed on the map when the 
    # user hovers over each country.  
    for c in cp.geojson.data['features']:
        # Countries for which data is not available.  
        na_list = [
            'Antarctica', 
            'French Southern and Antarctic Lands',
            'Ivory Coast',
            'Republic of the Congo',
            'Northern Cyprus',
            'Puerto Rico',
            'Western Sahara',
            'Somaliland',
            'Swaziland',
            'Turkmenistan',
            'East Timor',
            'West Bank'
            ]
        if c['properties']['name'] in na_list:
            c['properties']['deaths'] = 'Data Not Available'
            c['properties']['cases'] = "Data Not Available"
            c['properties']['date_updated'] = "Data Not Available"
        if c['properties']['name'] not in na_list:
            c['properties']['deaths'] = '{:,}'.format(df_covid_indexed.loc[c['properties']['name'], 'deaths'])
            c['properties']['cases'] = '{:,}'.format(df_covid_indexed.loc[c['properties']['name'], 'cases'])
            c['properties']['date_updated'] = str(df_covid_indexed.loc[c['properties']['name'], 'date_updated'])
    
    # User interactivity - display these properties when each country is hovered over. 
    folium.GeoJsonTooltip(['name', 'deaths', 'cases', 'date_updated'], ['Country: ', 'Total Deaths: ', 'Total Cases: ', 'Date Updated: ']).add_to(cp.geojson)
    
    plugins.Fullscreen(position='topright').add_to(map1)
    map1 = map1._repr_html_()
    context = {
        'map1': map1
    }
    conn.close()
    return render(request, 'dashboard/index.html', context)