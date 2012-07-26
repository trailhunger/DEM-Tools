'''
Created on 2012-07-06

@author: Edward Sargisson (edward@trailhunger.com)
'''

from sys import stderr
from math import floor, ceil
from ca_national_topographic_system.map_sheet import MapSheetFactory, MapSheet
from os import unlink, close, write, mkdir, chmod, makedirs
from os.path import basename, exists, isdir, join
from httplib import HTTPConnection
from urlparse import urlparse
from ftplib import FTP, error_perm
from osgeo import gdal, osr
from ca_national_topographic_system import CDEDCell
from tempfile import mkstemp
from zipfile import ZipFile
from hashlib import md5
import re
import os

osr.UseExceptions() # <-- otherwise errors will be silent and useless.

sref = osr.SpatialReference()
sref.ImportFromProj4('+proj=longlat +ellps=GRS80 +datum=NAD83 +no_defs')

def quads(minlon, minlat, maxlon, maxlat):
    """ Generate a list of southeast (lon, lat) for 0.5 * 0.25-degree quads of CDED 1:50000 data.
    """
    mapSheetFactory = MapSheetFactory();
    # CDED 1:50k longitude is divided into map sheets 0.5 deg wide
    lon = floor(minlon * 2.0) / 2.0
    while lon <= maxlon:
        lat = ceil(maxlat * 4.0) / 4.0
        while lat >= minlat:
            # We get the northwest point in the loop so we send the south east
            # point to get the map sheet
            print 'getting map sheet for lat={0}, lon={1}'.format(lat - .25, lon + .5)
            mapSheet = mapSheetFactory.getMapSheetBySouthEastCorner(lat - .25, lon + .5)
            for i in range(2):
                if i == 0:
                    cdedCell = CDEDCell(mapSheet, 'EAST')
                else:
                    cdedCell = CDEDCell(mapSheet, 'WEST')
                yield cdedCell
            #print lon, lat
            lat -= 0.25
        lon += 0.5
    
def datasource(cdedCell, source_dir):
    mapSheet = cdedCell.mapSheet
    mapSeriesDir = 'pub/geobase/official/cded/50k_dem/{0}'.format(mapSheet.series)
    mapSheetFileName = '{0}.zip'.format(mapSheet)
    mapSheetRetrCommand = 'RETR {0}'.format(mapSheetFileName)
    mapSheetFullPath = '{0}/{1}'.format(mapSeriesDir, mapSheetFileName)
    
    #
    # Create a local filepath
    #
    #s, host, path, p, q, f = urlparse(url)
    
    dem_dir = md5(mapSheetFullPath).hexdigest()[:3]
    dem_dir = join(source_dir, dem_dir)
    
    if (cdedCell.half == 'EAST'):
        dem_file = '{0}_deme.dem'.format(cdedCell.mapSheet)
    else:
        dem_file = '{0}_demw.dem'.format(cdedCell.mapSheet)
    dem_path = join(dem_dir, dem_file)
    dem_none = dem_path[:-4]+'.404'
    
    #
    # Check if the file exists locally
    #
    if exists(dem_path):
        return gdal.Open(dem_path, gdal.GA_ReadOnly)
    
    if exists(dem_none):
        return None

    if not exists(dem_dir):
        makedirs(dem_dir)
        chmod(dem_dir, 0777)
    
    assert isdir(dem_dir)
    
    #
    # Grab a fresh remote copy
    #
    print >> stderr, 'Retrieving', mapSheetFullPath, 'in DEM.CDED50k.datasource().'
    
    
    ftp = FTP('ftp2.cits.rncan.gc.ca')   # connect to host, default port
    ftp.login()               # user anonymous, passwd anonymous@
    ftp.cwd(mapSeriesDir)
    handle, zip_path = mkstemp(prefix='cded-', suffix='.zip')
    
    def write_to_handle(data):
        write(handle, data)
        
    try:
        ftp.retrbinary(mapSheetRetrCommand, write_to_handle)
        
        close(handle)
        
        #
        # Get the DEM out of the zip file
        #
        zipfile = ZipFile(zip_path, 'r')
        
        # The file names include a version so we have to look for it.
        matcher = re.compile('^.{6}_[0-9]{4}_dem[ew].dem$')
        extractList = filter(matcher.match, zipfile.namelist())
        
        #
        # Write the actual DEM
        #
        for extractFile in extractList:
            # We remove the edition and version identification from the file name
            # so that the cache lookup above will work.
            extract_path = join(dem_dir, extractFile[0:6] + extractFile[11:])
            dem_file = open(extract_path, 'w')
            dem_file.write(zipfile.read(extractFile))
            dem_file.close()
        
        chmod(dem_path, 0666)
    except error_perm:
        print >> stderr, 'action=datasourceFailed, mapSheetFullPath={0}, reason=ftpPermanentError'.format(mapSheetFullPath)
        # we're probably outside the coverage area
        print >> open(dem_none, 'w'), mapSheetFullPath
        return None
    # todo put this back
    #finally:
        #unlink(zip_path)
        
    #
    # The file better exist locally now
    #
    return gdal.Open(dem_path, gdal.GA_ReadOnly)

def datasources(minlon, minlat, maxlon, maxlat, source_dir):
    print 'minlon={0}, minlat={1}, maxlon={2}, maxlat={3}, source_dir={4}'.format(minlon, minlat, maxlon, maxlat, source_dir)
    """ Retrieve a list of CDED datasources overlapping the tile coordinate.
    """
    cdedCells = quads(minlon, minlat, maxlon, maxlat)
    #cellList = list(cdedCells)
    #print cellList
    sources = [datasource(cdedCell, source_dir) for (cdedCell) in cdedCells]
    return [ds for ds in sources if ds]
    

