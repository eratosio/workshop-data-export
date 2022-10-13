from eratos.creds import AccessTokenCreds
from eratos.adapter import Adapter
import eratos.climate as eratosClimate
import eratos.helpers as helpers
import os
import yaml
from yaml.loader import SafeLoader
import json
import pprint
import datetime
import shapely
from shapely import wkt, geometry
from datetime import timezone
from keplergl import KeplerGl
import geopandas as gpd
import numpy as np
import datetime
import json
import pandas as pd
import numpy as np
from datetime import  timezone
from datetime import date
import geopandas as gpd
from shapely.geometry import box
from shapely import wkt
import os

dirname = os.path.dirname(__file__)
creds_path = os.path.abspath(os.path.join(dirname, '..', 'mycreds.json'))



# Opening JSON file
f = open(creds_path)
  
# returns JSON object as 
# a dictionary
creds = json.load(f)

ecreds = AccessTokenCreds(
  creds['key'],
  creds['secret']
)
eadapter = Adapter(ecreds)


#Access SILO max temperature dataset block
e_data = eadapter.Resource(ern='ern:e-pn.io:resource:fcdi.block.vic-5.rcp85.cnrm-cerfacs-cnrm-cm5.r1i1p1.csiro-ccam-r3355.v1.day.tasmax')
gridded_max_temperature_data = e_data.data().gapi()

#Define variable we wish to extract
var = 'tasmax'

#40C = 313.15K  
# Tasmax is in Kelvin
threshold_temp_celsius = 35
cel_to_kelvin = 273.15

startDate = "2010-01-01T12:00:00Z"
endDate = "2079-12-31T12:00:00Z"


date_generated_list = pd.date_range(startDate, endDate, freq="Y")
date_range = date_generated_list.strftime("%Y").to_list()

df_id_list = []
df_point_list = []
df_days_above_list = []
df_year_list = []


#extract data for all three points, as using the same dataset can be done in one call
bottomLeftPoint = 'POINT(142.180431 -38.189593)'
topRightPoint = 'POINT(149.271033 -34.598160)'

## Extract Data
print("Loading Data.")
extracted_data = gridded_max_temperature_data.get_3d_subset_as_array(var,startDate,endDate,bottomLeftPoint,topRightPoint)

## Visualise Data
bottomLeftPoint_shape = wkt.loads(bottomLeftPoint)
topRightPoint_shape = wkt.loads(topRightPoint)

min_lat = bottomLeftPoint_shape.y
min_lon = bottomLeftPoint_shape.x
max_lat = topRightPoint_shape.y
max_lon = topRightPoint_shape.x

lats = gridded_max_temperature_data.get_subset_as_array('lat')
lons = gridded_max_temperature_data.get_subset_as_array('lon')
spacingLat, spacingLon = lats[1]-lats[0], lons[1]-lons[0]
minLatIdx, maxLatIdx = np.argmin(np.abs(lats-min_lat)), np.argmin(np.abs(lats-max_lat))
minLonIdx, maxLonIdx = np.argmin(np.abs(lons-min_lon)), np.argmin(np.abs(lons-max_lon))

grid_lats = lats[minLatIdx:maxLatIdx+1]
grid_lons = lons[minLonIdx:maxLonIdx+1]
print(len(grid_lons))
#Extract data at required location and time period

#Generate years of interest to loop through
#print(date_range_years)

poly_list = []
max_temp_val = []
id = []
count = 1

for i in range(len(grid_lats)-1):
  
  for j in range(len(grid_lons)-1):

    #print(j)
    poly = box(grid_lons[j],grid_lats[i],grid_lons[j+1],grid_lats[i+1])
    poly_list.append(poly)
    id.append(count)
    count+= 1

geo_dataframe = gpd.GeoDataFrame(geometry=poly_list)    
geo_dataframe['id'] =  id

count = 0

for date_val in date_range:
        #Work out how many days in a year
        d0 = date(int(date_val), 1, 1)
        d1 = date(int(date_val) + 1, 1, 1)
        year_delta = d1 - d0
       
        # calcuate days in year above threshold, celsius
        bool_arr = extracted_data[count:count+year_delta.days]  > (threshold_temp_celsius + cel_to_kelvin)
        
        count += year_delta.days
        grid = np.sum(bool_arr,axis=0)
        
        annual_days_above = grid.flatten()
        geo_dataframe[date_val] = annual_days_above



startDate = "2010-01-01T12:00:00Z"
endDate = "2079-12-31T12:00:00Z"

future_decades= ['2010s','2020s','2030s','2040s','2050s','2060s','2070s']

#Historical collating
grouping_decades= ['2010','2020','2030','2040','2050','2060','2070','2080']


for idx , decade in enumerate(future_decades):
    #print(decade)
    decade_year_list = pd.date_range(grouping_decades[idx], grouping_decades[idx+1], freq="Y")
    date_range_years = decade_year_list.strftime("%Y").to_list()
    print(date_range_years)
    geo_dataframe[decade] = geo_dataframe[date_range_years].mean(axis=1)

    

print(geo_dataframe.head()) 

geo_dataframe.to_file('data/2010_to_2070_projected_decadal_days_above_35.geojson', driver='GeoJSON')