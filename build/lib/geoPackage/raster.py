from osgeo import gdal
from affine import Affine
import numpy as np
from io import ReadFile
import geopandas as gpd
import rasterio
from rasterio.mask import mask

class GeoMan(object):
    def __init__(self):
        pass

    def readH5(self, filename):
        return ReadFile(filename)
    

    def rasterClip(self, raster, extent, dst):
        '''
        Inputs:
        -----------------
        :raster - str; file path points to geotiff data
        :extent - tuple; (xmin, xmax, ymin, ymax)
        :

        Output:
        -----------------
        :raster_cropepd - gdal object
        '''
        
        if not (src.endswith('.tif') or src.endswith('.tiff')):
            raise FileExistsError('expected file ends with .tif or .tiff')
        elif gdal.Open(src).ReadAsArray() is None:
            raise FileNotFoundError('please check the file path!')




    def pointExtract(self, raster, geopnts):
        '''
        Inputs:
        ------------------
        :raster - gdal object
        :geopnts - geopandas vector object
        '''

        self._validateType(raster, 'raster')
        self._validateType(vector, 'vector')
        geotrans= raster.GetGeoTransform()
        forward_transform= affine.Affine.from_gdal(*geotrans)
        values= {}
        for i in range(len(geopnts)):
            res = ~forward_transform* np.array(pnts.geometry[i])
            x,y = int(res[0]), int(res[1])
            values['lat']= pnts.geometry[i][0]
            values['lon']= pnts.geometry[i][1]
            values['sample']= self._pointsampling(raster, x, y)

        return values

    def maskExtract(self, raster, polygen):
        '''
        Inputs:
        --------------------
        :raster - gdal object
        :polygen - geopandas vector object

        Return:
        --------------------
        :maskedValues - geopandas vector object with values
        '''
        self._validateType(raster, 'raster')
        self._validateType(vector, 'vector')


    def latSplit(arr, del_deg=10, metric='sum'):
        '''
        Inputs:
        -----------------
        :arr - array (1800,3600)
        :del_deg - int, degree band that want to aggregate with

        Return:
        -----------------
        :results - dict, key of band name, value of metric over band
        '''
        results= {}
        self._validateType(arr, 'array')
        for lat in range(0,180,10):
            del_arr= lat*10
            if lat<900: name= '%sS-%sS'%(lat, lat+del_deg)
            elif lat>=900: name= '%sN-%sN'%(lat, lat+del_deg)
            results[name]= self._bandAgg(arr[:, del_arr:del_arr*2], metirc)

        return results

    def _bandAgg(self, arr, metric):
    '''
    Inputs:
    ---------------
    :arr - aray of shape (1800,3600)

    Return:
    ---------------
    :value - band aggregated results
    '''
    if metric=='sum':
        value= np.nansum(arr,axis=1)
    elif metric=='mean':
        value= np.nanmean(arr, axis=1)
    elif metric=='median':
        value= np.nanmedian(arr, axis=1)

    return value


    def _pointsampling(self, raster, x, y):
        arr= raster.ReadAsArray()
        if x<arr.shape[1] and y<arr.shape[0]:
            return arr[y,x]
        else:
            x= x-1
            return arr[y, x]

    def _validateType(self, src, dtype):
        types= {'raster': gdal.Dataset,
                'vector': gdp.geodataframe.GeoDataFrame,
                'array' : np.array,
                'list': list,
                'set': set,
                }
        if not isinstance(src, types[dtype]):
            raise ValueError('input type %s is not desired %s!'%(type(src), str(types[dtype])))
