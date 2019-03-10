"""
Functions to read and write SEGY files with the help of the ObsPy library.
These functions are essentially interfaces to the obspy.io.segy.segy sub-module.

:copyright: 2019 Geophysics Labs
:author: Joseph Barraud
:license: BSD License
"""
import numpy as np
from obspy.io.segy.segy import _read_segy, BINARY_FILE_HEADER_FORMAT

# most useful trace header keys
STH_keys = [u'trace_sequence_number_within_line',
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


#==============================================================================
# loadSEGYHeader
#==============================================================================
def loadSEGYHeader(seis, keys=None):
    '''
    Load headers from an ObsPy SEGYFile object.

    The headers are read from the so-called `binary header`. The function returns
    a default selection of useful headers or pick from an optional list (keys).

    Parameters
    ----------
    seis : ObsPy SEGYFile object
        This is created using the _read_segy function in obspy.io.segy.segy
    keys : list of strings
        List of headers to load. Must correspond to attributes as defined in ObsPy.
        See BINARY_FILE_HEADER_FORMAT dictionary.

    Returns
    -------
    SH : dictionary
        A dictionary with the values associated with the selected headers.

    '''
    # read binary header
    SHbin = seis.binary_file_header

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
def loadSEGYTraceHeader(traces, keys=None):
    '''
    Load trace headers from an ObsPy SEGYTrace object.

    The function returns a default selection of useful headers or pick from
    an optional list (keys).

    Parameters
    ----------
    traces : ObsPy SEGYTrace object
        This is created from a SEGYFile object.
    keys : list of strings
        List of trace headers to load. Must correspond to attributes as defined
        in ObsPy. See obspy.io.segy.header.TRACE_HEADER_FORMAT for a list of all
        available trace header attributes or the segyio.STH_keys for a shorter list.

    Returns
    -------
    STH : dictionary
        A dictionary with the values associated with the selected headers. The values
        are provided as Numpy arrays (vectors with ntraces elements).

    '''
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
def loadSEGY(filename, endian=None):
    """
    Read and load data and headers from a SEGY file.

    Usage
    -----
    data,SH,STH = loadSEGY(filename)
    """

    # read file with obspy
    seis = _read_segy(filename, endian=endian)
    traces = seis.traces
    ntraces = len(traces)

    # Load SEGY header
    SH = loadSEGYHeader(seis)

    # additional headers for compatibility with older segy module
    SH['filename'] = filename
    SH["ntraces"] = ntraces
    SH["ns"] = SH['number_of_samples_per_data_trace']
    SH["dt"] = SH['sample_interval_in_microseconds'] / 1000  # in milliseconds

    # Load all the Trace headers in arrays
    STH = loadSEGYTraceHeader(traces)

    # Load the data
    data = np.vstack([t.data for t in traces]).T

    return data, SH, STH


#===============================================================================
# loadSHandSTH
#===============================================================================
def loadSHandSTH(filename, endian=None):
    """
    Read and load headers from SEGY file. No data is loaded, saving time and memory.

    Usage
    -----
    SH, STH = loadSHandSTH(filename)
    """
    # read file with obspy (headers only)
    seis = _read_segy(filename, endian=endian, headonly=True)
    traces = seis.traces
    ntraces = len(traces)

    # Load SEGY header
    SH = loadSEGYHeader(seis)

    # additional headers for compatibility with older segy module
    SH['filename'] = filename
    SH["ntraces"] = ntraces
    SH["ns"] = SH['number_of_samples_per_data_trace']
    SH["dt"] = SH['sample_interval_in_microseconds'] / 1000  # in milliseconds

    # Load all the Trace headers in arrays
    STH = loadSEGYTraceHeader(traces)

    return SH, STH


#===============================================================================
# writeSTH
#===============================================================================
def writeSTH(seis, STH_Key, newSTH):
    """
    Write new trace header to a SEGY file, replacing the existing one.
    ***Not tested***
    """
    traces = seis.traces
    for i, trace in enumerate(traces):
        trace.header.__setattr__(STH_Key, newSTH[i])
