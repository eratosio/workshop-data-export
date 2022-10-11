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

## Define Query Parameters
startDate = "2021-01-01"
endDate = "2021-01-31"
var = 'max_temp'
bottomLeftPoint = 'POINT(142.180431 -38.189593)'
topRightPoint = 'POINT(149.271033 -34.598160)'





#Request acccess to the data resource in Eratos
e_data = eadapter.Resource(ern='ern:e-pn.io:resource:eratos.blocks.silo.maxtemperature')
#access the gridded data via the gridded data adapter:
gridded_max_temperature_data = e_data.data().gapi()
#Query the dataset to see what variables are inside
print(gridded_max_temperature_data.variables())
## Extract Data

#extracted_data = gridded_max_temperature_data.get_3d_subset_as_array(var,startDate,endDate,bottomLeftPoint,topRightPoint,verbose=True)
time_stride = 1
lat_stride = 1
lon_stride = 1

#2 date: Create a Unix timestamp in UTC timezone from the DD-MM-YYYY-MM formatted date string - e.g. "01-01-2022"
unix_ts_utc_start = datetime.datetime.strptime(startDate, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()
unix_ts_utc_end = datetime.datetime.strptime(endDate, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()

times = gridded_max_temperature_data.get_subset_as_array('time')
startTime_idx = np.where(times == unix_ts_utc_start)[0][0]
endTime_idx = (np.where(times == unix_ts_utc_end)[0][0])+1
spacingTime = times[startTime_idx]-times[endTime_idx]

# Load Point strings as Shapely Points     
bottomLeftPoint_shape = wkt.loads(bottomLeftPoint)
if type(bottomLeftPoint_shape) is not geometry.Point:
    raise ValueError('value inside bottomLeftPoint should be a WKT point')
topRightPoint_shape = wkt.loads(topRightPoint)
if type(topRightPoint_shape) is not geometry.Point:
    raise ValueError('value inside topRightPoint should be a WKT point')

# Find closest index location in underlying gridded dataset of bottomLeft and topRight Points, Snapping often occurs
lats = gridded_max_temperature_data.get_subset_as_array('lat')
lons = gridded_max_temperature_data.get_subset_as_array('lon')
spacingLat, spacingLon = lats[1]-lats[0], lons[1]-lons[0]
lats = gridded_max_temperature_data.get_subset_as_array('lat')
lons = gridded_max_temperature_data.get_subset_as_array('lon')
spacingLat, spacingLon = lats[1]-lats[0], lons[1]-lons[0]
minLatIdx, maxLatIdx = np.argmin(np.abs(lats-bottomLeftPoint_shape.y)), np.argmin(np.abs(lats-topRightPoint_shape.y))
minLonIdx, maxLonIdx = np.argmin(np.abs(lons -bottomLeftPoint_shape.x)), np.argmin(np.abs(lons -topRightPoint_shape.x))

data_query_array = gridded_max_temperature_data.get_subset_as_array(var, starts=[startTime_idx,minLatIdx,minLonIdx], ends=[endTime_idx,maxLatIdx,maxLonIdx], strides =  [time_stride,lat_stride,lon_stride])

# Verbose output, explaining whats going on under the hood and how it affects the output

print(f""" 
The following bottom left, {str(bottomLeftPoint)}, and top right {str(topRightPoint)} Points of the grid were provided.
As the grid corners must correspond to the dataset's underlying grid these points were snapped to the following points: 
bottom left, {str('Point('+str(lons[minLonIdx]) + " " + str(lats[minLatIdx]) +")")}, and top right {str('Point('+str(lons[maxLonIdx]) + " " + str(lats[maxLatIdx])+")")}""")
print(f"""
The returned numpy array will have the following shape: {str(data_query_array.shape)}
The first array dimension is time with length {str(data_query_array.shape[0])}
The second array dimension is a south-north vector with length {str(data_query_array.shape[1])} where the index = 0 is the southern most point of the grid {str(lats[minLatIdx])}
Incrementing at {str(round(spacingLat,2))} degree per 1 increase in index ending at {str(lats[maxLatIdx])}.
The third array dimension is a west-east vector with length {str(data_query_array.shape[2])} where the index = 0 is the eastern most point of the grid {str(lons[minLonIdx])}
Incrementing at {str(round(spacingLon,2))} degree per 1 increase in index ending at {str(lons[maxLonIdx])}.
    """)




coordinates =[[lons[minLonIdx],lats[maxLatIdx]],
[lons[maxLonIdx],lats[maxLatIdx]],
[lons[maxLonIdx],lats[minLatIdx]],
[lons[minLonIdx],lats[minLatIdx]]]

with open("coordinates.json", "w") as outfile:
    json.dump(coordinates, outfile)


    
# Only change
grid = np.mean(data_query_array,axis=0)
#

#grid[grid < 0] = np.nan
grid[grid < 0] = 0

print(grid.shape)
#print(grid)
from PIL import Image

im = Image.fromarray(grid)

if im.mode != 'RGB':
    im = im.convert('RGB')


im.save()



