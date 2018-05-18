import numpy as np
from scipy import ndimage

"""
Calculates a Vector Ruggedness Measure

Input:
slope raster (degrees; 0 = flat, 90 = vertical)
aspect raster (degrees, north = 0, clockwise increase)
Neighborhood size (int describing a square that is size by size pixels)

This tool measures terrain ruggedness by calculating the vector ruggedness measure
described in Sappington, J.M., K.M. Longshore, and D.B. Thomson. 2007. Quantifiying
Landscape Ruggedness for Animal Habitat Anaysis: A case Study Using Bighorn Sheep in
the Mojave Desert. Journal of Wildlife Management. 71(5): 1419 -1426.

ref: http://www.bioone.org/doi/abs/10.2193/2005-723

This Raster Function was based on an arcpy tool originally written by Mark Sappington
that was last updated 12/17/2010

From the abstract: 
Terrain ruggedness is often an important variable in wildlife habitat models.
Most methods used to quantify ruggedness are indices derived from measures of
slope and, as a result, are strongly correlated with slope. Using a Geographic
Information System, we developed a vector ruggedness measure (VRM) of terrain
based on a geomorphological method for measuring vector dispersion that is less
correlated with slope...
"""

class VectorRuggednessMeasure():

    def __init__(self):
        self.name = "Vector Ruggedness Measure"
        self.description = ("Calculates the ruggedness of the terrain by measuring "
                            "the amount of dispersal of the normal vectors "
                             "of the terrain in the neighborhood of a location")
        self.neighborhood_size = 3

    def getParameterInfo(self):
        return [
            {
                'name': 'slope',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Slope raster",
                'description': ("A raster of slope values for the terrain, in degrees "
                                "with 0 = flat and 90 = vertical")
            },
            {
                'name': 'aspect',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Aspect raster",
                'description': ("A raster of aspect value for the terrain, in degrees "
                                "with north = 0, increasing clockwise")
            },
            {
                'name': 'size',
                'dataType': 'numeric',
                'value': 3,
                'required': False,
                'displayName': "Neighborhood Size",
                'description': ("A square of size x size  is considered to determine "
                                "the ruggedness at the center of the square.")
            },
        ]


    def getConfiguration(self, **scalars):
        return {
          'inheritProperties': 2 | 4 | 8,          # inherit nodata, size, resample type, not pixel type. 
          'invalidateProperties':  1 | 2 | 4 | 8,  # reset everything on the parent dataset.
          'resampling': True,                      # process at request resolution
        }


    def updateRasterInfo(self, **kwargs):
        self.neighborhood_size = kwargs.get('size', 3)

        kwargs['output_info']['bandCount'] =  1     # output is a single band raster
        kwargs['output_info']['pixelType'] = 'f4'   # output is a 32bit floating point number
        kwargs['output_info']['statistics'] = ({'minimum': 0.0, 'maximum': 1.0}, )  # we know something about the range of the outgoing raster.
        kwargs['output_info']['histogram'] = ()
        return kwargs


    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        slope = np.array(pixelBlocks['slope_pixels'], dtype='f4', copy=False)[0] # limit to first (only) band
        aspect = np.array(pixelBlocks['aspect_pixels'], dtype='f4', copy=False)[0]
        dr = np.pi/180.0  # degree to radian
        slope_rad = slope * dr
        aspect_rad = aspect * dr
        xy = np.sin(slope_rad)
        z = np.cos(slope_rad)
        x = np.where(aspect == -1, 0.0, np.sin(aspect_rad)*xy)
        y = np.where(aspect == -1, 0.0, np.cos(aspect_rad)*xy)
        kernel = np.ones((self.neighborhood_size, self.neighborhood_size))
        kernel_size = self.neighborhood_size * self.neighborhood_size
        # focal statistics sum (used in the original tool) is the same as an image
        #   convolution with an all ones in the kernel.  I.e. the sum all the cells
        #   overlapping the kernel with a weight of 1 on each cell.
        # TODO: how should we handle the boundary condition
        #   cells outside the boundary will always have a zero value -- no contribution
        # FIXME: need to handle nodata
        #   original tool returned nodata if any cell in the neighborhood was nodata
        x_sum = ndimage.convolve(x, kernel) #, mode='constant', cval=0.0)
        y_sum = ndimage.convolve(y, kernel) #, mode='constant', cval=0.0)
        z_sum = ndimage.convolve(z, kernel) #, mode='constant', cval=0.0)
        total = np.sqrt(x_sum*x_sum + y_sum*y_sum + z_sum*z_sum)
        ruggedness = 1.0 - (total/kernel_size)
        pixelBlocks['output_pixels'] = ruggedness.astype(props['pixelType'], copy=False)
        return pixelBlocks


    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            keyMetadata['datatype'] = 'Processed'               # outgoing raster is now 'Processed'
        elif bandIndex == 0:
            keyMetadata['wavelengthmin'] = None                 # reset inapplicable band-specific key metadata
            keyMetadata['wavelengthmax'] = None
        return keyMetadata
