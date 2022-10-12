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

bottomLeftPoint = 'POINT(142.180431 -38.189593)'
topRightPoint = 'POINT(149.271033 -34.598160)'

## Visualise Data
bottomLeftPoint_shape = wkt.loads(bottomLeftPoint)
topRightPoint_shape = wkt.loads(topRightPoint)

min_lat = bottomLeftPoint_shape.y
min_lon = bottomLeftPoint_shape.x
max_lat = topRightPoint_shape.y
max_lon = topRightPoint_shape.x

size = 10000

generated_lons = np.random.uniform(low=min_lon, high=max_lon, size=size)

generated_lats = np.random.uniform(low=min_lat, high=max_lat, size=size)

generated_morgages = np.random.uniform(low=10000, high=10000000, size=size)

generated_fire_risk = np.random.uniform(low=0, high=1, size=size)
generated_frost_risk = np.random.uniform(low=0, high=1, size=size)
generated_storm_risk = np.random.uniform(low=0, high=1, size=size)
generated_flood_risk = np.random.uniform(low=0, high=1, size=size)

df = pd.DataFrame()

df['lons'] = generated_lons
df['lats'] = generated_lats
df['morgages'] = generated_morgages
df['fire_risk'] = generated_fire_risk
df['frost_risk'] = generated_frost_risk
df['storm_risk'] = generated_storm_risk
df['flood_risk'] = generated_flood_risk


df.to_csv('data/morgage_data.csv')