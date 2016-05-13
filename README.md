# segy2segy
A Python utility to manipulate SEGY files.

For this initial release, this tool has only one function: it allows you to transform coordinates in a SEGY from one coordinate system to another (a so-called reprojection). This is useful when you have a project mixing seismic surveys acquired over several UTM zones, or for those vintage datasets that make use of a local datum and you want everything in WGS84.

##Requirements
segy2segy needs the following libraries:
  - The ability to read and write SEG-Y files is provided by [Obspy](http://docs.obspy.org). 
  - The transformations of coordinates and the projection calculations are handled by [GDAL](http://www.gdal.org/).

##Installation
###Dependencies
You need a working installation of Python (tested with version 2.7, but it should work with Python 3.x). I would recommend using [Anaconda](https://www.continuum.io/downloads) to automatise the installation of all the necessary packages. 

Once you have downloaded and installed Anaconda, start with ObsPy by typing on the command line:

    conda install -c obspy obspy

The `-c` option means that ObsPy is going to be installed from its own channel.

For GDAL, the latest version is available from the [conda-forge](https://conda-forge.github.io/) channel. So you can type:

    conda config --add channels conda-forge 
    conda install gdal

That's it, almost... On Windows at least, the installation of GDAL fails to create the necessary environment variables. This is a known issue in Anaconda. So you need to set it manually. This is quite easy:

  1. Open the **System Settings** (on Windows 8 or 10, right-click the bottom left corner of the screen and select System).
  2. Click the **Advanced System Settings** link in the left column.
  3. Click on the Advanced tab, then click the **Environment Variables** button near the bottom of that tab.
  4. In the "System variables" section and click the **New...** button. 
  5. The name of the variable is `GDAL_DATA`, and the value is `C:\Anaconda2\Library\share\gdal`.

The path to the `GDAL_DATA` directory may vary depending on your installation. Look for a folder containing a lot of csv files, especially one called gcs.csv.

###Installation of segy2segy
There is no installation required, just use `git` or download the ZIP file and unzip it to your local drive. 

----------

##Running
Open the command line and enter the directory where the segy2segy files have been downloaded.

You can either process of single SEGY file, or a bunch of them in a directory. Example for a single file:

    python segy2segy.py <\path\to\infile.segy> -o \path\to\output.segy -s_srs 23030 -t_srs 23029

###Parameters
  **inSEGY** : Filename
  
    Input SEGY file.
    
  **outSEGY** : Filename
  
    Output SEGY file.
    
  **s_srs** : Integer
  
    Spatial reference system of the input (source) file. Must be defined as
    a EPSG code, i.e. 23029 for ED50 / UTM Zone 29N
    
  **t_srs** : Integer
  
    Spatial reference system of the output (target) file. Must be defined
    as a EPSG code, i.e. 23030 for ED50 / UTM Zone 30N
    
  **s_coord** : String
  
    Position of the coordinates in the input SEGY file. The field corresponds 
    to a byte position in the binary file.
    
  **t_coord** : String
  
    Position of the coordinates in the output SEGY file. The field corresponds
    to a byte position in the binary file.
    
  **force_scaling** : Boolean
  
    If True, the program will use the number defined by the scaler argument
    to calculate the coordinates. Default is False and so the program will read
    the coordinate scaler from the SEGY file. It will use the same value for 
    writing coordinates in the new SEGY file.
    
  **scaler** : Float
  
    Used in combination with force_scaling. The scaler is defined like for 
    a SEGY file, for example -100 for dividing by 100 when reading.






