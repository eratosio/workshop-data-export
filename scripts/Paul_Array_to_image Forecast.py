
from eratos.adapter import Adapter

import rasterio
from rasterio.warp import reproject, Resampling, calculate_default_transform
from rasterio.crs import CRS
from rasterio.transform import from_bounds

import numpy as np
import datetime
from PIL import Image
from matplotlib import cm

#Wrap it into a function, ern, max min values , startTime,endTime)
#Hourly list, 3hourly list

block_ern_list = ['ern:e-pn.io:resource:eratos.blocks.bom.adfd.forestfueldrynessforecastau6km',
'ern:e-pn.io:resource:eratos.blocks.bom.adfd.3hourlythunderstormforecastau6km',
'ern:e-pn.io:resource:eratos.blocks.bom.adfd.hourlywindspeedforecastau6km',
'ern:e-pn.io:resource:eratos.blocks.bom.adfd.3hourlymeanprecipforecastau6km']
var_list = ['DF_SFC','WxThunderstorms_SFC','WindOnHourMagKmh_SFC','Precip_SFC']

list_idx = 3
minRange, maxRange = 0, 1

var = var_list[list_idx]
ern_string_spilt = block_ern_list[list_idx].split('.')
#print(ern_string_spilt[5])

# Load the data.
print('Loading data.')
eratos_adapter = Adapter()
res = eratos_adapter.Resource(ern=block_ern_list[list_idx])
ga = res.data().gapi()

# Query the Gridded API to see what variables are inside the dataset
print(dict.keys(ga.variables()))

                            # Color scale constants.

threeHourly = 7
Hourly = 23
forecast_time = ga.get_subset_as_array('time')
lats = ga.get_subset_as_array('latitude')
lons = ga.get_subset_as_array('longitude')
raw_values = ga.get_subset_as_array(var, starts=[0,0,0], ends=[threeHourly,-1,-1])
# rasterio expects top-left orientation
print(raw_values)

# Project from the grid projection to web mecrator.
print('Reprojecting data.')
print('Bounds:')
print(f'  Min Lon: {lons[0]}')
print(f'  Min Lat: {lats[0]}')
print(f'  Max Lon: {lons[-1]}')
print(f'  Max Lat: {lats[-1]}')

for idx in range(threeHourly):
    
    minTemps = raw_values[idx]
    minTemps = minTemps[::-1,:]
    with rasterio.Env():
        src_shape = minTemps.shape
        src_transform = from_bounds(lons[0], lats[0], lons[-1], lats[-1], minTemps.shape[1], minTemps.shape[0])
        src_crs = CRS.from_proj4(res.prop_path('primary.grid.geo.proj', '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'))

        dst_shape = (minTemps.shape[0]*2,minTemps.shape[1]*2) # Increase the dst size by 2 to help with resampling.
        dst_crs = CRS.from_proj4('+proj=webmerc +datum=WGS84')
        dst_transform, dw, dh = calculate_default_transform(
            src_crs, dst_crs,
            minTemps.shape[1], minTemps.shape[0],
            lons[0], lats[0], lons[-1], lats[-1],
            dst_width=dst_shape[1], dst_height=dst_shape[0]
        )
        dst = np.zeros(dst_shape, minTemps.dtype)

        reproject(
            minTemps,
            dst,
            src_transform=src_transform,
            src_crs=src_crs,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            resampling=Resampling.nearest
        )

    # Save the data.
    print('Saving data.')
    
    scaledTemp = (dst - minRange) / (maxRange-minRange)            # Scale temp from minTemp-maxTemp to 0-1
    rgba = np.uint8(cm.rainbow(scaledTemp)*255)
    rgba[:,:,3] = 255*np.logical_and(dst >= minRange, dst <= maxRange)
    im = Image.fromarray(rgba)
    date_time = datetime.datetime.utcfromtimestamp(forecast_time[idx]).strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f'data/forecast/rasterImage/{date_time}_{ern_string_spilt[5]}.png'
    im.save(f'data/forecast/rasterImage/{ern_string_spilt[5]}_{date_time}.png')
    