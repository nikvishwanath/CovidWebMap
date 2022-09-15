from cmath import isnan
import pandas as pd
import psycopg2
import numpy as np
from decouple import config 

# Run this script when the table in the database needs to be updated.  

# Connect to DB. 
conn = psycopg2.connect(
    host = config('DB_HOST'),
    database = config('DB_NAME'),
    user = config('DB_USER'),
    password = config('DB_PASSWORD')
    )

cur = conn.cursor()

# Clear the table.  
cur.execute("truncate table dashboard_data")
conn.commit()

# Add data as in initial_data.py.

# Data source. 
url = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'

# Dataframe. 
x_df = pd.read_csv(url)

for index in range(len(x_df.index)-1):
    # Iterate until the last row for each country, which contains the most recent data. 
    if x_df['location'][index] != x_df['location'][index+1]:
        
        # Handling the case where the latest row of data for a country is empty. 
        while np.isnan(x_df['total_cases'][index]):
            index = index - 1
            
        location = x_df['location'][index]
        
        # Don't include non-country specific data.
        not_countries = [
            'Asia', 'Africa', 'North America', 'South America', 'Europe','European Union', 
            'High income', 'International', 'Low income', 'Lower middle income', 
            'Upper middle income', 'World', 'European Union'
            ]
        
        if location not in not_countries:
            total_cases = x_df['total_cases'][index]
            total_deaths = x_df['total_deaths'][index]
            date_updated = str(x_df['date'][index])
            
            # Set total deaths to 0 if there is data for total cases but no recorded deaths.
            if not np.isnan(total_cases) and np.isnan(total_deaths):
                total_deaths = 0
            # Add to DB if there is data.  
            if not np.isnan(total_cases) and not np.isnan(total_deaths):
                cur.execute("insert into dashboard_data (country, deaths, cases, date_updated) values (%s, %s, %s, %s)", (location, total_deaths,total_cases, date_updated))
    # Last country (Zimbabwe).
    if index == len(x_df.index)-2:
        location = x_df['location'][index+1]
        total_cases = x_df['total_cases'][index+1]
        total_deaths = x_df['total_deaths'][index+1]
        date_updated = x_df['date'][index+1]
        if not np.isnan(total_cases) and np.isnan(total_deaths):
                total_deaths = 0  
        if not np.isnan(total_cases) and not np.isnan(total_deaths):
                cur.execute("insert into dashboard_data (country, deaths, cases, date_updated) values (%s, %s, %s, %s)", (location, total_deaths,total_cases, date_updated))
conn.commit()
cur.close()
conn.close()  