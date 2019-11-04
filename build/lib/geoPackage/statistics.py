"""
This function implements block-wise calculation for computing some statistics
"""
import h5py
import numpy as np
import os
import datetime
import scipy
import itertools

class Block:
    '''
    This block iteration calculates basic statistics for 20 yrs data

    Attributes:
    ------------------
    :window_size - Tuple like; by default 10x10
    :early_folders - str; where the early run are stored
    :late_folders - str; where the late runs are stored
    :lon_lens - int; length of longitudes
    :lat_lens - int; length of latitudes

    Methods:
    ------------------
    main_loop() - controls block
    file_loop() - controls IO
    retrieve() - extract information from HDF5 file
    fileDateAssert() - assertion for dates
    dataAssert() - assertion for data to have the expected dimension
    dataClean() - preprocess for data, normally fill no data with nan
    '''

    def __init__(self, window_size=(10,10)):

        self.window_size= window_size
        self.early_folders= [str(i) for i in range(2000, 2020)]
        self.final_folders= [str(i)+'_final' for i in range(2000, 2020)]
        self.lon_lens= 3600
        self.lat_lens= 1800
        dt = np.dtype([('pearsonr', np.float16),
                       ('std', np.float16),
                       ('volume_loss', np.float32),
                       ('normRMSE', np.float16),
                       ('RMSE', np.float32),
                       ('MAE', np.float32),
                       ('normMAE', np.float32)])
        self.stats= np.zeros((self.lat_lens, self.lon_lens), dtype=dt)

    def main_loop(self, threads=10):
        pool= multiprocessing.Pool(threads)
        m,n= self.window_size
        early_arr= np.zeros((m,n,1), dtype=np.float32)
        late_arr= early_arr.copy()
        num_m, num_n= self.lat_lens//m; self.lon_lens//n
        stats= Stats()
        for i in range(num_m):
            for j in range(num_n):
                for block_arr_early, block_arr_late in self.file_loop(i,j):
                    early_arr= np.stack([early_arr, block_arr_early[:,:,np.newaxis]], axis=2)
                    late_arr= np.stack([late_arr, block_arr_late[:,:,np.newaxis]], axis=2)
                _,_,t= early_arr.shape
                early_arr= early_arr.reshpae(m*n,t)
                early_arr= [early_arr[i,:] for i in range(m*n)]
                late_arr= late_arr.reshape(m*n,t)
                late_arr= [ late_arr[i,:] for i in range(m*n)]
                r, mae, normMAE, rmse, normRMSE= pool.starmap(stats.main, zip(early_arr, late_arr))
                self.stats['pearsonr'][i*m:*(i+1)*m, j*n:*(j+1)*n]= np.array(r).reshape(m,n)
                self.stats['normRMSE'][i*m:*(i+1)*m, j*n:*(j+1)*n]= np.array(normRMSE).reshape(m,n)
                self.stats['mae'][i*m:*(i+1)*m, j*n:*(j+1)*n]= np.array(mae).reshape(m,n)
                self.stats['normMAE'][i*m:*(i+1)*m, j*n:*(j+1)*n]= np.array(normMAE).reshape(m,n)
                self.stats['rmse'][i*m:*(i+1)*m, j*n:*(j+1)*n]= np.array(rmse).reshape(m,n)


    def file_loop(self, block_i, block_j):
        m,n= self.window_size
        for folder in self.early_folders:
            days= sorted(os.listdir(os.path.join(folder)))
            for day in days:
                dst_early= os.path.join(folder, day)
                dst_late= os.path.join(folder+'_final', day)
                files_early= os.listdir(dst_early)
                files_late= os.listdir(dst_late)
                if len(files_early)!=48 and len(files_late)!=48:
                    raise FileNotFoundError('expected 48 files inside one day folder!, but got %d, %d for early and late'%(len(files_early), len(files_late)))
                else:
                    for i, f in enumerate(sorted(files_early)):
                        early_h5= f
                        late_h5= files_late[i]
                        self.fileDateAssert(early_h5, late_h5)
                        early_map, late_map= self.retrieve(h5_early, late_h5)

                        yield early_map[block_i*m:*(block_i+1)*m, block_j*n:*(block_j+1)*n], late_map[block_i*m:*(block_i+1)*m, block_j*n:*(block_j+1)*n]


    def retrieve(self, h5_early, h5_late):
        """
        :file - .HDF5 file
        """
        early_map= np.array(h5py.File(h5_early, 'r')['Grid/precipitationCal']).transpose().squeeze()
        late_map= np.array(h5py.File(h5_late, 'r')['Grid/precipitationCal']).transpose().squeeze()
        self.dataAssert(early_map, late_map)
        self.dataClean(early_map, late_map)

        return early_map, late_map

    def fileDateAssert(self, file1, file2):
        '''
        According to fine name convention, e.g. 20000601-S000000-E002900.HDF5
        '''
        date1, time1= file1.split('-')[:2]
        time1= time1[1:]
        date2, time2= file2.split('-')[:2]
        time2= time2[1:]
        datetime1= datetime.datetime.strptime(date1+time1, format="%Y%m%d%H%M%S")
        datetime2= datetime.datetime.strptime(date2+time2, format="%Y%m%d%H%M%S")
        if datetime1!= datetime2:
            raise ValueError('two map dates are inconsistent, one is %s, the other is %s'%(str(datetime1), str(datetime2)))

    def dataAssert(self, *args):
        for arg in args:
            assert arg.shape==(1800,3600), 'expected map size (1800,3600), but got %s'%(str(arg.shape))

    def dataClean(self, *args):
        for arg in args:
            arg[arg<0]= np.nan

        return args

class Stats:
    """
    This module helps to calculate basic statistics e.g. pearson r, MAE, normalized MAE,
    RMSE, normalized RMSE and total loss

    Note:
        x,y in these methods stand for early run and final run respectively. don't mess up the order
    """

    def __init__(self):
        pass

    def main(self, *args, metrics='all'):
        arr1= args[0]
        arr2= args[1]
        if metrics=='all':
            r= self.pearsonr(self.arr1, self.arr2)
            mae= self.mae(self.arr1, self.arr2)
            normMAE= self.normMAE(self.arr1, self.arr2)
            rmse= self.rmse(self,arr1, self.arr2)
            normRMSE= self.normRMSE(self.arr1, self.arr2)

            return r, mae, normMAE, rmse, normRMSE

    def pearsonr(self, x, y):
        x,y= self.protection_nan(x,y)
        if len(x)<2 or len(y)<2:
            return np.nan
        else:
            return scipy.stats.pearsonr(x,y)

    def mae(self, x, y):
        x, y= self.protection_nan(x,y)
        if len(x)==0 or len(y)==0:
            return np.nan
        else:
            return np.abs(x-y).sum()/len(x)

    def normMAE(self, x, y):
        x,y= self.protection_nan(x, y)
        if len(x)==0 or len(y)==0:
            return np.nan
        elif y.mean()==0:
            return np.nan
        else:
            return np.abs(x-y).sum()/y.mean()

    def rmse(self, x, y):
        x,y= self.protection_nan(x,y)
        if len(x)==0 or len(y)==0:
            return np.nan
        else:
            return (((x-y)**2).mean())**0.5

    def normRMSE(self, x, y):
        x, y= self.protection_nan(x, y)
        if len(x)==0 or len(y)==0:
            return np.nan
        elif y.mean()==0:
            return np.nan
        else:
            return ((((x-y)/y.mean())**2).mean())**0.5

    def volume_loss(self, x, y):
        # total volume deficit, final run - early run
        x,y= self.protection_nan(x,y)
        if len(x)==0 or len(y)==0:
            return np.nan
        else:
            return y.sum()-x.sum()

    def protection_nan(self, x, y):
        #remove corresponding nans
        ind_x= np.isnan(x)
        ind_y= np.isnan(y)
        intersection= ~ind_x * ~ ind_y

        return x[intersection], y[intersection]
