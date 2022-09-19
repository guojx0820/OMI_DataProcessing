function h5_data_get,file_name,dataset_name
  file_id=h5f_open(file_name)
  dataset_id=h5d_open(file_id,dataset_name)
  data=h5d_read(dataset_id)
  h5d_close,dataset_id
  return,data
  data=!null
end

pro omi_no2__average_calculating
  ;输入输出路径设置
  start_time=systime(1)
  in_path='D:/Experiments/OMI_DataProcessing/Data/OMI_L3_NO2/'
  out_path='D:/Experiments/OMI_DataProcessing/Data/Results/Average/'
  dir_test=file_test(out_path,/directory)
  if dir_test eq 0 then begin
    file_mkdir,out_path
  endif
  file_list=file_search(in_path,'*NO2*.he5')
  file_n=n_elements(file_list)
  group_name='/HDFEOS/GRIDS/ColumnAmountNO2/Data Fields/'
  target_dataset='ColumnAmountNO2TropCloudScreened'
  dataset_name=group_name+target_dataset
  
  ;月份储存数组初始化
  data_total_month=fltarr(1440,720,12)
  data_valid_month=fltarr(1440,720,12)
  data_avr_month=fltarr(1440,720,12)
  help,data_total_month
  ;季节储存数组初始化
  data_total_season=fltarr(1440,720,4)
  data_valid_season=fltarr(1440,720,4)
  data_avr_season=fltarr(1440,720,4)
  
  ;月份储存数组初始化
  year_start=2017
  year_n=2
  data_total_year=fltarr(1440,720,year_n)
  data_valid_year=fltarr(1440,720,year_n)
  data_avr_year=fltarr(1440,720,year_n)
  
  for file_i=0,file_n-1 do begin
    print,file_list[file_i]
    data_temp=h5_data_get(file_list[file_i],dataset_name)
    data_temp=((data_temp gt 0.0)*data_temp/!const.NA)*(10.0^10.0) ;mol/km
    data_temp=rotate(data_temp,7)
    
    layer_i=fix(strmid(file_basename(file_list[file_i]),24,2))-1
    data_total_month[*,*,layer_i]+=data_temp
    data_valid_month[*,*,layer_i]+=(data_temp gt 0.0)
    
    if (layer_i ge 2) and (layer_i le 4) then begin
      data_total_season[*,*,0]+=data_temp
      data_valid_season[*,*,0]+=(data_temp gt 0.0)
    endif
    if (layer_i ge 5) and (layer_i le 7) then begin
      data_total_season[*,*,1]+=data_temp
      data_valid_season[*,*,1]+=(data_temp gt 0.0)
    endif
    if (layer_i ge 8) and (layer_i le 10) then begin
      data_total_season[*,*,2]+=data_temp
      data_valid_season[*,*,2]+=(data_temp gt 0.0)
    endif
    if (layer_i ge 11) or (layer_i le 1) then begin
      data_total_season[*,*,3]+=data_temp
      data_valid_season[*,*,3]+=(data_temp gt 0.0)
    endif
    
    year_i=fix(strmid(file_basename(file_list[file_i]),19,4))-year_start
    data_total_year[*,*,year_i]+=data_temp
    data_valid_year[*,*,year_i]+=(data_temp gt 0.0)
  endfor
  ;print,data_valid_season
  data_valid_month=(data_valid_month gt 0.0)*data_valid_month+(data_valid_month eq 0.0)*(1.0)
  data_avr_month=data_total_month/data_valid_month
  data_valid_season=(data_valid_season gt 0.0)*data_valid_season+(data_valid_season eq 0.0)*(1.0)
  data_avr_season=data_total_season/data_valid_season
  data_valid_year=(data_valid_year gt 0.0)*data_valid_year+(data_valid_year eq 0.0)*(1.0)
  data_avr_year=data_total_year/data_valid_year
  
  month_out=['01','02','03','04','05','06','07','08','09','10','11','12']
  season_out=['spring','summer','autumn','winter']
  year_out=['2017','2018']
  
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
    
  for month_i=0,11 do begin
    out_month=out_path+'month_avr_'+month_out[month_i]+'.tiff'
    write_tiff,out_month,data_avr_month[*,*,month_i],/float,geotiff=geo_info
  endfor
  for season_i=0,3 do begin
    out_season=out_path+'season_avr_'+season_out[season_i]+'.tiff'
    write_tiff,out_season,data_avr_season[*,*,season_i],/float,geotiff=geo_info
  endfor
  for year_i=0,1 do begin
    out_year=out_path+'year_avr_'+strcompress(string(year_i+year_start),/remove_all)+'.tiff'
    ;out_year=out_path+'year_avr_'+year_out[year_i]+'.tiff'
    write_tiff,out_year,data_avr_year[*,*,year_i],/float,geotiff=geo_info
  endfor
  
  end_time=systime(1)
  print,'Processing is ending,the total time consuming is: '+strcompress(string(end_time-start_time))+' s.'
end