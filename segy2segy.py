# -*- coding: utf-8 -*-
"""
:copyright: 2016 Geophysics Labs
:author: Joseph Barraud
:license: BSD License
"""
# import system modules
import os,argparse,re

# import numpy
import numpy as np

# import obspy
from obspy.io.segy.segy import _read_segy

# import our modules
import segyio,spatial

# coordinate positions in SEGY (lookup dictionary)
coordKeys = {'Source':['source_coordinate_x','source_coordinate_y'],
             'Group':['group_coordinate_x','group_coordinate_y'],
             'CDP':['x_coordinate_of_ensemble_position_of_this_trace',
                    'y_coordinate_of_ensemble_position_of_this_trace']  }

#==============================================================================
# convertScaler
#==============================================================================
def convertScaler(scaler,toRead=True): 
    '''              
    Convert scaler header in SEGY file to a multiplicative coefficient to be
    applied to coordinates.
    With option toRead True, the function returns a scaler for converting
    coordinates from a SEGY, while if False, the function returns a scaler to 
    write coordinates to SEGY file.
    The converted scaler must be used as a multiplicator.
    The scaler is normally defined in the trace header of the SEGY file at 
    position 71 ("scalar_to_be_applied_to_all_coordinates").
    The function works for both scalars and vectors.
    
    Usage
    -----
    The convention in SEGY files is that if the header is negative then it is
    applied as a multiplicator to the coordinates. For example, a scaler of -100
    transforms metres to centimetres. So when reading coordinates from a file,
    the coordinates must be divided by the absolute value of the scaler. It is 
    the reverse when the scaler is positive.
    In both cases (reading or writing) the coefficients returned by the function 
    must be multiplied by the coordinates.
    '''
    if np.any(scaler == 0):  # some SEGY files lack a proper definition of the scaler
        XYscale = 1.
    elif np.any(scaler < 0): # Positive scaler is multiplier, if negative is divisor
        XYscale = 1 / np.asfarray(np.abs(scaler))  # makes sure the coordinates are turned into floats
    else:
        XYscale = np.asfarray(np.abs(scaler))
        
    # change operation if scaler used to write coordinates
    if not toRead:
        XYscale = 1 / XYscale
        
    return XYscale
    
#==============================================================================
# segyXY
#==============================================================================
def segyXY(inSEGY,coord='Source',force_scaling=False,scaler=1.): 
    '''
    Extract XY coordinates of traces from SEGY file (navigation) and
    return a (ntraces,2) Numpy array.
    '''
    # retrieve keywords for coordinate headers
    Xcoord,Ycoord = coordKeys[coord]
        
    # open file and read it with obspy module (does not read the data)
    SH,STH = segyio.loadSHandSTH(inSEGY)
    ntraces = SH['ntraces']
    
    # define output
    XYarray = np.zeros((ntraces,2),dtype=np.float)
    
    # Retrieve coordinates 
    if not force_scaling: # get scaler from file 
        scaler = STH['scalar_to_be_applied_to_all_coordinates'] # this is a vector with ntraces elements
        XYscale = convertScaler(scaler,toRead=True)
    else:
        XYscale = scaler
            
    XYarray[:,0] = STH[Xcoord]*XYscale
    XYarray[:,1] = STH[Ycoord]*XYscale
    
    return XYarray,XYscale
 
#==============================================================================
# segy2segy
#==============================================================================
def segy2segy(inSEGY,outSEGY,s_srs=23029,t_srs=23030,s_coord='Source',t_coord='CDP',
              force_scaling=False,scaler=1.):
    '''
    Transform coordinates in SEGY files. This function makes use of the GDAL
    library for processing coordinates and projections. 
    
    Parameters
    ----------
    inSEGY : Filename
        Input SEGY file.
    outSEGY : Filename
        Output SEGY file.
    s_srs : Integer
        Spatial reference system of the input (source) file. Must be defined as
        a EPSG code, i.e. 23029 for ED50 / UTM Zone 29N
    t_srs : Integer
        Spatial reference system of the output (target) file. Must be defined
        as a EPSG code, i.e. 23030 for ED50 / UTM Zone 30N
    s_coord : String
        Position of the coordinates in the input SEGY file. The field corresponds 
        to a byte position in the binary file.
    t_coord : String
        Position of the coordinates in the output SEGY file. The field corresponds
        to a byte position in the binary file.
    force_scaling : Boolean
        If True, the program will use the number defined by the scaler argument
        to calculate the coordinates. Default is False and so the program will read
        the coordinate scaler from the SEGY file. It will use the same value for 
        writing coordinates in the new SEGY file.
    scaler : Float
        Used in combination with force_scaling. The scaler is defined like for 
        a SEGY file, for example -100 for dividing by 100 when reading.
        
    '''
    # read coordinates from input 
    XYarray,XYscale = segyXY(inSEGY,s_coord,force_scaling,scaler)
    
    # transform coordinates
    newXYarray = spatial.projectPoints(XYarray,s_srs,t_srs)
    
    # load SEGY object (headers only)
    seis = _read_segy(inSEGY,headonly=True)
    traces = seis.traces
    
    # get key for coordinates position in output file
    Xcoord,Ycoord = coordKeys[t_coord]
    
#    # read coordinate scaler and set new one for writing (assumes scaler is identical for all traces)
#    XYscale = traces[0].header.scalar_to_be_applied_to_all_coordinates
#    if XYscale == 0: # some SEGY files lack a proper definition of the scaler
#        scaler = 1.
#    elif XYscale < 0: # Positive scaler is multiplier, if negative is divisor
#        scaler = abs(XYscale)
#    else:
#        scaler = 1./abs(XYscale)
    
    # insert new coordinates in SEGY object
    for i,trace in enumerate(traces):
        trace.header.__setattr__(Xcoord,int(newXYarray[i,0]/XYscale))
        trace.header.__setattr__(Ycoord,int(newXYarray[i,1]/XYscale))
        
    # write output SEGY with new coordinates
    seis.write(outSEGY)
    
#==============================================================================
# Use module as a script (command line)
#==============================================================================
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Reproject SEGY coordinates.')
    parser.add_argument('input_file',
                        metavar='Input SEGY file or directory',
                        type=str,
                        help='The path to a SEGY file or a directory.')
    parser.add_argument('-o','--output',
                        metavar='Output SEGY file',
                        type=str,
                        nargs='?',
                        help='The path to the output SEGY file.')
    parser.add_argument('-s_srs', 
                        metavar='source spatial reference set',
                        type=int,
                        nargs='?',
                        default=23029,
                        help='The spatial reference of the input file.')
    parser.add_argument('-t_srs', 
                        metavar='target spatial reference set',
                        type=int,
                        nargs='?',
                        default=23030,
                        help='The spatial reference of the output file.')
    parser.add_argument('-s_coord', 
                        metavar='Source coordinate position',
                        type=str,
                        nargs='?',
                        default='Source',
                        help='Position of the coordinates in the input SEGY headers.')
    parser.add_argument('-t_coord', 
                        metavar='Target coordinate position',
                        type=str,
                        nargs='?',
                        default='CDP',
                        help='Position of the new coordinates in the output SEGY headers.')
    parser.add_argument('-fs', '--force_scaling', 
                        action='store_true',
                        help='If used, the program will use the number defined by the scaler \
                        argument to scale the coordinates.')
    parser.add_argument('-sc','--scaler',  metavar='scaler',
                        type=float,
                        nargs='?',
                        default=1.0,
                        help='Scaling factor applied to coordinates.')
    parser.add_argument('-s', '--suffix',
                        metavar='Suffix to output filename',
                        type=str,
                        nargs='?',
                        default='',
                        help='Suffix to add to the input filename to create the output filename. \
                        Only works if input is a directory.')
              
    args = parser.parse_args()
    infile = args.input_file

    # Process file or list of files
    if os.path.isfile(infile):
        print("Processing file: {}".format(os.path.basename(infile)))
        segy2segy(infile,args.output,args.s_srs,args.t_srs,
                  args.s_coord,args.t_coord,args.force_scaling,args.scaler)
        print("\nSEGY coordinates successfully projected.")
        
    elif os.path.isdir(infile):
        print("Reading SEGY files in {}".format(infile))
        for f in os.listdir(infile):
            if re.search("\\.se?gy$",f,flags=re.IGNORECASE):
                print("Processing file: {}".format(f))
                target = os.path.join(infile,f)
                segyName,extension = os.path.splitext(f)
                outfile = os.path.join(infile, segyName + args.suffix + '.sgy')
                segy2segy(target,outfile,args.s_srs,args.t_srs,
                          args.s_coord,args.t_coord,args.force_scaling,args.scaler)
        print("\nSEGY files successfully processed.")
        
    else:
        print("Error: Not a file or directory.")

    
    