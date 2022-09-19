import h5py
import numpy as np
import os
from scipy.constants import find, physical_constants
import scipy
import cv2 as cv
import gdal

if __name__ == '__main__':
    file_name = '/mnt/d/Experiments/OMI_DataProcessing/Data/OMI_L3_NO2/OMI-Aura_L3-OMNO2d_2022m0901_v003-2022m0902t232524.he5'
    omi_file = h5py.File(file_name, 'r')
    no2_data = omi_file['/HDFEOS/GRIDS/ColumnAmountNO2/Data Fields/ColumnAmountNO2TropCloudScreened'][:]
    print(no2_data.shape, no2_data.dtype)
    out_directory = '/mnt/d/Experiments/OMI_DataProcessing/Data/Results/'
    if not os.path.exists(out_directory):
        os.makedirs(out_directory)
    out_name = out_directory + os.path.basename(file_name)[0:50] + '.tiff'
    no2_data_copy = no2_data
    no2_data_copy[no2_data_copy <= 0] = 0.0
    avo_const = scipy.constants.physical_constants['Avogadro constant'][0]  # 阿伏伽德罗常数
    no2_data_copy[no2_data_copy > 0] = no2_data_copy[no2_data_copy > 0] * 10 ** 10 / avo_const
    no2_data_flip = np.flip(no2_data_copy, axis=0)
    cv.imwrite(out_directory + 'no2_data_flip.tiff', no2_data_flip)
