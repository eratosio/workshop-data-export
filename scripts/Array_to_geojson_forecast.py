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
import datetime
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


block_ern_list = ['ern:e-pn.io:resource:eratos.blocks.bom.adfd.forestfueldrynessforecastau6km',
'ern:e-pn.io:resource:eratos.blocks.bom.adfd.3hourlythunderstormforecastau6km',
'ern:e-pn.io:resource:eratos.blocks.bom.adfd.hourlywindspeedforecastau6km',
'ern:e-pn.io:resource:eratos.blocks.bom.adfd.3hourlymeanprecipforecastau6km']
var_list = ['DF_SFC','WxThunderstorms_SFC','WindOnHourMagKmh_SFC','Precip_SFC']

list_idx = 2

var = var_list[list_idx]

ern_string_spilt = block_ern_list[list_idx].split('.')
#Request acccess to the data resource in Eratos
e_data = eadapter.Resource(ern=block_ern_list[list_idx])
#access the gridded data via the gridded data adapter:
gridded_e_data = e_data.data().gapi()

print(dict.keys(gridded_e_data.variables()))

threeHourly = 7
Hourly = 23
Start = 5

forecast_time = gridded_e_data.get_subset_as_array('time')

## Define Query Parameters
startDate = datetime.datetime.utcfromtimestamp(forecast_time[Start]).strftime('%Y-%m-%d_%H-%M-%S')
endDate = datetime.datetime.utcfromtimestamp(forecast_time[Start+threeHourly]).strftime('%Y-%m-%d_%H-%M-%S')


print(startDate,endDate)

bottomLeftPoint = 'POINT(142.180431 -38.189593)'
topRightPoint = 'POINT(149.271033 -34.598160)'

## Extract Data

#extracted_data = gridded_e_data.get_3d_subset_as_array(var,startDate,endDate,bottomLeftPoint,topRightPoint)

## Visualise Data
bottomLeftPoint_shape = wkt.loads(bottomLeftPoint)
topRightPoint_shape = wkt.loads(topRightPoint)

min_lat = bottomLeftPoint_shape.y
min_lon = bottomLeftPoint_shape.x
max_lat = topRightPoint_shape.y
max_lon = topRightPoint_shape.x

lats = gridded_e_data.get_subset_as_array('latitude')
lons = gridded_e_data.get_subset_as_array('longitude')
spacingLat, spacingLon = lats[1]-lats[0], lons[1]-lons[0]
minLatIdx, maxLatIdx = np.argmin(np.abs(lats-min_lat)), np.argmin(np.abs(lats-max_lat))
minLonIdx, maxLonIdx = np.argmin(np.abs(lons-min_lon)), np.argmin(np.abs(lons-max_lon))

print("Loading Data.")
extracted_data = gridded_e_data.get_subset_as_array(var, starts=[Start,minLatIdx,minLonIdx], ends=[Start+threeHourly,maxLatIdx,maxLonIdx], strides =  [1,1,1])








grid_lats = lats[minLatIdx:maxLatIdx+1]
grid_lons = lons[minLonIdx:maxLonIdx+1]
print(len(grid_lons))
#Extract data at required location and time period


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
for idx in range(threeHourly):

    print(idx)
    #Extract year out of full data vector
    year_arr = extracted_data[idx]
    print(year_arr.shape)
   

    forecast_data = year_arr.flatten()

   #print(year_arr[0,0],forecast_data[0])
    geo_dataframe[datetime.datetime.utcfromtimestamp(forecast_time[idx]).strftime('%Y-%m-%dT%H:%M:%SZ')] = forecast_data


#print(geo_dataframe)
geo_dataframe.to_file(f'data/forecast/geojson/{ern_string_spilt[5]}_{startDate}_to_{endDate}.geojson', driver='GeoJSON')
