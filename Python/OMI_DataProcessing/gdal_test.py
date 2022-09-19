import gdal
import numpy as np
import scipy
file = '/mnt/d/Experiments/OMI_DataProcessing/Data/Results/OMI-Aura_L3-OMNO2d_2022m0901_v003-2022m0902t232524_geo.tiff'
dataset = gdal.Open(file, gdal.GA_ReadOnly)
data=dataset.GetRasterBand(1).ReadAsArray()
print(np.max(data))
proj = dataset.GetProjection()
rows = dataset.RasterYSize
cols = dataset.RasterXSize
print(rows, cols)
print(proj)
print(dataset.RasterCount)
