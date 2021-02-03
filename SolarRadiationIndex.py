# -*- coding: utf-8 -*-
"""
Calculates a Simple Solar Radiation Index

cos(l*pi/180) * cos(s*pi/180) + sin(l*pi/180)*sin(s*pi/180) * cos((180 - a)*pi/180)
where
s = slope raster (degrees; 0 = flat, 90 = vertical)
a = aspect raster (degrees, north = 0, clockwise increase)
l = latitude raster (degrees; 0 = equator, 90 = pole)

ref: https://pubs.er.usgs.gov/publication/70160322

Solar radiation is a potentially important covariate in many wildlife habitat studies,
but it is typically addressed only indirectly, using problematic surrogates like aspect
or hillshade. We devised a simple solar radiation index (SRI) that combines readily
available information about aspect, slope, and latitude. Our SRI is proportional to the
amount of extraterrestrial solar radiation theoretically striking an arbitrarily oriented
surface during the hour surrounding solar noon on the equinox. Because it derives from
first geometric principles and is linearly distributed, SRI offers clear advantages over
aspect-based surrogates. The SRI also is superior to hillshade, which we found to be
sometimes imprecise and ill-behaved.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np


class SolarRadiationIndex:
    def __init__(self):
        self.name = "Solar Radiation Index Function"
        self.description = (
            "Calculates a Simple Solar Radiation Index based on slope, "
            "aspect and latitude"
        )

    def getParameterInfo(self):
        return [
            {
                "name": "slope",
                "dataType": "raster",
                "value": None,
                "required": True,
                "displayName": "Slope raster",
                "description": (
                    "A raster of slope values for the terrain, in degrees "
                    "with 0 = flat and 90 = vertical"
                ),
            },
            {
                "name": "aspect",
                "dataType": "raster",
                "value": None,
                "required": True,
                "displayName": "Aspect raster",
                "description": (
                    "A raster of aspect value for the terrain, in degrees "
                    "with north = 0, increasing clockwise"
                ),
            },
            {
                "name": "latitude",
                "dataType": "raster",
                "value": None,
                "required": True,
                "displayName": "Latitude raster",
                "description": (
                    "A raster of latitude values for each cell, in degrees north "
                    "0 = equator and 90 = north pole"
                ),
            },
        ]

    def getConfiguration(self, **scalars):
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
        kwargs["output_info"]["bandCount"] = 1  # output is a single band raster
        kwargs["output_info"][
            "pixelType"
        ] = "f4"  # output is a 32bit floating point number
        kwargs["output_info"]["statistics"] = (
            {"minimum": 0.0, "maximum": 1.0},
        )  # we know something about the stats of the outgoing HeatIndex raster.
        kwargs["output_info"]["histogram"] = ()
        return kwargs

    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        slope = np.array(pixelBlocks["slope_pixels"], dtype="f4", copy=False)
        aspect = np.array(pixelBlocks["aspect_pixels"], dtype="f4", copy=False)
        latitude = np.array(pixelBlocks["latitude_pixels"], dtype="f4", copy=False)
        dr = np.pi / 180.0  # degree to radian
        latitude_rad = latitude * dr
        slope_rad = slope * dr
        t1 = np.cos(latitude_rad) * np.cos(slope_rad)
        t2 = np.sin(latitude_rad) * np.sin(slope_rad)
        t3 = np.cos((180.0 - aspect) * dr)
        index = t1 + t2 * t3
        pixelBlocks["output_pixels"] = index.astype(props["pixelType"], copy=False)
        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            keyMetadata["datatype"] = "Processed"  # outgoing raster is now 'Processed'
        elif bandIndex == 0:
            keyMetadata[
                "wavelengthmin"
            ] = None  # reset inapplicable band-specific key metadata
            keyMetadata["wavelengthmax"] = None
        return keyMetadata
