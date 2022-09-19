# OMI_DataProcessing


##This Project is processing OMI sitellite data using Python and IDL language.
First of all, I read HDF5 dataset(OMI data:*.he5) and calculated thier average values of month, season and year(2017 and 2018).
Next, I reprojection these data and write geographic infomation for them with gdal lib.
Lastly, I write and save them to the disk with geotiff format.
I using the way of object oriented design when I use Python. 
But to my surprise, as a interpreted laguage Python is faster than IDL which is a compiled language.
That is all of the program. 