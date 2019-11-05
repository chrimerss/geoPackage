#TODO
'''
Map plot
'''

from .taylor import TaylorDiagram
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from mpl_toolkits.basemap import Basemap
from .io import Raster


def layout(src, *arg, **kargs):
    '''
    Inputs:
    -----------------------
    :src - geoPackage.io.Raster object
    :kargs - {'cmap': plt.cm.colorbar object,
              'location': location of colorbar right/bottom,
              'remove_neg': bool; don't display negative values
              'cb_label': label of colorbar,
              'extent': base map extent 'global'/'local',
              'save': save path}

    Returns:
    -----------------------
    :map - Basemap object
    '''
    cmap= kargs.get('cmap', cm.rainbow)
    loc= kargs.get('location', 'bottom')
    cb_label= kargs.get('cb_label', '')
    extent= kargs.get('extent', 'global')
    dst= kargs.get('save', None)
    remove= kargs.get('remove_neg', True)
    figkargs= {key: kargs[key] for key in kargs.keys() if key in ['figsize', 'dpi']}
    meshplotkargs= {key: kargs[key] for key in kargs.keys() if key in ['vmin', 'vmax']}

    if not isinstance(src, Raster):
        raise ValueError('expected geo.Package.io.Raster object, but get %s'%type(src))

    ulx, xres, _, uly, _, yres  = src.geotransform
    m,n= src.array.shape
    xmin= ulx+ 0.5*xres
    ymin= uly+ 0.5*yres
    xmax = xmin + ((src.layer.RasterXSize-0.5) * xres)
    ymax = ymin + ((src.layer.RasterYSize-0.5) * yres)
    lons= np.linspace(xmin, xmax, n)
    lats= np.linspace(ymin, ymax, m)
    x,y = np.meshgrid(lons, lats)
    data= src.array
    if remove:
        data[data<0]= np.nan
    # print(xmin, xmax, ymin, ymax)

    if extent=='global':
        map_extent= (-180, 180, -90, 90)
    else:
        map_extent= (xmin, xmax, ymin, ymax)

    fig= plt.figure(**figkargs)
    m = Basemap(projection='cyl', resolution='l',
                llcrnrlat=map_extent[3], urcrnrlat=map_extent[2],
                llcrnrlon=map_extent[0], urcrnrlon=map_extent[1])
    m.drawcoastlines(linewidth=0.5)
    m.drawparallels(np.arange(-90, 91, 45), labels=[True,False,False,True], dashes=[10,10], linewidth=.5)
    m.drawmeridians(np.arange(-180, 180, 45), labels=[True,False,False,True], dashes=[10,10], linewidth=.5)
    # cmap= plt.get_cmap('rainbow') if cmap is None else plt.get_cmap(cmap)
    x,y = m(x,y)
    map = m.pcolormesh(x,y, data, cmap=cmap, **meshplotkargs)
    cb = m.colorbar(location=loc, pad='10%')
    cb.set_label(cb_label)
    if dst is not None:
        fig.savefig(dst)

    return map


def taylorPlot(*args, **kargs):
    '''
    Inputs:
    ------------------------
    :args
        data=arg[0]
        example
            [
                [std, cc, name]
            ]
    :kargs
        refstd=1.0, fig=None, rect=111, label='_', srange=(0, 1.5), extend=False
    '''
    data= args[0]
    markers= args[1]
    colors= args[2]
    dst= kargs.get('save', None)
    diakargs= {key: kargs[key] for key in kargs.keys() if key in ['refstd', 'fig', 'rect', 'label', 'srange', 'extend']}
    figkargs= {key: kargs[key] for key in kargs.keys() if key in ['figsize', 'dpi']}
    dia= TaylorDiagram(**diakargs)
    fig = plt.figure(**figkargs)
    for i, (stddev, corrcoef, name) in enumerate(data):
        dia.add_sample(stddev, corrcoef,
                       marker=markers[i], ms=10, ls='',
                       mfc=colors[i],mec=colors[i],
#                        mfc='k', mec='k',
                       label=str(name))
    contours = dia.add_contours(levels=5, colors='0.5')
    plt.clabel(contours, inline=1, fontsize=10, fmt='%.2f')

    dia.add_grid()                                  # Add grid
    dia._ax.axis[:].major_ticks.set_tick_out(True)  # Put ticks outward

    # Add a figure legend and title
    fig.legend(dia.samplePoints,
               [ p.get_label() for p in dia.samplePoints ],
               numpoints=1, prop=dict(size='large'), loc='upper right')
    cbar= fig.add_axes((0.5,0.9,.4,.01))
    cb = plt.colorbar(orientation='horizontal', mappable= plt.matplotlib.cm.ScalarMappable(cmap=plt.matplotlib.cm.rainbow), cax=cbar, fraction=0.70, shrink=0.7,ticks=[0,1,2,3,4])
    cb.set_label('Temperature')
    cb.ax.set_xticks(range(5))
    cb.ax.set_xticklabels(['cold','hot'])
#     fig.suptitle("Taylor diagram", size='x-large')  # Figure title
    if dst is not None:
        fig.savefig(dst, dpi=144)

    return dia
