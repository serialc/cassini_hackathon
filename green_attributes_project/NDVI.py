
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

# Files paths and directories

data = '/home/eouser/Data'
file = data + '/c_gls_NDVI300_202106010000_GLOBE_OLCI_V2.0.1.nc'
wdata = '/home/eouser/green_attributes_project/wdata'

# if not os.path.exists(wdata):
#     os.makedirs(wdata)
    
if not os.path.exists(wdata + '/ndvi'):
    os.makedirs(wdata + '/ndvi')

fileOut = wdata + '/ndvi/ncdf.nc'
fileOutLambert = wdata + '/ndvi/ncdfLambert.nc'

# Loading the nc file to the urban boundaries

nc = gdal.Open(file)

for key, value in nc.GetMetadata().items():
    print("{:35}: {}".format(key, value))

for item in nc.GetSubDatasets():
    print(item[0])

for item in nc.GetSubDatasets():
    print(item[1])


# Loading the layer of interest

ndvi = gdal.Open(nc.GetSubDatasets()[0][0])
ndvi_sd_no = gdal.Open(nc.GetSubDatasets()[1][0])
ndvibs = gdal.Open(nc.GetSubDatasets()[2][0])
ndvi_flag = gdal.Open(nc.GetSubDatasets()[3][0])

np.size(ndvi)


# Dimensions of the file

print ('NDVI (T, Y, X)' , (ndvi.RasterCount, ndvi.RasterYSize, ndvi.RasterXSize))


# ndvi.GetMetadata()

# ndvi.GetGeoTransform()

ndvi.GetProjection()


# Loading the city's boundaries

boundary = gpd.read_file(wdata + '/LUXEMBOURG/Shapefiles/LU001L1_LUXEMBOURG_CityBoundary.shp')
boundaryFUA = gpd.read_file(wdata + '/LUXEMBOURG/Shapefiles/LU001L1_LUXEMBOURG_UA2012_Boundary.shp')

boundary.crs

boundary

ndvi.SetGeoTransform()
# ndvi.SetProjection()

gdal.Warp(ndvi, wdata + '/ndvi/ndvi.tif',
                cutlineDSName = boundary, 
                cropToCutLine = True)


#ndvi.ReadAsArray()[1,1:3,1:2]
ndvi[:,30:40, 30:40]


# In[76]:


figsize = (12, 12)
ax.set_axis_off()


# In[83]:


f, ax = plt.subplots(figsize = (12, 12))
plt.imshow(ndvi.ReadAsArray(), extent = ext)


# In[77]:


boundary.plot()


# In[60]:


ext = boundary.total_bounds


# In[65]:


t = 1
x1, x2 = ext[0], ext[1]
y1, y2 = ext[2], ext[3]


# In[67]:


plt.imshow(ndvi.ReadAsArray()[t, x1:x2, y1:y2],
          extent = ext,
          cmap = 'gist_earth')


# In[71]:


boundary.crs


# In[73]:


ndvi.GetProjection()


# In[108]:


gdal.Warp(ndvi, wdata + '/ndvi/ndvi.tif',
                cutlineDSName = boundary, 
                cropToCutLine = True)


# In[ ]:


cdo.sellonlatbox(ext, input = file, output = newNdvi, options = '-f nc')


# In[ ]:


cdo.sellonlatbox(ext, input = file, output = newNdvi, options = '-f nc')


# In[33]:


print(ndvi)


# In[ ]:


#ndvi = netcdf.NetCDFFile(file, 'r')
#print(ndvi)


# In[ ]:


#Cdo.sellonlatbox(ext, input = file,
#                 output = fileOut, 
#                 options = '-f nc')

