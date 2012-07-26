'''Methods for dealing with Canada's National Topographic System (NTS) - 
specifically finding the NTS Map Sheet number for a latitude, longitude pair.
'''

from math import floor, ceil

class MapSheetFactory(object):
    '''
    Creates map_sheet objects
    '''
    map_area_lookup = [
                ['a', 'b', 'c', 'd'],
                ['h', 'g', 'f', 'e'],
                ['i', 'j', 'k', 'l'],
                ['p', 'o', 'n', 'm']
                ]
    map_sheet_lookup = [
                ['01', '02', '03', '04'],
                ['08', '07', '06', '05'],
                ['09', '10', '11', '12'],
                ['16', '15', '14', '13']
                ]

    '''
    Returns a Map Sheet representation for the map sheet specified by its
    south east corner. 
    '''
    def getMapSheetBySouthEastCorner(self, lat, lon):
        
        # the left most part of the series is based on the longitude
        series_west = floor((lon + 48.0) / 8.0 * -1)
        # the right most part of the series is based on the latitude
        series_north = abs(ceil((lat - 44.0) / 4.0))
        
        # A Series is divided into 16 Map Areas, marked sinusoidally from A to M starting from the south-east corner of the Series. Ex 96-M.
        # series orgin is the south east corner
        series_origin_lon = series_west * -8 - 48
        series_origin_lat = (series_north  - 1) * 4 + 44
        
        series_remainder_lon = lon - series_origin_lon
        series_remainder_lat = lat - series_origin_lat
        
        # series is 8 deg wide divided into 4
        map_area_x = int(floor(series_remainder_lon / 2 * -1))
        map_area_y = int(floor(series_remainder_lat))
        
#        print 'lat={0}, lon={1}, series_west={2}, series_north={3}, s_o_lat={4}, s_o_lon={5}, s_r_lat={6}, s_r_lon={7}, map_area_x={8}, map_area_y={9}'.format(lat, lon, series_west, series_north, series_origin_lat, series_origin_lon, series_remainder_lat, series_remainder_lon, map_area_x, map_area_y)
        
        map_area = self.map_area_lookup[map_area_y][map_area_x]
        
        map_area_origin_lon = map_area_x * 2
        map_area_origin_lat = map_area_y
        
        # A Map Area is divided into 16 Map Sheets, marked sinusoidally from 1 to 15 starting from the south-east corner of the Map Area. Ex 96-M-16.
        map_area_remainder_lon = series_remainder_lon + map_area_origin_lon 
        map_area_remainder_lat = series_remainder_lat - map_area_origin_lat
        
        # a map sheet is 0.5 deg wide and 0.25 deg high
        map_sheet_x = int((map_area_remainder_lon * -1.0) / 0.5)
        map_sheet_y = int(map_area_remainder_lat / 0.25)
        map_sheet = self.map_sheet_lookup[map_sheet_y][map_sheet_x]
        
        # print lat, lon, series_west, series_north, series_origin_lat, series_origin_lon, series_remainder_lat, series_remainder_lon, map_area_x, map_area_y, map_area, map_area_remainder_lat, map_area_remainder_lon, map_sheet_x, map_sheet_y, map_sheet
        # print  '{0:02.0f}{1:.0f}{2}{3}'.format(series_west, series_north, map_area, map_sheet)
        series_str = '{0:02.0f}{1:.0f}'.format(series_west, series_north)
        return MapSheet(series_str, map_area, map_sheet)
        
class MapSheet(object):
    def __init__(self, series, mapArea, mapSheet):
        self.series = series
        self.mapArea = mapArea
        self.mapSheet = mapSheet
        
    def __eq__(self, other):
        return self.series == other.series and self.mapArea == other.mapArea and self.mapSheet == other.mapSheet
    
    def __repr__(self):
        return '{0}{1}{2}'.format(self.series, self.mapArea, self.mapSheet)

class CDEDCell:
    ''' Represents a Cell from the Canada Digital Elevation Data. Every Map Sheet
    in the National Topographic System is divided into two halves: a western half and
    and eastern half. '''
    
    def __init__(self, mapSheet, half):
        self.mapSheet = mapSheet
        self.half = half
        
    def __eq__(self, other):
        return self.mapSheet == other.mapSheet and self.half == other.half
    
    def __repr__(self):
        return '{0}-{1}'.format(self.mapSheet, self.half)