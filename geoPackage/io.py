import pandas as pd
import h5py
import numpy as np
from osgeo import gdal
import geopandas as gpd

class ReadFile:
    def __init__(self, filename):
        if filename.endswith('h5'):
            self.layer= H5(filename)
        # self.sample= h5py.File('test_sample.HDF5','r')
        elif filename.endswith('.tif') or filename.endswith('.tiff'):
            self.raster= Raster(filename)

        elif filename.endswith('.shp') or filename.endswith('.gpdk'):
            self.vector= Vector(filename)


class Raster():
    def __init__(self, filename):
        self.filename= filename
        self.layer= gdal.Open(filename)

    @property
    def types(self):
        return type(self.layer)

    @property
    def geotransform(self):
        return self.layer.GetGeoTransform()

    @property
    def crs(self):
        return self.layer.GetProjection()

    @property
    def array(self):
        return self.layer.ReadAsArray()

    @property
    def filepath(self):
        return self.filename

class Vector:
    def __init__(self, filename):
        self.filename= filename
        self.layer= gpd.read_file(filename)

    # @property
    # def geometry(self):
    #     '''Return X, Y'''
    #     return [list(self.layer.geometry)[0] for i in range(len(self.layer))], [list(self.layer.geometry)[1] for i in range(len(self.layer))]

    @property
    def head(self):
        return self.layer.head()

    @property
    def crs(self):
        return self.layer.crs

    @property
    def filepath(self):
        return self.filename

class H5:
    '''
    Typical NASA IMERG .HDF5 format, which includes attribute ['Grid/lons', 'Grid/lats', 'Grid/precipitationUncal',
    'Grid/precipitationCal'] ...
    '''
    def __init__(self, filename):
        self.layer= h5py.File(filename, 'r')
        self._attrs= self.layer.keys()

    @property
    def types(self):
        return type(self.layer)

    @property
    def rmse(self):
        if 'rmse' in self._attrs:
            return self.layer['rmse'][:]
        else:
            raise AttributeError('rmse not in %s!'%(list(self._attrs)))

    @property
    def mae(self):
        if 'mae' in self._attrs:
            return self.layer['mae'][:]
        else:
            raise AttributeError('mae not in %s!'%(list(self._attrs)))

    @property
    def prob(self):
        if 'prob' in self._attrs :
            return self.layer['prob'][:]
        else:
            raise AttributeError('prob not in %s!'%(list(self._attrs)))

    @property
    def lats(self):
        if 'lats' in self._attrs :
            return self.layer['Grid/lats'][:]
        else:
            raise AttributeError('lats not in %s!'%(list(self._attrs)))

    @property
    def lons(self):
        if 'lons' in self._attrs :
            return self.layer['Grid/lons'][:]
        else:
            raise AttributeError('lons not in %s!'%(list(self._attrs)))

class WriteFile:
    def __init__(self, field):
        '''
        Inputs:
        ---------------
        :field - numpy array with shape (rows, cols)
        '''
        self.field= field
        self.sampleFile= ReadFile('test_sample.HDF5').layer

    def write(self, dst):
        '''
        Inputs:
        ---------------
        :dst - str, file path to store new file
        '''
        lats= self.sampleFile.lats
        lons= self.sampleFile.lons
        pixelHeight= lats[1]- lats[0]
        pixelWidth= lons[1]- lons[0]
        rows, cols= self.field.shape
        originX= lons[0]
        originY= lons[1]

        driver = gdal.GetDriverByName('GTiff')
        outdata = driver.Create(dst, cols, rows, 1, gdal.GDT_Float32)
        outdata.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
        outdata.SetProjection("EPSG:4326")
        outdata.GetRasterBand(1).WriteArray(self.field)
