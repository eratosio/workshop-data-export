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

creds_path = r"/home/ml/code/eratos/token/creds.json"

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

#Request acccess to the data resource in Eratos
e_data = eadapter.Resource(ern='ern:e-pn.io:resource:eratos.blocks.barra.r.ffdi')
#access the gridded data via the gridded data adapter:
gridded_data = e_data.data().gapi()

## Define Query Parameters
startDate = "2019-01-01"
endDate = "2019-01-10"
var = 'ffdi'
bottomLeftPoint = 'POINT(142.180431 -38.189593)'
topRightPoint = 'POINT(149.271033 -34.598160)'

## Extract Data
print("Loading Data.")
extracted_data = gridded_data.get_3d_subset_as_array(var,startDate,endDate,bottomLeftPoint,topRightPoint)

## Visualise Data
bottomLeftPoint_shape = wkt.loads(bottomLeftPoint)
topRightPoint_shape = wkt.loads(topRightPoint)

min_lat = bottomLeftPoint_shape.y
min_lon = bottomLeftPoint_shape.x
max_lat = topRightPoint_shape.y
max_lon = topRightPoint_shape.x

lats = gridded_data.get_subset_as_array('lat')
lons = gridded_data.get_subset_as_array('lon')
spacingLat, spacingLon = lats[1]-lats[0], lons[1]-lons[0]
minLatIdx, maxLatIdx = np.argmin(np.abs(lats-min_lat)), np.argmin(np.abs(lats-max_lat))
minLonIdx, maxLonIdx = np.argmin(np.abs(lons-min_lon)), np.argmin(np.abs(lons-max_lon))

grid_lats = lats[minLatIdx:maxLatIdx+1]
grid_lons = lons[minLonIdx:maxLonIdx+1]
print(len(grid_lons))
#Extract data at required location and time period

#Generate years of interest to loop through
date_generated_list = pd.date_range(startDate, endDate, freq="D")
date_range_years = date_generated_list.strftime("%Y-%m-%d").to_list()
#print(date_range_years)

forecast_time = gridded_data.get_subset_as_array('time')
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

ffdi_2019_df = gpd.GeoDataFrame(geometry=poly_list)    
ffdi_2019_df['id'] =  id

count = 0
hours_in_day = 24
for idx in range(9):

    print(idx)

    
    #Extract year out of full data vector
    year_arr = extracted_data[count:count+hours_in_day]
    #print(year_arr.shape)
    # add length of year (365,366) to count so next loop pulls out the following year

    grid = np.mean(year_arr,axis = 0)

    count += hours_in_day

    #Extract year out of full data vector

    forecast_data = grid.flatten()

   #print(year_arr[0,0],forecast_data[0])
    ffdi_2019_df[date_range_years[idx]] = forecast_data


print(ffdi_2019_df)
ffdi_2019_df.to_file('data/2019_daily_mean_ffdi.geojson', driver='GeoJSON')
