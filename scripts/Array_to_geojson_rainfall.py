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

creds_path = r"C:\Users\Quinten\Documents\Eratos_tok\mycreds.json"


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
e_data = eadapter.Resource(ern='ern:e-pn.io:resource:eratos.blocks.bom.adfd.forestfueldrynessforecastau6km')
#access the gridded data via the gridded data adapter:
gridded_e_data = e_data.data().gapi()

print(dict.keys(gridded_e_data.variables()))

exit()

## Define Query Parameters
startDate = "2001-01-01"
endDate = "2021-12-31"
var = 'daily_rain'
bottomLeftPoint = 'POINT(142.180431 -38.189593)'
topRightPoint = 'POINT(149.271033 -34.598160)'

## Extract Data
print("Loading Data.")
extracted_data = gridded_hist_rainfall_data.get_3d_subset_as_array(var,startDate,endDate,bottomLeftPoint,topRightPoint)


## Visualise Data
bottomLeftPoint_shape = wkt.loads(bottomLeftPoint)
topRightPoint_shape = wkt.loads(topRightPoint)

min_lat = bottomLeftPoint_shape.y
min_lon = bottomLeftPoint_shape.x
max_lat = topRightPoint_shape.y
max_lon = topRightPoint_shape.x

lats = gridded_hist_rainfall_data.get_subset_as_array('lat')
lons = gridded_hist_rainfall_data.get_subset_as_array('lon')
spacingLat, spacingLon = lats[1]-lats[0], lons[1]-lons[0]
minLatIdx, maxLatIdx = np.argmin(np.abs(lats-min_lat)), np.argmin(np.abs(lats-max_lat))
minLonIdx, maxLonIdx = np.argmin(np.abs(lons-min_lon)), np.argmin(np.abs(lons-max_lon))

grid_lats = lats[minLatIdx:maxLatIdx+1]
grid_lons = lons[minLonIdx:maxLonIdx+1]
print(len(grid_lons))
#Extract data at required location and time period

#Generate years of interest to loop through
date_generated_list = pd.date_range(startDate, endDate, freq="Y")
date_range_years = date_generated_list.strftime("%Y").to_list()
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

rainfall_grid_20_year_df = gpd.GeoDataFrame(geometry=poly_list)    
rainfall_grid_20_year_df['id'] =  id

count = 0
for year in date_range_years:
    #Work out how many days in a year
    d0 = date(int(year), 1, 1)
    d1 = date(int(year) + 1, 1, 1)
    year_delta = d1 - d0

    #Extract year out of full data vector
    year_arr = extracted_data[count:count+year_delta.days]
    print(year_arr.shape)
    # add length of year (365,366) to count so next loop pulls out the following year
    count += year_delta.days
    
    grid = np.sum(year_arr,axis=0)
    grid[grid < 0] = np.nan
    print(grid.shape)

    annual_rainfall = grid.flatten()

    print(grid[0,0],annual_rainfall[0])
    rainfall_grid_20_year_df[year] = annual_rainfall

print(rainfall_grid_20_year_df)
rainfall_grid_20_year_df.to_file('data/20_year_cummalitve_rainfall.geojson', driver='GeoJSON')
