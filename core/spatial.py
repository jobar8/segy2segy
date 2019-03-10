"""
Functions for reading and transforming spatial data.
Makes use of the GDAL library: http://www.gdal.org
:copyright: 2019 Geophysics Labs
:author: Joseph Barraud
:license: BSD License
"""

import numpy as np

# import GDAL modules
from osgeo import osr, ogr


#==============================================================================
#  projectPoints
#==============================================================================
def projectPoints(inputPoints, s_srs=4326, t_srs=23029):
    '''
    Reproject a set of points from one spatial reference to another.

    Parameters
    ----------
    inputPoints : list of doubletons or array of shape (n, 2)
        Coordinates of points to transform. Must be in groups of (X,Y) or (Lon,Lat).
    s_srs : Integer
        Spatial reference system of the input (source) file. Must be defined as a EPSG code,
        i.e. 23029 for ED50 / UTM Zone 29N
    t_srs : Integer
        Spatial reference system of the output (target) file. Must be defined as a EPSG code,
        i.e. 23029 for ED50 / UTM Zone 29N

    Returns
    -------
    outputPoints : array of shape (n, 2)
        Transformed coordinates of input points.

    Note
    ----
    Other examples of EPSG codes:
        WGS84 = EPSG:4326
        ED50 / UTM Zone 30N = EPSG:23030
    '''
    # input SpatialReference
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(s_srs)

    # output SpatialReference
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(t_srs)

    # create the CoordinateTransformation
    coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    # Loop through the points
    outputPoints = []
    for XY in inputPoints:
        point = ogr.CreateGeometryFromWkt("POINT ({} {})".format(*XY))
        point.Transform(coordTrans)
        outputPoints.append([point.GetX(), point.GetY()])

    return np.asarray(outputPoints)
