# segy2segy
A Python utility to manipulate SEGY files.

For this initial release, this tool has only one function: it allows you to re-project coordinates in a SEG-Y from one coordinate system to another. This is useful when you have a project mixing seismic surveys acquired over different UTM zones, or for these vintage datasets that make use of a local datum and you want everything in WGS84.

Requirements
------------
The tool needs to read and write SEG-Y files, and this ability is provided by Obspy. The transformations of coordinates and the projection calculations are handled by GDAL.
