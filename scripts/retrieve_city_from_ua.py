# The script reads an argument (city name) and:
# - retrieves the zip file,
# - unzips it, and 
# - converts vector to raster

import os, sys, re, zipfile, shutil
import geopandas as gpd
import rasterio
from rasterio import features

#import pandas as pd
#import numpy as np
#import matplotlib.pyplot as plt

data_root = '/eodata/'
urban_atlas = data_root + 'CLMS/Local/Urban_Atlas/Urban_Atlas_2012/'
wd = 'wdata/'
overwrite = False

# load conversion table for LU codes see source: https://land.copernicus.eu/user-corner/technical-library/urban-atlas-mapping-guide
ludict = {}
with open('resources/lu_codes.csv', 'r') as f:
    for line in f:
        p = line.strip().split(',')
        ludict[p[0]] = int(p[1])

if len(sys.argv) < 2:
    exit("Please specify the city name argument")

# good we have enough arguments
city = sys.argv[1]

# check overwrite parameter
if len(sys.argv) == 3 and sys.argv[2] == 'overwrite':
    overwrite = True

cityname = city.upper()
ua_file_name = ''

# copy it from urban_atlas to wd
for f in os.listdir(urban_atlas):
    # we want to match the city name string with underscores or no spaces
    v1 = '_'.join(re.split('_|\.', f)[1:-1])
    v2 = ''.join(re.split('_|\.', f)[1:-1])

    # check this is the filename we want
    if v1 == cityname or v2 == cityname:
        ua_file_name = f.strip('.zip')
        break

# unzip
# optimization possible - we can directly extract shapefile without unzipping
# see: https://geopandas.org/docs/user_guide/io.html
with zipfile.ZipFile(urban_atlas + ua_file_name + '.zip', 'r') as zip_ref:

    # extract file if it doesn't exist or requested overwrite
    if not os.path.exists(wd + cityname) or overwrite:
        # delete old directory
        #os.remove(wd + cityname)
        if os.path.exists(wd + cityname):
            shutil.rmtree(wd + cityname)

        zip_ref.extractall(wd)
        os.rename(wd + ua_file_name, wd + cityname)

# extract the boundaries and save
# is done above automatically for UA2012 as the bounds are provided

# save as raster
shapefile_path = wd + cityname + "/Shapefiles/" + ua_file_name + "_CityBoundary.shp"
shapefile_path2 = wd + cityname + "/Shapefiles/" + ua_file_name + "_UA2012.shp"
raster_paths =  wd + cityname + '/rasters/'
resolution = (100, 100)

if os.path.exists(shapefile_path):
    # make the folder if needed
    if not os.path.exists(raster_paths):
        os.mkdir(raster_paths)

    raster_path_tmplt = raster_paths + cityname + '_template.tif'
    raster_path_values = raster_paths + cityname + '_values.tif'

    if not os.path.exists(raster_path_tmplt) or overwrite:
        print("Creating city raster template from Urban Atlas city bounds")

        # load the shapefile
        city_shp = gpd.read_file(shapefile_path)

        # load geometry from shapefile
        transform = rasterio.transform.from_bounds(*city_shp['geometry'].total_bounds, *resolution)

        # set options
        rasterize_city = rasterio.features.rasterize(
            [(poly, 1) for poly in city_shp['geometry']],
            out_shape=resolution,
            transform=transform,
            fill=0,
            all_touched=True,
            dtype=rasterio.uint8)

        # open file for writing with parameters, such as CRS
        with rasterio.open(raster_path_tmplt, 'w',
            driver='GTiff',
            crs=city_shp.crs,
            dtype=rasterio.uint8,
            count=1,
            width=resolution[0],
            height=resolution[1],
            transform=transform
        ) as dst:
            dst.write(rasterize_city, indexes=1)

    if not os.path.exists(raster_path_values) or overwrite:
        print("Creating city landuse raster from Urban Atlas")

        # load the shapefile
        city_lu_shp = gpd.read_file(shapefile_path2)

        # want code as int rather than string - shortening codes
        city_lu_shp['code'] = [ludict[v] for v in city_lu_shp['CODE2012']]

        # load the raster template
        rst = rasterio.open(raster_path_tmplt)

        # copy meta data from source
        meta = rst.meta.copy()
        meta.update(compress='lzw')

        # burn the feature into raster
        with rasterio.open(raster_path_values, 'w+', **meta) as out:
            out_arr = out.read(1)

            # create an iterator 'table' that has the geometry and the landuse code
            shapes = ((geom, code) for geom, code in zip(city_lu_shp.geometry, city_lu_shp.code))
            shapes2 = city_lu_shp[['geometry', 'code']].values.tolist()

            # rasterize will iterate through the shapes (geometry, value)
            burned = rasterio.features.rasterize(shapes=shapes2, fill=0, out=out_arr, transform=out.transform)

            out.write_band(1, burned)

else:
    exit("ERROR - didn't find shapefile: " + shapefile_path)

