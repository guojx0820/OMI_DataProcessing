import numpy as np
import gdal
import os
import scipy
from scipy.constants import find, physical_constants
import osr
import time


class OMI_NO2_AverageCalculating:
    def __init__(self, file_name, output_path, raster_origin, pixel_width, pixel_height, month_out, season_out,
                 year_out):
        self.file_name = file_name
        self.output_path = output_path
        self.raster_origin = raster_origin
        self.pixel_width = pixel_width
        self.pixel_height = pixel_height
        self.month_out = month_out
        self.season_out = season_out
        self.year_out = year_out
        # 月份储存数组初始化
        self.total_month_data = np.zeros((720, 1440, 12), dtype=np.float64, order='C')
        self.valid_month_data = np.zeros((720, 1440, 12), dtype=np.float64, order='C')
        self.avr_month_data = np.zeros((720, 1440, 12), dtype=np.float64, order='C')
        # 季节储存数组初始化
        self.total_season_data = np.zeros((720, 1440, 4), dtype=np.float64, order='C')
        self.valid_season_data = np.zeros((720, 1440, 4), dtype=np.float64, order='C')
        self.avr_season_data = np.zeros((720, 1440, 4), dtype=np.float64, order='C')
        # 年储存数据初始化
        self.total_year_data = np.zeros((720, 1440, 2), dtype=np.float64, order='C')
        self.valid_year_data = np.zeros((720, 1440, 2), dtype=np.float64, order='C')
        self.avr_year_data = np.zeros((720, 1440, 2), dtype=np.float64, order='C')

    def _cal_avr_(self):
        for i_file in self.file_name:
            print(i_file)
            dataset = gdal.Open(i_file)
            sub_dataset = dataset.GetSubDatasets()
            data_temp = gdal.Open(sub_dataset[3][0]).ReadAsArray()[:]
            data_temp_fix = data_temp
            avo_const = scipy.constants.physical_constants['Avogadro constant'][0]
            data_temp_fix[data_temp_fix <= 0.0] = 0.0
            data_temp_fix[data_temp_fix > 0.0] = data_temp_fix[data_temp_fix > 0.0] * 10.0 ** 10.0 / avo_const
            data_temp_fix = np.flip(data_temp_fix, axis=0)  # 翻转
            # 截取文件日期
            layer_i = int(os.path.splitext(os.path.basename(i_file))[0][24:26]) - 1
            # 月份
            self.total_month_data[:, :, layer_i] += data_temp_fix
            self.valid_month_data[:, :, layer_i] += np.int64(data_temp_fix > 0)
            # print(self.valid_month_data[:, :, layer_i].shape)
            # 季节
            if layer_i >= 2 and layer_i <= 4:
                self.total_season_data[:, :, 0] += data_temp_fix
                self.valid_season_data[:, :, 0] += np.int64(data_temp_fix > 0)
            elif layer_i >= 5 and layer_i <= 7:
                self.total_season_data[:, :, 1] += data_temp_fix
                self.valid_season_data[:, :, 1] += np.int64(data_temp_fix > 0)
            elif layer_i >= 8 and layer_i <= 10:
                self.total_season_data[:, :, 2] += data_temp_fix
                self.valid_season_data[:, :, 2] += np.int64(data_temp_fix > 0)
            elif layer_i >= 11 or layer_i <= 1:
                self.total_season_data[:, :, 3] += data_temp_fix
                self.valid_season_data[:, :, 3] += np.int64(data_temp_fix > 0)
            # 年
            year_start = 2017
            year_i = int(os.path.splitext(os.path.basename(i_file))[0][19:23])
            self.total_year_data[:, :, (year_i - year_start)] += data_temp_fix
            self.valid_year_data[:, :, (year_i - year_start)] += np.int64(data_temp_fix > 0)
            # print('*' * 50)
        self.valid_month_data[self.valid_month_data == 0] = 1.0
        self.avr_month_data = self.total_month_data / self.valid_month_data
        self.valid_season_data[self.valid_season_data == 0] = 1.0
        self.avr_season_data = self.total_season_data / self.valid_season_data
        self.valid_year_data[self.valid_year_data == 0] = 1.0
        self.avr_year_data = self.total_year_data / self.valid_year_data
        # 给图像设置投影信息并输出
        for i_month in range(self.avr_month_data.shape[2]):
            raster_fn_month = self.output_path + 'month_avr_' + self.month_out[i_month] + '.tiff'
            self._array2raster_(raster_fn_month, self.avr_month_data[:, :, i_month])
        for i_season in range(self.avr_season_data.shape[2]):
            raster_fn_season = self.output_path + 'season_avr_' + self.season_out[i_season] + '.tiff'
            self._array2raster_(raster_fn_season, self.avr_season_data[:, :, i_season])
        for i_year in range(self.avr_year_data.shape[2]):
            raster_fn_year = self.output_path + 'year_avr_' + self.year_out[i_year] + '.tiff'
            self._array2raster_(raster_fn_year, self.avr_year_data[:, :, i_year])

    def _array2raster_(self, raster_fn, array):
        # 获取数据的行和列
        cols = array.shape[1]
        rows = array.shape[0]
        # 获取数据左上角坐标值
        origin_x = self.raster_origin[0]
        origin_y = self.raster_origin[1]
        format = 'GTiff'
        driver = gdal.GetDriverByName(format)

        out_raster = driver.Create(raster_fn, cols, rows, 1, gdal.GDT_Float32)
        out_raster.SetGeoTransform((origin_x, pixel_width, 0, origin_y, 0, pixel_height))
        out_band = out_raster.GetRasterBand(1)
        out_band.WriteArray(array)

        out_raster_SRS = osr.SpatialReference()
        out_raster_SRS.ImportFromEPSG(4326)
        out_raster.SetProjection(out_raster_SRS.ExportToWkt())
        out_band.FlushCache()


if __name__ == '__main__':
    start_time = time.time()
    input_path = '/mnt/d/Experiments/OMI_DataProcessing/Data/OMI_L3_NO2/'
    output_path = '/mnt/d/Experiments/OMI_DataProcessing/Data/Results/Average2/'
    if os.path.exists(output_path) == False:
        os.makedirs(output_path)
    file_list = []
    for root, dirs, files in os.walk(input_path):
        file_list.extend(files)
    file_name = [input_path + i_he5 for i_he5 in file_list if i_he5.startswith('OMI') and i_he5.endswith('.he5')]
    month_out = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    season_out = ['spring', 'summer', 'autumn', 'winter']
    year_out = ['2017', '2018']
    raster_origin = (-180, 90)
    pixel_width = 0.25
    pixel_height = -0.25
    no2_avr_cal = OMI_NO2_AverageCalculating(file_name, output_path, raster_origin, pixel_width, pixel_height,
                                             month_out, season_out,
                                             year_out)
    no2_avr_cal._cal_avr_()
    end_time = time.time()
    run_time = end_time - start_time
    print('程序运行时间为：' + str(run_time) + 's')
