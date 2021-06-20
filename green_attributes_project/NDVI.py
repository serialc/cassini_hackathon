# coding: utf-8

# In this script we:
# - load the latest NDVI netCDF (nc) file
# - retrieve the layers NDVI, sd and nobs
# - extract the city boudaries of the city requested
# - reproject the NDVI data
# - extract the NDVI data within those boundaries

# Libraries

from osgeo import gdal
import geopandas as gpd
import glob, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import rioxarray # for the extension to load
import xarray
import rasterio

# Files paths and directories

root = '/Users/marlene.boura/Dropbox/CassiniHackathons2021/cassini_hackathon'
#root = '/home/eouser'
data = root + '/Data'
wdata = root + '/wdata'
file = data + '/c_gls_NDVI300_202106010000_GLOBE_OLCI_V2.0.1.nc'

# if not os.path.exists(wdata):
#     os.makedirs(wdata)
    
if not os.path.exists(wdata + '/ndvi'):
    os.makedirs(wdata + '/ndvi')

#fileOut = wdata + '/ndvi/ncdf.nc'
#fileOutLambert = wdata + '/ndvi/ncdfLambert.nc'

# Loading the nc file

#nc = gdal.Open(file)
nc = xarray.open_dataset(file)
nc = nc.rio.write_crs(4326)
nc
nc.info()

# Clipping

# cannot read the shapefiles locally from mac os ...
boundary = gpd.read_file(wdata + '/LUXEMBOURG/Shapefiles/LU001L1_LUXEMBOURG_CityBoundary.shp')
boundary.crs
boundary.info()

boundaryWGS = boundary.to_crs({"init":"epsg:4326"})
boundaryWGS.crs
boundaryWGS.info()

clipped = nc.rio.clip(boundaryWGS)

# Reprojecting the nc file

clipped_lambert = clipped.NDVI.rio.reproject('EPSG:3035')
clipped_lambert

# Resampling to spatial resolution 100 * 100 m

res = (100, 100)
rst = rasterio.transform.from_bounds(* boundary['geometry'].total_bounds, * res)

# set options
rasterize_city = rasterio.features.rasterize(
    [(poly, 1) for poly in boundary['geometry']],
    out_shape = res,
    transform = rst,
    fill = 0,
    all_touched = True,
    dtype = rasterio.uint8)

# open file for writing with parameters, such as CRS
with rasterio.open(raster_path_tmplt, 'w',
    driver='GTiff',
    crs=boundary.crs,
    dtype=rasterio.uint8,
    count=1,
    width=res[0],
    height=res[1],
    transform=rst
) as dst:
    dst.write(rasterize_city, indexes = 1)
            
# Exporting the dinal NDVI city file

rasterize_city.rio.to_raster(wdata + '/output/NDVI_luxembourg.tif')

