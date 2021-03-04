# -*- coding: utf-8 -*-
"""
Calculates a latitude raster; each cell gets the latitude of its geographic location

For more information on ArcGIS Python Raster Functions, See:
https://github.com/Esri/raster-functions/wiki/PythonRasterFunction
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import arcpy
import numpy as np


# pylint: disable=invalid-name,unused-argument,no-self-use
# required for the class contract required by the executing framework.


class Latitude:
    """A Python Raster Function to calculate a latitude raster."""

    def __init__(self):
        self.name = "Latitude Function"
        self.description = "Provides a raster of the latitude of each cell in the input"
        self.sr = None
        self.cgs = None
        self.cellsize = None

    def getParameterInfo(self):
        """Describes all raster and scalar inputs to the raster function."""

        return [
            {
                "name": "input",
                "dataType": "raster",
                "value": None,
                "required": True,
                "displayName": "input raster",
                "description": ("Any georeferenced raster."),
            },
        ]

    def getConfiguration(self, **scalars):
        """Define how input rasters are read and the output raster constructed."""

        return {
            "inheritProperties": 2
            | 4
            | 8,  # inherit nodata, size, resample type, not pixel type.
            "invalidateProperties": 1
            | 2
            | 4
            | 8,  # reset everything on the parent dataset.
            "resampling": True,  # process at request resolution
        }

    def updateRasterInfo(self, **kwargs):
        """Define the location and dimensions of the output raster."""

        # extent and spatial reference are for map coordinates, not native image coords.
        extent = kwargs["input_info"]["extent"]
        self.cellsize = kwargs["input_info"]["cellSize"]  # Tuple(2x Floats)
        epsg = kwargs["input_info"]["spatialReference"]  # int EPSG code
        self.sr = arcpy.SpatialReference()
        self.sr.loadFromString("{0}".format(epsg))
        self.cgs = self.sr.GCS
        ymin, ymax = extent[1], extent[3]
        if self.cgs != self.sr:
            xmin, xmax = extent[0], extent[2]
            p = arcpy.PointGeometry(arcpy.Point(xmin, ymin), self.sr, False, False)
            q = p.projectAs(self.cgs)
            ymin = q.firstPoint.Y
            p = arcpy.PointGeometry(arcpy.Point(xmax, ymax), self.sr, False, False)
            q = p.projectAs(self.cgs)
            ymax = q.firstPoint.Y
        kwargs["output_info"]["bandCount"] = 1  # output is a single band raster
        kwargs["output_info"][
            "pixelType"
        ] = "f4"  # output is a 32bit floating point number
        kwargs["output_info"]["statistics"] = (
            {"minimum": ymin, "maximum": ymax},
        )  # we could get something from the input extents
        kwargs["output_info"]["histogram"] = ()
        return kwargs

    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        """Creates processed pixels given all scalar and raster inputs."""

        # pylint: disable=too-many-locals

        nRows, nCols = (
            shape if len(shape) == 2 else shape[1:]
        )  # dimensions of request pixel block
        # tlc is the row, column number, not the projected or geographic coordinates
        e = props["extent"]  # XMin, YMin, XMax, YMax values in the output coordinates
        h = props["height"]  # Number of rows in the parent raster
        w = props["width"]  # Number of cols in the parent raster
        dY = (e[3] - e[1]) / h  # cell height
        dX = (e[2] - e[0]) / w  # cell width
        # dX,dY = self.cellsize
        left_col, top_row = tlc
        yMax = e[3] - top_row * dY  # top-left corner of request on map
        if self.cgs != self.sr:
            xMin = e[0] + left_col * dX
            p = arcpy.PointGeometry(arcpy.Point(xMin, yMax), self.sr, False, False)
            q = p.projectAs(self.cgs)
            yMax = q.firstPoint.Y
        # Create a raster with 0 in the top row, 1 in the next row, etc.
        x = np.linspace(0, nCols - 1, nCols)
        y = np.linspace(0, nRows - 1, nRows)
        row_matrix = np.meshgrid(x, y)[1]

        latitude = yMax - row_matrix * dY
        pixelBlocks["output_pixels"] = latitude.astype(props["pixelType"], copy=False)
        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        """Define metadata attributes associated with the output raster dataset."""

        if bandIndex == -1:
            keyMetadata["datatype"] = "Processed"  # outgoing raster is now 'Processed'
        elif bandIndex == 0:
            keyMetadata[
                "wavelengthmin"
            ] = None  # reset inapplicable band-specific key metadata
            keyMetadata["wavelengthmax"] = None
        return keyMetadata
