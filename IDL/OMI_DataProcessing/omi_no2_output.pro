function h5_data_get,file_name,dataset_name
  file_id=h5f_open(file_name)
  dataset_id=h5d_open(file_id,dataset_name)
  data=h5d_read(dataset_id)
  h5d_close,dataset_id
  return,data
  data=!null
end

pro omi_no2_output
 file_name='D:\Experiments\OMI_DataProcessing\Data\OMI_L3_NO2\OMI-Aura_L3-OMNO2d_2022m0901_v003-2022m0902t232524.he5'
 dataset_name='/HDFEOS/GRIDS/ColumnAmountNO2/Data Fields/ColumnAmountNO2TropCloudScreened'
 out_directory='D:\Experiments\OMI_DataProcessing\Data\Results\'
 dir_test=file_test(out_directory,/directory) ;测试文件/目录（加关键字/directory）是否存在，存在返回1，不存在则返回0
 if dir_test eq 0 then begin
  file_mkdir,out_directory
 endif ;如果不存在（返回0），则新建对应的目录
 out_name=out_directory+file_basename(file_name,'.he5')+'_geo'+'.tiff'
 data_temp=h5_data_get(file_name,dataset_name)
 data_temp=(data_temp gt 0.0)*data_temp*10.0^10.0/(!const.NA) ;mol/km2
 data_temp=rotate(data_temp,7)
 
 geo_info={$
   MODELPIXELSCALETAG:[0.25,0.25,0.0],$;X,Y,Z方向的像元分辨率
   MODELTIEPOINTTAG:[0.0,0.0,0.0,-180.0,90.0,0.0],$
   ;坐标转换信息，前三个0.0代表栅格图像上的第0，0，0个像元位置（z方向一般不存在），
   ;后面-180.0代表x方向第0个位置对应的经度是-180.0度，90.0代表y方向第0个位置对应的经度是90.0度。
   GTMODELTYPEGEOKEY:2,$
   GTRASTERTYPEGEOKEY:1,$
   GEOGRAPHICTYPEGEOKEY:4326,$
   GEOGCITATIONGEOKEY:'GCS_WGS_1984',$
   GEOGANGULARUNITSGEOKEY:9102,$
   GEOGSEMIMAJORAXISGEOKEY:6378137.0,$
   GEOGINVFLATTENINGGEOKEY:298.25722}
 
 write_tiff,out_name,data_temp,/float,geotiff=geo_info
end