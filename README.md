# segy2segy

A Python utility to manipulate SEGY files.

For this initial release, this tool has only one function: it allows you to transform coordinates in a SEGY from one coordinate system to another (a so-called reprojection). This is useful when you have a project mixing seismic surveys acquired over several UTM zones, or for those vintage datasets that make use of a local datum and you want everything in WGS84.

## Requirements

`segy2segy` needs the following libraries:

- The ability to read and write SEG-Y files is provided by [Obspy](http://docs.obspy.org).
- The transformations of coordinates and the projection calculations are handled by [GDAL](http://www.gdal.org/).

## Installation

### Dependencies

You need a working installation of Python (tested with version 2.7 and 3.7). I would recommend using [Anaconda](https://www.continuum.io/downloads) to automatise the installation of all the necessary packages.

Once you have downloaded and installed Anaconda, create a new environment like so:

```bash
conda config --add channels conda-forge
conda create -n segy obspy gdal
```

This creates an environment called `segy` that then needs to be activated with the command `conda activate segy`.

That's it, almost... On Windows at least, the installation of GDAL *may* fail to create the necessary environment variables (you need to check that with `set` on a command line where a conda environment has been activated). If you need to set it manually, follow these steps:

  1. Open the **System Settings** (on Windows 8 or 10, right-click the start (*Windows*) button and select System).
  2. Click the **Advanced System Settings** link in the left column.
  3. Click on the Advanced tab, then click the **Environment Variables** button near the bottom of that tab.
  4. In the "System variables" section and click the **New...** button.
  5. The name of the variable is `GDAL_DATA`, and the value is something like `C:\Anaconda2\Library\share\gdal`.

The path to the `GDAL_DATA` directory may vary depending on your installation. Look for a folder containing a lot of csv files, especially one called gcs.csv.

### Installation of segy2segy

To install segy2segy, simply use `git` to clone the repo, or download as a ZIP file and unzip it to your local drive. Then run the following:

```bash
cd segy2segy
python setup.py install
```

In addition to copying the files into your python environment, this will also make the script `segy2segy.py` executable so it is available anywhere on your system.

----------

## Running

You can either process of single SEGY file, or a bunch of them in a directory.

Example for a single file:

```bash
segy2segy.py \path\to\infile.segy -o \path\to\output.segy -s_srs 23030 -t_srs 23029
```

Note that, by default, the coordinates are read from the "Source" header (bytes 73 and 77) and are not overwritten. The new coordinates are written in the "CDP" header (bytes 181 and 185). The positions can be changed with the `-s_coord` and `t_coord` arguments.

Example for a directory:

```bash
segy2segy.py \path\to\folder -s_srs 23030 -t_srs 23029 -s_coord CDP -t_coord Source -s _UTM29
```

### Parameters

**inSEGY** : Input SEGY file or directory containing SEGY files.

**-o** ***outSEGY*** : Output SEGY file. If omitted, a suffix must be defined (see option -s). Files can't be overwritten.

**-s_srs** ***srs def*** : Spatial reference system of the input (source) file. Must be defined as a EPSG code, i.e. 23029 for ED50 / UTM Zone 29N. See [epsg.org](http://www.epsg.org) and [epsg.io](http://epsg.io) for a convenient tool to find these codes.

**-t_srs** ***srs def*** : Spatial reference system of the output (target) file. Must be defined as a EPSG code, i.e. 23030 for ED50 / UTM Zone 30N. See [epsg.org](http://www.epsg.org) and [epsg.io](http://epsg.io) for a convenient tool to find these codes.

**-s_coord** ***string*** : Position of the coordinates in the input SEGY file. This corresponds to a trace header. *Can be either 'Source', 'Group', or 'CDP'*. Default is Source.

**-t_coord** ***string*** : Position of the coordinates in the output SEGY file. This corresponds to a trace header. *Can be either 'Source', 'Group', or 'CDP'*. Default is CDP.

**-fs** ***boolean*** : Force Scaling (optional). If True, the program will use the number defined by the scaler argument to calculate the coordinates. Default is False and so the program will read the coordinate scaler from the SEGY file. It will use the same value for writing coordinates to the new SEGY file.

**-sc** ***scaler*** : Used in combination with Force Scaling (optional). The scaler is defined like for a SEGY file, for example -100 for dividing by 100 when reading.

**-s** ***string*** : String to add at the end of the input file name as a suffix to create the output file name.
