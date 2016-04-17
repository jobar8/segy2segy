# -*- coding: utf-8 -*-
"""
:copyright: 2016 Geophysics Labs
:author: Joseph Barraud
:license: BSD License
"""
# import system modules
import os,datetime,math

# import numpy and matplotlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# import our modules
import segyio


#==============================================================================
# segyXY
#==============================================================================
def segyXY(inputFile,coord='Source',force_scaling=False,scaler=1.): 
    '''
    Extract XY coordinates of traces from SEGY file (navigation)
    Returns a (ntraces,2) array.
    '''
    # retrieve keywords for coordinate headers
    if coord == "Source":
        Xcoord = 'source_coordinate_x'
        Ycoord = 'source_coordinate_y'
    elif coord == "Group":
        Xcoord = 'group_coordinate_x'
        Ycoord = 'group_coordinate_y'
    else:
        Xcoord = 'x_coordinate_of_ensemble_position_of_this_trace'
        Ycoord = 'y_coordinate_of_ensemble_position_of_this_trace'
        
    # open file and read it with segpy
    SH,STH = segyio.loadSHandSTH(inputFile)

    ntraces = SH['ntraces']
    XYarray = np.zeros((ntraces,2),dtype=np.float)
    
    # Retrieve shotpoint coordinates 
    if not force_scaling:
        XYscale = STH['scalar_to_be_applied_to_all_coordinates'] # this is a vector with ntraces elements
        if np.any(XYscale == 0):
            scaler = 1.
        elif np.any(XYscale < 0): # Positive scaler is multiplier, if negative is divisor
            scaler = 1 / np.asfarray(np.abs(XYscale))  # makes sure the coordinates are turned into floats
        else:
            scaler = np.asfarray(np.abs(XYscale))
            
    XYarray[:,0] = STH[Xcoord]*scaler
    XYarray[:,1] = STH[Ycoord]*scaler
    
    return XYarray 
 
#==============================================================================
# shpToSEGY
#==============================================================================
def shpToSEGY(inSHP,outFilename,straight=False,trace_num=1000,value=1.,start=0,
         sampling_rate=4,samples_num=2501,scaler=10,doXYZ=False):

    # read coordinates from shapefile
    lineXY = spatial.shp2XY(inSHP,onlyPoints=True) # 2-column array
    
    if straight:
        tr_limits = [1,trace_num]
        traces = np.arange(1,trace_num+1)
        X_limits = [lineXY[0,0],lineXY[-1,0]]
        Y_limits = [lineXY[0,1],lineXY[-1,1]]
        X = np.interp(traces,tr_limits,X_limits)
        Y = np.interp(traces,tr_limits,Y_limits)
    else:        
        trace_num = len(lineXY)
        X = lineXY[:,0]
        Y = lineXY[:,1]
    
    # create SHin header if needed
    SHin = {}
    SHin['ntraces'] = trace_num
    SHin['ns'] = samples_num
    SHin['dt'] = sampling_rate * 1000 # in microseconds
    
    # create STHin headers
    STHin = {}
    STHin['SourceX'] = np.rint(X*scaler)
    STHin['SourceY'] = np.rint(Y*scaler)
    STHin["cdpX"] = np.rint(X*scaler)
    STHin["cdpY"] = np.rint(Y*scaler)
    STHin['DelayRecordingTime'] = np.ones(trace_num)*start
    STHin['LagTimeA'] = np.zeros(trace_num)
    STHin['LagTimeB'] = np.zeros(trace_num)
    STHin['SourceGroupScalar'] = np.ones(trace_num)*-1*scaler  # If positive use as a multiplier, if negative, use as a divisor.
    
    # create data
    data = value * np.ones((samples_num,trace_num))
    
    # create segy file
    misc.AddMessage("\nCreating " + outFilename)
    if not doXYZ:
        segy.writeSegy(outFilename,data,1000.*sampling_rate,STHin)
    else:
        segy.SegytoXYZ(data,SHin,STHin,outFilename) 
    misc.AddMessage("Done.")
    
    return
    
   
    
    