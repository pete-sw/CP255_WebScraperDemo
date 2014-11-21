# Author: Geoff Boeing
# Purpose: Merges two data sets on pid to combine lat-long data with rental listing data
import pandas, os
from time import strftime

# [dan] read each csv into a pandas dataframe
rents = pandas.read_csv('temp-rentals.csv', usecols=['pid', 'neighborhood', 'title', 'price', 'date', 'sqft', 'bedrooms', 'link', 'sourcepage'])
latlong = pandas.read_csv('temp-latlong.csv', usecols=['pid', 'latitude', 'longitude'])

rents = rents.drop_duplicates(cols='pid')
latlong = latlong.drop_duplicates(cols='pid')

# [dan] use pandas to merge the two dataframes by matching on the "pid" column, then write to a new file. Then delete the two unmerged files
combined = pandas.merge(rents, latlong, on='pid', how='left')

filename = 'DC_craigslist-' + strftime('%Y-%m-%d-%H-%M-%S') + '.csv'
combined.to_csv(filename, index=False)

os.remove('temp-rentals.csv')
os.remove('temp-latlong.csv')
