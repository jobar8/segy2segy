# -*- coding: utf-8 -*-
"""
Functions for reading and transforming spatial data. 
Makes use of the GDAL library: http://www.gdal.org
:copyright: 2016 Geophysics Labs
:author: Joseph Barraud
:license: BSD License
"""

# Import system modules
import os

# import numpy
import numpy as np

# import GDAL modules
from osgeo import gdal,osr,ogr

# example GDAL error handler function
def gdal_error_handler(err_class, err_num, err_msg):
    errtype = {
            gdal.CE_None:'None',
            gdal.CE_Debug:'Debug',
            gdal.CE_Warning:'Warning',
            gdal.CE_Failure:'Failure',
            gdal.CE_Fatal:'Fatal'
    }
    err_msg = err_msg.replace('\n',' ')
    err_class = errtype.get(err_class, 'None')
    print 'Error Number: %s' % (err_num)
    print 'Error Type: %s' % (err_class)
    print 'Error Message: %s' % (err_msg)

# install error handler
gdal.PushErrorHandler(gdal_error_handler)
    
#==============================================================================
# rasterToArray
#==============================================================================
class file_info:
    """A class holding information about a GDAL file.
    Copied from gdal_merge.py (GDAL samples)
    """

    def init_from_name(self, filename):
        """
        Initialize file_info from filename

        filename -- Name of file to read.

        Returns 1 on success or 0 if the file can't be opened.
        modified by JB - 18 Oct 2015
        """
        fh = gdal.Open( filename )
        if fh is None:
            return 0

        self.filename = filename
        self.bands = fh.RasterCount
        self.xsize = fh.RasterXSize
        self.ysize = fh.RasterYSize
        self.band_type = fh.GetRasterBand(1).DataType
        self.projection = fh.GetProjection()
        self.geotransform = fh.GetGeoTransform()
        self.cellsize = self.geotransform[1] # new
        self.ulx = self.geotransform[0] # corner of upper-left pixel
        self.uly = self.geotransform[3]
        self.lrx = self.ulx + self.geotransform[1] * self.xsize
        self.lry = self.uly + self.geotransform[5] * self.ysize
        self.data = fh.ReadAsArray()  # new
        self.noDataValue = fh.GetRasterBand(1).GetNoDataValue() # new
        
        ct = fh.GetRasterBand(1).GetRasterColorTable()
        if ct is not None:
            self.ct = ct.Clone()
        else:
            self.ct = None

        return 1

    def report( self ):
        #print('\nFilename: '+ self.filename)
        print('Raster Size: {:d} columns x {:d} rows x {:d} bands'.format(self.xsize, self.ysize, self.bands))
        print('Cell Sizes: {:.2f} x {:.2f}'.format(self.geotransform[1],self.geotransform[5]))
        print('Upper-left corner:({:.2f},{:.2f})\nBottom-right corner:({:.2f},{:.2f})'.format(self.ulx,self.uly,self.lrx,self.lry))
        print('No Data Value: {}'.format(self.noDataValue))

#*****************************************************************************
def rasterToArray(infile,doNan=True,doMessage=True):
    '''
    This tool converts a raster image to a numpy array (like the arcpy function)
    and also returns coordinates and grid properties.
    
    Usage
    -----
    
    data,nrows,ncols,header = spatial.rasterToArray(infile)
    [xll,yll,cellsize,nodata_value] = header # coordinates of cell center
    '''
    # read raster 
    fi = file_info()
    fi.init_from_name(infile)
    
    # print report
    if doMessage:
        fi.report()

    # Get raster properties
    if abs(fi.geotransform[1] - abs(fi.geotransform[5])) > 1e-6:
        raise Exception("Pixels are not square (cell size different in x and y directions)")
    cellsize = fi.geotransform[1]

    ncols = fi.xsize # nb of columns
    nrows = fi.ysize # nb of rows
    nodata_value = fi.noDataValue

    # Converts extent to header (coordinates of cell center)
    xll = fi.ulx + cellsize/2.
    yll = fi.lry + cellsize/2.
    header = [xll,yll,cellsize,nodata_value]
    
    # convert nodata values to nans
    if doNan:
        fi.data[fi.data == nodata_value] = np.nan

    return fi.data,nrows,ncols,header
    
#==============================================================================
# extent
#==============================================================================
def extent(xll,yll,cellsize,nrows,ncols,scale=1.):
    '''
    Return the extent of a raster given the coordinates of the lower-left corner,
    the cellsize and the numbers of rows and columns. The coordinates are defined
    as cell centres.
    '''
    xmin = xll*scale
    xmax = (xll+(ncols-1)*cellsize)*scale
    ymin = yll * scale
    ymax = (yll + (nrows-1)*cellsize)*scale
    return (xmin,xmax,ymin,ymax)
    
#==============================================================================
# calcGeoTransform
#==============================================================================
def calcGeoTransform(xll,yll,dx,dy,nrows,ncols):
    '''
    Transform header parameters to GDAL GeoTransform.
    xll and yll are the coordinates of the center of bottom-left pixel.
    '''
    
    top_left_x = xll - dx/2.
    top_left_y = (yll + (nrows-1)*dy) + dy/2.
    return (top_left_x,dx,0,top_left_y,0,-1*dy)
    
# =============================================================================
# arrayToRaster
# =============================================================================
def arrayToRaster(data,outFile,xll=0,yll=0,cellsize=100,dy=None,outSR=None,format="GTiff",
                  dataType='Float32',nodata_value=-999999.,creation_options=[]):
    '''
    This tool creates a raster file from a numpy array using GDAL drivers.
    xll,yll = coordinates of center of bottom-left pixel
    WGS84 = EPSG:4326
    '''
    # geographic location of the grid
    RasterYSize,RasterXSize = data.shape
    if dy: # cell not square
        geoT = calcGeoTransform(xll,yll,cellsize,dy,RasterYSize,RasterXSize)
    else:
        geoT = calcGeoTransform(xll,yll,cellsize,cellsize,RasterYSize,RasterXSize)
    
    # Set nans to the No Data Value
    data[np.isnan(data)] = nodata_value
    
    drv = gdal.GetDriverByName(format)
    GDdataType = gdal.GetDataTypeByName(dataType)
    outRaster = drv.Create(outFile,RasterXSize,RasterYSize,1,GDdataType,creation_options) # the '1' is for band 1.
    outRaster.SetGeoTransform(geoT) # GDAL references top-left corner of top-left pixel
    outBand = outRaster.GetRasterBand(1)
    outBand.WriteArray(data)
    outBand.SetNoDataValue(nodata_value)
    outBand.GetStatistics(0,1)
    
    # define projection
    if outSR:
        outRasterSRS = osr.SpatialReference()
        try:
            if os.path.isfile(outSR): # if definition is .prj file
                with open(outSR) as f:
                    ESRIstring = f.readlines()
                outRasterSRS.ImportFromESRI(ESRIstring)
        except TypeError: # definition is assumed to be EPSG code
            outRasterSRS.ImportFromEPSG(outSR)
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
    
    #  dereference the raster dataset to write the data modifications and close the raster file.
    outBand = None
    outRaster = None
    
    return
    
#===============================================================================
# grid2xyz
#===============================================================================
def grid2xyz(inputFile,dest='',addZcolumn=False):
    '''
    Converts raster and grid to .xyz file
    The output format is eithe three columns X Y Data or optionally with an additional
    Z column filled with zeros (useful for importing grids into OpendTect).
    '''
    # NameRoot is the original name of the input file
    RasterImage = os.path.basename(inputFile)
    NameRoot,extension = os.path.splitext(RasterImage)

    # If dest is not given then keep original path to the raster file
    if dest == '':
        outPath = os.path.dirname(inputFile)
    else:
        outPath = dest

    # Output file name
    OutXYZFile = outPath + "\\" + NameRoot + ".xyz"

    # Convert data to array and get properties
    grid_data,nrows,ncols,header = rasterToArray(inputFile)
    [xll,yll,cellsize,nodata_value] = header # coordinates of cell center
    ymax = yll + (nrows - 1)*cellsize
    
    #### Create vectors ####
    # Generate indices where data exists
    data_indices = grid_data != nodata_value

    # 1-D arrays of coordinates
    x = np.arange(xll , xll+ncols*cellsize , cellsize)
    y = np.arange(ymax , yll - cellsize , -1*cellsize)

    # 2-D arrays of coordinates
    x_array , y_array = np.meshgrid(x, y)

    # Points arranged in two vectors
    X_vector = x_array[data_indices].flatten()
    Y_vector = y_array[data_indices].flatten()

    # Data arranged in one single vector
    values = grid_data[data_indices].flatten()
    
    # create optional Z column (zeros for importing in OpendTect)
    if addZcolumn:
        Z_vector = np.zeros_like(X_vector)

    #### Create XYZ file ####
    if addZcolumn:
        np.savetxt(OutXYZFile,np.array((X_vector,Y_vector,Z_vector,values)).T,fmt='%14.2f %14.2f %14.2f %.8g')
    else:
        np.savetxt(OutXYZFile,np.array((X_vector,Y_vector,values)).T,fmt='%14.2f %14.2f %.8g')    
        
    
#==============================================================
# shp2XY
#==============================================================
def shp2XY(inputSHP,onlyPoints=False,SQLstring=''):
    """
    Extracts XY coordinates from a shapefile.
    If points, returns an array with two columns [X,Y]
    If polylines or polygons, returns an array with three columns [lineNum,X,Y]
    """
    # open shapefile
    inShp = ogr.Open(inputSHP)
    # open layer in shape
    inLayer = inShp.GetLayer(0)
    # shapefile type
    shpType = inLayer.GetGeomType()
    
    # polylines or polygons
    if shpType in [ogr.wkbLineString,ogr.wkbPolygon]:
        ptsList = []
        ptsIDs = []
        # read points in each feature
        for feat in inLayer:
            geom = feat.GetGeometryRef()
            ptsList = ptsList + geom.GetPoints()
            ptsIDs = ptsIDs + geom.GetPointCount()*[feat.GetField(0)]
        
        if onlyPoints:
            XYarray = np.asarray(ptsList)
        else:
            XYarray = np.column_stack((np.asarray(ptsIDs),np.asarray(ptsList))) #three columns [lineNum,X,Y]
    
    # points
    elif shpType == ogr.wkbPoint:
        ptsList = []
        for feat in inLayer:
            geom = feat.GetGeometryRef()
            ptsList = ptsList + geom.GetPoints()
    
        XYarray = np.asarray(ptsList)
    # error
    else:
        print("\nError: This is not a shapefile!\n")
    
    # cleanup
    inShp = None
    
    return XYarray
    
#==============================================================================
#  projectPoints
#==============================================================================
def projectPoints(inputPoints,s_srs=4326,t_srs=23029):
    '''
    Reproject a set of points from one spatial reference to another.
    
    Parameters
    ----------    
    s_srs : Integer
        Spatial reference system of the input (source) file. Must be defined as a EPSG code,
        i.e. 23029 for ED50 / UTM Zone 29N
    t_srs : Integer
        Spatial reference system of the output (target) file. Must be defined as a EPSG code,
        i.e. 23029 for ED50 / UTM Zone 29N
        
    WGS84 = EPSG:4326
    '''
    # input SpatialReference
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(s_srs)
    
    # output SpatialReference
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(t_srs)
    
    # create the CoordinateTransformation
    try:
        coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
    except:
        # Raise error
        gdal.Error(1, 2, 'test error')
        
    # Loop through the points 
    outputPoints = []
    for XY in inputPoints:
        point = ogr.CreateGeometryFromWkt("POINT ({} {})".format(*XY))
        point.Transform(coordTrans)
        outputPoints.append([point.GetX(),point.GetY()])
        
    return np.asarray(outputPoints)

