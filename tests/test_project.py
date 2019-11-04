#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('..')
import unittest
import matplotlib.pyplot as plt
import geoPackage as gp
import geoPackage.io as io
import geoPackage.raster as georaster
import h5py
import geopandas as gpd
from osgeo import gdal
from geoPackage.raster import Geoprocess
from geoPackage.dataprocess import normalize
import numpy as np
from geoPackage.visualize import layout


RASTER_PTH= '/Users/allen/Documents/Python/global_analysis/geotiffs/e1.tif'
VECTOR_PTH= '/Users/allen/Documents/Python/global_analysis/gisSrc/gauge_pnt_vector.shp'

class UnitTests(unittest.TestCase):

    def test_import(self):
        self.assertIsNotNone(gp)

    def test_project(self):
        self.assertTrue(True, "write more tests here")

    def test_io(self):
        h5_pth= '/Users/allen/Documents/Python/global_analysis/result.h5'
        ras_pth= '/Users/allen/Documents/Python/global_analysis/geotiffs/e1.tif'
        vec_pth= '/Users/allen/Documents/Python/global_analysis/gisSrc/gauge_pnt_vector.shp'
        h5= io.ReadFile(h5_pth)
        raster= io.ReadFile(ras_pth).raster
        vector= io.ReadFile(vec_pth).vector
        print(type(raster))
        # self.assertIsInstance(h5.layer, h5py.Dataset)
        self.assertEqual(h5.layer.rmse.shape, (1800,3600)), 'shape mistake'
        self.assertIsInstance(raster.layer, gdal.Dataset), 'raster type not correct'
        self.assertIsInstance(vector.layer, gpd.geodataframe.GeoDataFrame), 'vector type not correct'

        #Pass
    
    def test_raster(self):
        ras_pth= '/Users/allen/Documents/Python/global_analysis/geotiffs/total.tif'
        vec_pth= '/Users/allen/Documents/Python/global_analysis/gisSrc/gauge_pnt_vector.shp'
        raster= io.ReadFile(ras_pth).raster
        vector= io.ReadFile(vec_pth).vector
        # outraster= Geoprocess(raster).rasterClipByExt([-90,90,-45,45])
        # self.assertEqual(outraster.array.shape, (900,1800)) #pass clip raster by extent
        # outraster= Geoprocess(raster).rasterClipByMask(vector)
        # print(outraster.array.shape)     #Pass clip raster by mask
        # values= Geoprocess(raster).pointExtract(vector) # Pass point sampling 
        # print(values)
    
    def test_dataprocess(self):
        test_arr= np.random.randint(0,100, size=(10,10))
        # trans_arr= normalize(test_arr, 'minmax', feature_range=(0,5))   #Minmax passed
        # trans_arr= normalize(test_arr, 'normalizer', norm='l1')         #normalizer passed
        # trans_arr= normalize(test_arr, 'robust')                        #robust passed
        trans_arr= normalize(test_arr, 'mean')                          #mean std passed
        print(trans_arr)

    def test_visualize(self):
        raster= io.ReadFile(RASTER_PTH).raster
        fig= plt.figure()
        ax= fig.add_subplot(111)
        plot= layout(raster,save='temp.png')                                           #layout passed

    
if __name__ == '__main__':
    unittest.main()
    # raster= io.ReadFile(RASTER_PTH).raster
    # fig= plt.figure()
    # ax= fig.add_subplot(111)
    # plot= layout(raster, vmin=0, vmax=5)  