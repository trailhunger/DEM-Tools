'''
Created on 2012-07-08

@author: Edward
'''
import unittest
from ca_national_topographic_system import MapSheetFactory, MapSheet

class testMapSheetFactory(unittest.TestCase):


    def testShouldGet092j02WhenNearWhistlerBC(self):
        mapSheetFactory = MapSheetFactory();
        mapSheet = mapSheetFactory.getMapSheetBySouthEastCorner(50, -122.5)
        self.assertEquals(mapSheet, MapSheet('092', 'j', '02'))
        
    def testShouldGet092j03WhenNearWestsideWhistlerBC(self):
        mapSheetFactory = MapSheetFactory();
        mapSheet = mapSheetFactory.getMapSheetBySouthEastCorner(50, -123.0)
        self.assertEquals(mapSheet, MapSheet('092', 'j', '03'))
        
    def testShouldGet001n08WhenNearStJohnsNL(self):
        mapSheetFactory = MapSheetFactory();
        mapSheet = mapSheetFactory.getMapSheetBySouthEastCorner(47.25, -52)
        self.assertEquals(mapSheet, MapSheet('001', 'n', '08'))
        
    def testShouldGet030m11WhenNearTorontoOn(self):
        mapSheetFactory = MapSheetFactory();
        mapSheet = mapSheetFactory.getMapSheetBySouthEastCorner(43.5, -79)
        self.assertEquals(mapSheet, MapSheet('030', 'm', '11'))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()