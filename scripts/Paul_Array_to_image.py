
from eratos.adapter import Adapter

import rasterio
from rasterio.warp import reproject, Resampling, calculate_default_transform
from rasterio.crs import CRS
from rasterio.transform import from_bounds

import numpy as np

from PIL import Image
from matplotlib import cm

#Wrap it into a function, ern, max min values , startTime,endTime)

# Load the data.
print('Loading data.')
eratos_adapter = Adapter()
res = eratos_adapter.Resource(ern='ern:e-pn.io:resource:eratos.blocks.silo.mintemperature')
ga = res.data().gapi()
lats = ga.get_subset_as_array('lat')
lons = ga.get_subset_as_array('lon')
minTemps = ga.get_subset_as_array('min_temp', starts=[0,0,0], ends=[1,-1,-1])
minTemps = minTemps[0,::-1,:] # rasterio expects top-left orientation

# Project from the grid projection to web mecrator.
print('Reprojecting data.')
print('Bounds:')
print(f'  Min Lon: {lons[0]}')
print(f'  Min Lat: {lats[0]}')
print(f'  Max Lon: {lons[-1]}')
print(f'  Max Lat: {lats[-1]}')
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
minTemp, maxTemp = -20.0, 30                              # Color scale constants.
scaledTemp = (dst - minTemp) / (maxTemp-minTemp)            # Scale temp from minTemp-maxTemp to 0-1
rgba = np.uint8(cm.rainbow(scaledTemp)*255)
rgba[:,:,3] = 255*np.logical_and(dst >= minTemp, dst <= maxTemp)
im = Image.fromarray(rgba)
im.save('data/aus_min_temp.png')