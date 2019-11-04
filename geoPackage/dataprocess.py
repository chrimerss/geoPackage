import numpy as np
from sklearn.preprocessing import Normalizer, RobustScaler, MinMaxScaler, scale

def normalize(arr, *args, **kargs):
    '''
    Inputs:
    -----------------------
    :arr - numpy array;
    :arg - str
        minmax - normalize by min and max value;
        normalizer - scale by l1 or l2 norm;
        robust - scale by 25/75 percentile (remove outliers)
        mean - standardize by mean and unit variance

        details see: sklearn.preprocessing

    :kargs - dict keyword arguments

    
    Outputs:
    -----------------------
    :new_arr - transformed numpy array
    '''
    method= args[0]
    options= {'minmax': MinMaxScaler,
            'normalizer': Normalizer,
            'robust': RobustScaler,
            'mean': scale}
    # print(kargs)
    if method not in list(options.keys()):
        raise AttributeError('%s not in %s'%(method, options.keys()))
    elif method=='mean':
        return options[method](arr, **kargs)
    else:
        return options[method](**kargs).fit_transform(arr)
    
