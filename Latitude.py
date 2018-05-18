import numpy as np

"""
Calculates a latitude raster; each cell gets the latitude of its geographic location
"""

class Latitude():

    def __init__(self):
        self.name = "Latitude Function"
        self.description = ("Provides a raster of the latitude of "
                            "each cell in the input")


    def getParameterInfo(self):
        return [
            {
                'name': 'input',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "input raster",
                'description': ("Any georeferenced raster.")
            },
        ]


    def getConfiguration(self, **scalars):
        return {
          'inheritProperties': 2 | 4 | 8,            # inherit nodata, size, resample type, not pixel type. 
          'invalidateProperties':  1 | 2 | 4 | 8,    # reset everything on the parent dataset.
          'resampling': True,                        # process at request resolution
        }


    def updateRasterInfo(self, **kwargs):
        extent = kwargs['input_info']['extent']
        ymin, ymax = extent[1], extent[3]
        # may need to convert to geographic
        kwargs['output_info']['bandCount'] =  1     # output is a single band raster
        kwargs['output_info']['pixelType'] = 'f4'   # output is a 32bit floating point number
        kwargs['output_info']['statistics'] = ({'minimum': ymin, 'maximum':ymax}, )    # we could get something from the input extents
        kwargs['output_info']['histogram'] = ()
        return kwargs


    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        nRows, nCols = shape if len(shape) == 2 else shape[1:]      # dimensions of request pixel block
        # tlc is the row, column number, not the projected or geographic coordinates
        e = props['extent']      # XMin, YMin, XMax, YMax values in the output coordinates
        h = props['height']      # Number of rows in the of parent raster
        dY = (e[3]-e[1])/h       # cell height
        top_row = tlc[1]
        yMax = e[3]-top_row*dY    # top-left corner of request on map
        # we will cheat and give every cell in the block the same value.
        # FIXME: if projected, get the geographic value
        x = np.linspace(0, nCols-1, nCols)
        y = np.linspace(0, nRows-1, nRows)
        row_matrix = np.meshgrid(x,y)[1]  # has 0 in the top row, 1 in the next row, etc.
        latitude = yMax - row_matrix * dY
        pixelBlocks['output_pixels'] = latitude.astype(props['pixelType'], copy=False)
        return pixelBlocks


    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            keyMetadata['datatype'] = 'Processed'               # outgoing raster is now 'Processed'
        elif bandIndex == 0:
            keyMetadata['wavelengthmin'] = None                 # reset inapplicable band-specific key metadata
            keyMetadata['wavelengthmax'] = None
        return keyMetadata
