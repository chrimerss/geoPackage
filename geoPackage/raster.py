from osgeo import gdal, ogr
from affine import Affine
import numpy as np
from .io import ReadFile, Raster, Vector
import geopandas as gpd
import os


class Geoprocess(object):
    def __init__(self, raster):
        self.raster= raster

    def rasterClipByExt(self, extent, dst=None, nodata=-9999):
        '''
        Inputs:
        -----------------
        :extent - tuple; (xmin, xmax, ymin, ymax)
        :

        Output:
        -----------------
        NorasterCropedne - gdal.Dataset object
        '''
        if dst is None:
            if not os.path.exists('temp'):
                os.mkdir('temp')
            dst= 'temp/temp_file.tif'
        self._validateType(self.raster, 'raster')
        xmin, xmax, ymin, ymax= extent
        ds= gdal.Translate(dst, self.raster.filename, projWin=[xmin, ymin, xmax, ymax], noData=nodata, outputSRS= self.raster.geotransform)
        rasterCroped= ReadFile(dst).raster
        if os.path.exists('temp/temp_file.tif'):
            os.system('rm -r temp')

        return rasterCroped


    def rasterClipByMask(self, mask, dst=None, nodata=-9999):
        '''
        Inputs:
        -----------------
        :mask - geopandas object
        :dst -

        Output:
        -----------------
        :rasterCroped - gdal object
        '''
        self._validateType(self.raster, 'raster')
        self._validateType(mask, 'vector')
        # self._validateCRS(self.raster, mask)
        if dst is None:
            if not os.path.exists('temp'): os.mkdir('temp')
            out= 'temp/temp_file.tif'
        result= gdal.Warp(out, self.raster.filename, cutlineDSName= mask.filename, dstNodata=nodata)
        rasterCroped= ReadFile(out).raster
        if os.path.exists('temp/temp_file.tif'):
            os.system('rm -r temp')

        return rasterCroped

    def pointExtract(self, geopnts):
        '''
        Inputs:
        ------------------
        :raster - gdal object
        :geopnts - geopandas vector object
        '''

        self._validateType(self.raster, 'raster')
        self._validateType(geopnts, 'vector')
        geotrans= self.raster.geotransform
        forward_transform= Affine.from_gdal(*geotrans)
        values= {}
        for i in range(len(geopnts.layer)):
            res = ~forward_transform* np.array(geopnts.layer.geometry[i])
            x,y = int(res[0]), int(res[1])
            values['lat']= np.array(geopnts.layer.geometry[i])[0]
            values['lon']= np.array(geopnts.layer.geometry[i])[1]
            values['sample']= self._pointsampling(self.raster, x, y)

        return values

    #TODO
    def reshape(self, shape, dst=None, method='bilinear', proj='WGS84', noData=-9999):
        '''
        Inputs:
        ------------------
        :shape - tuple or list; (rows, cols)
        :method - str; ['bilinear' 'nearest', 'cubic', 'cubicspline', 'lanczos', 'average', 'mode']
        :dst - str; output file path
        :proj - str; projection
        :noData - int; 

        Outputs:
        ------------------
        :rasterReshaped - geoPackage.io.Raster object
        '''
        Xori, Xres, Xskew, Yori, Yskew, Yres= self.raster.geotransform
        rows, cols= self.raster.array
        Xfac, Yfac= cols/shape[1], rows/shape[0]
        rasterXres= Xres*Xfac
        rasterYres= Yres*Yfac
        if dst is None:
            if not os.path.exists('temp'): os.mkdir('temp')
            dst= 'temp/temp_file.tif'
        cmd= 'gdal_translate -ot Float32 -of GTIFF -a_sts %s -a_nodata %s -tr %s %s -r %s COMPRESS=Deflate %s'\
            %(proj, str(noData), rasterXres, rasterYres, method, dst)
        os.system(cmd)
        if os.path.exists('temp/temp_file.tif'):
            os.system('rm -r temp')
        rasterReshaped= ReadFile(dst).raster

        return rasterReshaped



    def latSplit(self, arr, del_deg=10, metric='sum'):
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
            results[name]= self._bandAgg(arr[:, del_arr:del_arr*2], metric)

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
        arr= raster.array
        if x<arr.shape[1] and y<arr.shape[0]:
            return arr[y,x]
        else:
            x= x-1
            return arr[y, x]

    def _validateType(self, src, dtype):
        types= {'raster': Raster,
                'vector': Vector,
                'array' : np.array,
                'list': list,
                'set': set,
                }
        if not isinstance(src, types[dtype]):
            raise ValueError('input type %s is not desired %s!'%(type(src), str(types[dtype])))

    def _validateCRS(self, *args):
        crs= None
        first=True
        for layer in args:
            if first:
                first= False
                crs= layer.crs
            else:
                if crs!=layer.crs: raise ValueError('%s CRS is not equal to %s'%(layer.crs, crs))
