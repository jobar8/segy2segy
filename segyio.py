# -*- coding: utf-8 -*-
"""
Functions to read and write SEGY files with the Obspy module.
These functions are essentially interfaces to the segy class in Obspy.

:copyright: 2016 Geophysics Labs
:author: Joseph Barraud
:license: BSD License
"""

import numpy as np
#import obspy.io.segy.segy as seg
from obspy.io.segy.segy import _read_segy,BINARY_FILE_HEADER_FORMAT

# most useful trace header keys
STH_keys=[u'trace_sequence_number_within_line',
          u'trace_sequence_number_within_segy_file',
          u'scalar_to_be_applied_to_all_coordinates',
          u'source_coordinate_x',
          u'source_coordinate_y',
          u'group_coordinate_x',
          u'group_coordinate_y',
          u'coordinate_units',
          u'lag_time_A',
          u'lag_time_B',
          u'delay_recording_time',
          u'number_of_samples_in_this_trace',
          u'sample_interval_in_ms_for_this_trace',
          u'x_coordinate_of_ensemble_position_of_this_trace',
          u'y_coordinate_of_ensemble_position_of_this_trace',
          u'for_3d_poststack_data_this_field_is_for_in_line_number',
          u'for_3d_poststack_data_this_field_is_for_cross_line_number']

#===============================================================================
# loadSEGYHeader
#===============================================================================  
def loadSEGYHeader(segy,keys=None):
    '''
    Load SEGY file headers from a list
    '''
    # read binary header
    SHbin = segy.binary_file_header
    
    # load selection of most useful headers if none requested already
    if not keys:
        keys = [header[1] for header in BINARY_FILE_HEADER_FORMAT if header[2]]
        
    SH = {}
    for key in keys:
        SH[key] = SHbin.__getattribute__(key)
        
    return SH
        
#===============================================================================
# loadSEGYTraceHeader
#===============================================================================
def loadSEGYTraceHeader(traces,keys=None):
    """
    Load trace headers into Numpy arrays 
    """
    # load selection of most useful headers if none requested already
    if not keys:
        keys = STH_keys
        
    STH = {}
    for key in keys:
        STH[key] = np.hstack([t.header.__getattr__(key) for t in traces])
        
    return STH
    
#===============================================================================
# loadSEGY
#===============================================================================
def loadSEGY(filename,endian=None):
    """
    Read and load data and headers from SEGY file.
    
    Usage
    -----
    data,SH,STH = loadSEGY(filename)
    """
    
    # read file with obspy
    seis = _read_segy(filename,endian=endian)
    traces = seis.traces    
    ntraces = len(traces)
    
    # Load SEGY header
    SH = loadSEGYHeader(seis)
    SH['filename'] = filename
    SH["ntraces"] = ntraces
    # for compatibility with older segy module
    SH["ns"] = SH['number_of_samples_per_data_trace']
    SH["dt"] = SH['sample_interval_in_microseconds'] / 1000 # in milliseconds
    
    # Load all the Trace headers in arrays
    STH = loadSEGYTraceHeader(traces)
   
    # Load the data
    data = np.vstack([t.data for t in traces]).T
    
    return data,SH,STH

#===============================================================================
# loadSHandSTH
#===============================================================================
def loadSHandSTH(filename,endian=None):
    """
    Read and load only headers from SEGY file. No data is loaded, saving time and memory.
    
    Usage
    -----
    SH,STH = loadSHandSTH(filename)
    """
    # read file with obspy (headers only)
    seis = _read_segy(filename,endian=endian,headonly=True)
    traces = seis.traces    
    ntraces = len(traces)
    
    # Load SEGY header
    SH = loadSEGYHeader(seis)
    SH['filename'] = filename
    SH["ntraces"] = ntraces
    # for compatibility with older segy module
    SH["ns"] = SH['number_of_samples_per_data_trace']
    SH["dt"] = SH['sample_interval_in_microseconds'] / 1000 # in milliseconds
    
    # Load all the Trace headers in arrays
    STH = loadSEGYTraceHeader(traces)
    
    return SH,STH

#===============================================================================
# writeSTH
#===============================================================================
def writeSTH(seis,STH_Key,newSTH):
    """
    writeSTH(fileid,SH,STH_Key,newSTH,endian='>')

    Write new trace header in a SEGY file
    """
    traces = seis.traces
    for i,trace in enumerate(traces):
        trace.header.__setattr__(STH_Key,newSTH[i])
        
    
    
    
    
