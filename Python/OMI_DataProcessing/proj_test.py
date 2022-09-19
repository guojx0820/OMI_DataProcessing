import gdal
import numpy as np
import scipy
from scipy.constants import find, physical_constants
import osr
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def array2raster(newRasterfn, rasterOrigin, pixelWidth, pixelHeight, array):
    cols = array.shape[1]  # obtain cols
    rows = array.shape[0]  # obtain rows
    originX = rasterOrigin[0]  # upper left corner X
    originY = rasterOrigin[1]  # upper left corner Y

    format = 'GTiff'
    driver = gdal.GetDriverByName(format)

    # create a single band raster
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Float32)
    # set GeoTransform parameters
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    # read band 1
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    # EPSG4326
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(4326)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()


def main(newRasterfn, rasterOrigin, pixelWidth, pixelHeight, array):
    reversed_arr = array[::-1]
    array2raster(newRasterfn, rasterOrigin, pixelWidth, pixelHeight, reversed_arr)


if __name__ == '__main__':
    file_name = '/mnt/d/Experiments/OMI_DataProcessing/Data/OMI_L3_NO2/OMI-Aura_L3-OMNO2d_2017m0101_v003-2019m1123t033050.he5'
    out_dir = '/mnt/d/Experiments/OMI_DataProcessing/Data/Results/'
    dataset = gdal.Open(file_name)
    sub_dataset = dataset.GetSubDatasets()
    no2_data = gdal.Open(sub_dataset[3][0]).ReadAsArray()[:]
    no2_data[no2_data > 2e+16] = np.nan
    no2_data[no2_data < 0] = np.nan
    avo_const = scipy.constants.physical_constants['Avogadro constant'][0]  # 阿伏伽德罗常数
    no2_data = no2_data * 10 ** 10 / avo_const
    # keep date in output files
    fn = os.path.splitext(os.path.basename(file_name))[0][19:28]

    fn = fn.replace('m', '_')
    print(fn)
    newRasterfn = os.path.join(out_dir, fn + '.tiff')
    # define upper left corner and pixel size
    rasterOrigin = (-180, 90)
    x_size = 0.25
    y_size = -0.25
    print('Writing ... ' + newRasterfn)
    main(newRasterfn, rasterOrigin, x_size, y_size, no2_data)
    print(no2_data)


