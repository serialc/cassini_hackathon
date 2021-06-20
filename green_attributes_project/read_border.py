import geopandas as gpd


def getBorder(borderfile="/home/eouser/green_attributes_project"
			"/wdata/LU001L1_LUXEMBOURG/Shapefiles/"
                        "LU001L1_LUXEMBOURG_UA2012_Boundary.shp"):
    return gpd.read_file(borderfile)
    


