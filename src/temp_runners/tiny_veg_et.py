"""
Make a smaller model dataset clipped from another set of datasets using a shapefile
"""
import os
# annoying stuff I need to do
os.environ['PROJ_LIB'] = r'C:\Users\gparrish\AppData\Local\conda\conda\envs\gdal_env\Library\share\proj'
os.environ['GDAL_DATA'] = r'C:\Users\gparrish\AppData\Local\conda\conda\envs\gdal_env\Library\share\epsg_csv'
# more imports
import rasterio
import fiona
from datetime import datetime, timedelta
import numpy as np

from src.vegetLib.vegetLib.pathmanager import PathManager
from src.vegetLib.vegetLib.rastermanager import RasterManager
from src.vegetLib.vegetLib.vegconfig import return_veget_params

yml_file_location = r'C:\Users\gparrish\Desktop\smallVeget\veget_sample_configs'
small_location = r'Z:\Users\Gabe\UpperRioGrandeBasin\Shapefiles\RogersVegET_ROI.shp'

params = return_veget_params(config_directory=yml_file_location)
# the tile has to be set
params['tile'] = '' # TODO - 'tile' parameter is problematic the way it can cause problems
print('params! \n', type(params), '\n', params)
pm = PathManager(config_dict=params)
rm = RasterManager(config_dict=params, shp=small_location)
# # If you want to change any parameters, you should do it here....
# # .....................................................

params['temp_folder'] = r'C:\Users\gparrish\Desktop\smallVeget\temp'
params['start_year'] = 2000
params['start_day'] = 274
params['end_year'] = 2001
params['end_day'] = 365
start_year: 2000
end_year: 2019
start_day: 274
end_day: 365
# set the standard grid from the small location and the params
rm.set_model_std_grid()


# # TODO - write tiny model.
output_location = r'C:\Users\gparrish\Desktop\smallVeget'

# ====================== data settings ==================================
interception_settings = params['interception_settings']
whc_settings = params['whc_settings']
saturation_settings = params['saturation_settings']
watermask_settings = params['watermask_settings']
field_capacity_settings = params['field_capacity_settings']
ndvi_settings = params['ndvi_settings']
precip_settings = params['precip_settings']
pet_settings = params['pet_settings']
tavg_settings = params['tavg_settings']
tmin_settings = params['tmin_settings']
tmax_settings = params['tmax_settings']

# set all climatologies to false # todo - maybe a little better option to do this...
interception_settings['climatology'] = False
whc_settings['climatology'] = False
saturation_settings['climatology'] = False
watermask_settings['climatology'] = False
field_capacity_settings['climatology'] = False
# ndvi_settings['climatology'] = False
# precip_settings['climatology'] = False
# pet_settings['climatology'] = False
# tavg_settings['climatology'] = False
# tmin_settings['climatology'] = False
# tmax_settings['climatology'] = False

def write_new_aoi_based_on_datasets():

    start_dt = datetime.strptime("{}-{:03d}".format(params['start_year'], params['start_day']), '%Y-%j')
    print(start_dt)
    end_dt = datetime.strptime("{}-{:03d}".format(params['end_year'], params['end_day']), '%Y-%j')
    print(end_dt)
    time_interval = end_dt - start_dt
    num_days = time_interval.days
    print(num_days)

    # Open static inputs and normalize them to standard numpy arrays

    # static inputs
    interception = pm.get_static_data(params['interception_settings'])
    whc = pm.get_static_data(params['whc_settings'])
    field_capacity = pm.get_static_data(params['field_capacity_settings'])
    saturation = pm.get_static_data(params['saturation_settings'])
    watermask = pm.get_static_data(params['watermask_settings'])
    # package as a list
    static_inputs = [interception, whc, field_capacity, saturation, watermask]

    interception, whc, field_capacity, saturation, watermask \
        = rm.normalize_to_std_grid_fast(inputs=static_inputs, resamplemethod='nearest')

    interception = interception.astype('float64')
    whc = whc.astype('float64')
    field_capacity = field_capacity.astype('float64')
    saturation = saturation.astype('float64')
    watermask = watermask.astype('float64')


    # output the statics
    rm.output_rasters(arr=interception, outdir=os.path.join(output_location, 'statics'), outname='interception.tif')
    rm.output_rasters(arr=whc, outdir=os.path.join(output_location, 'statics'), outname='whc.tif')
    rm.output_rasters(arr=field_capacity, outdir=os.path.join(output_location, 'statics'), outname='fc.tif')
    rm.output_rasters(arr=saturation, outdir=os.path.join(output_location, 'statics'), outname='saturation.tif')
    rm.output_rasters(arr=watermask, outdir=os.path.join(output_location, 'statics'), outname='watermask.tif')


    for i in range(num_days + 1):

        # so what day is it
        today = start_dt + timedelta(days=i)
        doy = today.timetuple().tm_yday

        # dynamic inputs to the model
        ndvi, ndvi_scale = pm.get_dynamic_data(today, ndvi_settings)
        pet, pet_scale = pm.get_dynamic_data(today, pet_settings)
        ppt, ppt_scale = pm.get_dynamic_data(today, precip_settings)
        tavg, tavg_scale = pm.get_dynamic_data(today, tavg_settings)
        tmin, tmin_scale = pm.get_dynamic_data(today, tmin_settings)
        tmax, tmax_scale = pm.get_dynamic_data(today, tmax_settings)

        # Call Raster Manager function to standardize all the input dataset.
        dynamic_inpts = [ndvi, pet, ppt, tavg, tmin, tmax]

        # All the variables are now Numpy Arrays!
        ndvi, pet, ppt, tavg, tmin, tmax = rm.normalize_to_std_grid_fast(inputs=dynamic_inpts, resamplemethod='nearest')

        ndvi = ndvi.astype('float64')
        pet = pet.astype('float64')
        ppt = ppt.astype('float64')
        tavg = tavg.astype('float64')
        tmin = tmin.astype('float64')
        tmax = tmax.astype('float64')

        # output the datasets after standardizing them
        rm.output_rasters(arr=ndvi, outdir=os.path.join(output_location, 'ndvi'),
                          outname='ndvi_{}{:03d}.tif'.format(today.year, doy))
        rm.output_rasters(arr=pet, outdir=os.path.join(output_location, 'pet'),
                          outname='pet_{}{:03d}.tif'.format(today.year, doy))
        rm.output_rasters(arr=ppt, outdir=os.path.join(output_location, 'ppt'),
                          outname='ppt_{}{:03d}.tif'.format(today.year, doy))
        rm.output_rasters(arr=tavg, outdir=os.path.join(output_location, 'tavg'),
                          outname='tavg_{}{:03d}.tif'.format(today.year, doy))
        rm.output_rasters(arr=tmax, outdir=os.path.join(output_location, 'tmax'),
                          outname='tmax_{}{:03d}.tif'.format(today.year, doy))
        rm.output_rasters(arr=tmin, outdir=os.path.join(output_location, 'tmin'),
                          outname='tmin_{}{:03d}.tif'.format(today.year, doy))



# call the function
write_new_aoi_based_on_datasets()

print('THE END')

# TODO - Generate tiny config files for the script user.


