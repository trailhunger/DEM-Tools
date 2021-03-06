#!/usr/bin/env python
"""
"""
from optparse import OptionParser

from TileStache import getTile
from TileStache.Geography import SphericalMercator

from ModestMaps.Core import Coordinate
from ModestMaps.Geo import Location

from Hillup.data import SeedingLayer

parser = OptionParser(usage="""%prog [options] [zoom...]

Bounding box is given as a pair of lat/lon coordinates, e.g. "37.788 -122.349
37.833 -122.246". Output is a list of tile paths as they are created.

See `%prog --help` for info.""")

defaults = dict(demdir='source', tiledir='out', tmpdir=None, source='srtm-ned', bbox=(37.777, -122.352, 37.839, -122.086))

parser.set_defaults(**defaults)

parser.add_option('-b', '--bbox', dest='bbox',
                  help='Bounding box in floating point geographic coordinates: south west north east, default (%.3f, %.3f, %.3f, %.3f).' % defaults['bbox'],
                  type='float', nargs=4)

parser.add_option('-d', '--dem-directory', dest='demdir',
                  help='Directory for raw source elevation files, default "%(demdir)s".' % defaults)

parser.add_option('-t', '--tile-directory', dest='tiledir',
                  help='Directory for generated slope/aspect tiles, default "%(tiledir)s". This directory will be used as the "source_dir" for Hillup.tiles:Provider shaded renderings.' % defaults)

parser.add_option('-s', '--source', dest='source',
                  help='Data source for elevations. One of "srtm-ned" for SRTM and NED data or "ned-only" for US-only downsample NED, default "%(source)s".' % defaults,
                  choices=('srtm-ned', 'ned-only'))

parser.add_option('--tmp-directory', dest='tmpdir',
                  help='Optional working directory for temporary files. Consider a ram disk for this.')

def generateCoordinates(ul, lr, zooms, padding):
    """ Generate a stream of (offset, count, coordinate) tuples for seeding.
    """
    # start with a simple total of all the coordinates we will need.
    count = 0
    
    for zoom in zooms:
        ul_ = ul.zoomTo(zoom).container().left(padding).up(padding)
        lr_ = lr.zoomTo(zoom).container().right(padding).down(padding)
        
        rows = lr_.row + 1 - ul_.row
        cols = lr_.column + 1 - ul_.column
        
        count += int(rows * cols)

    # now generate the actual coordinates.
    # offset starts at zero
    offset = 0
    
    for zoom in zooms:
        ul_ = ul.zoomTo(zoom).container().left(padding).up(padding)
        lr_ = lr.zoomTo(zoom).container().right(padding).down(padding)

        for row in range(int(ul_.row), int(lr_.row + 1)):
            for column in range(int(ul_.column), int(lr_.column + 1)):
                coord = Coordinate(row, column, zoom)
                
                yield (offset, count, coord)
                
                offset += 1

if __name__ == '__main__':

    options, zooms = parser.parse_args()

    lat1, lon1, lat2, lon2 = options.bbox
    south, west = min(lat1, lat2), min(lon1, lon2)
    north, east = max(lat1, lat2), max(lon1, lon2)

    northwest = Location(north, west)
    southeast = Location(south, east)
    
    webmerc = SphericalMercator()

    ul = webmerc.locationCoordinate(northwest)
    lr = webmerc.locationCoordinate(southeast)

    for (i, zoom) in enumerate(zooms):
        if not zoom.isdigit():
            raise KnownUnknown('"%s" is not a valid numeric zoom level.' % zoom)

        zooms[i] = int(zoom)
    
    layer = SeedingLayer(options.demdir, options.tiledir, options.tmpdir, options.source)

    for (offset, count, coord) in generateCoordinates(ul, lr, zooms, 0):
        
        mimetype, content = getTile(layer, coord, 'TIFF', True)

        print coord
