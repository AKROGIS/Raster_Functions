# Raster Functions

This repository houses modern image processing and analytic tools called raster functions.
Raster functions are lightweight and process only the pixels visible on your screen, in memory,
without creating intermediate files. They are powerful because you can chain them together and
apply them on huge rasters and mosaics on the fly.

In this repository, you will find useful function chains (\*.rft.xml) created by NPS and/or the
esri community.  The function chains dynamically apply either standard or custom raster processing
functions to your source raster to create a new raster in memory that can be displayed or exported
to disk.

 * Elevation Templates - This folder contains a number of function chains that are intended to
 be applied to a digital elevation model and return a raster represented by the name of the
 function chain.  These can be used on a variety of DEMs, but were originally designed to
 provide useful products from the Alaska SDMI 5m IFSAR elevation data.

You will also find custom raster functions that can be used in existing or new function chains.

 * AspectSlope.py - Create a map that simultaneously displays the aspect (direction) and slope(steepness)
 of a continuous surface, such as terrain as represented in a digital elevation model (DEM).
 * Latitude.py - Calculates a latitude raster; each cell gets the latitude of its geographic location.
 * SolarRadiationIndex.py - Calculates a Simple Solar Radiation Index, using the slope, aspect and
 latitude of a raster cell.
 * VectorRuggednessMeasure.py - Calculates a Vector Ruggedness Measure using the slope and aspect of
 a cell and its neighbors.

See the comments in the individual python files for more information on the processing methodology.

This repo is similar to the [raster-functions repo](https://github.com/Esri/raster-functions)
provided by [Esri](https://www.esri.com/en-us/home).  Please see that repo for additional
raster functions and function chains.  That repo also has a lot of good information on
developing and using raster functions and function chains.
