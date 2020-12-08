import os
import yaml
from vegetLib.vegetLib.veget import VegET
"""This script is an example of how to set up a bunch of model runs based on chips
generated with degree_gridmeister.py (see grid_generate.py for an example of that...)"""

# a directory filled with shapefiles generated by grid_generate.py
shapedir = r'Z:\Projects\VegET_ndviLSP\aa_30m_run\shapefiles'

# path for
template_configurations_root = r'Z:\Projects\VegET_ndviLSP\aa_30m_run\sample_configs'

# path for where the directories go
proj_root = r'Z:\Projects\VegET_ndviLSP\aa_30m_run'

testing = False

# create paths to each sample config. settings in the sample will propagate unless otherwise specified.
sample_cfgs = []
for cfg in ['run_param.yml', 'path_param.yml', 'model_param.yml']:
    sample_cfgs.append(os.path.join(template_configurations_root, cfg))

# dictionaries used to modify some properties in run_param, path_param and model_param.yml
# respective to the sample config. The 'shapefile' in run_mod_dict is a placeholder...
run_mod_dict = {'geoproperties_file': r'Z:\Projects\VegET_ndviLSP\daily_ndvi\ndvi001.tif',
                'shapefile': '', 'start_year': 2000, 'end_year': 2019}
# out_root need to change with the shapefile, so provided here is a placeholder.
# with these settings, it may be easier to set them in the sample config, so they just get repeated.
path_mod_dict = None
# nothing to change in model_param.yml right now
model_mod_dict = None

tile_dir_list = []
shapefile_list = []
for file in os.listdir(shapedir):
    if file.endswith('.shp'):
        # chip name and thus,the filename too
        print(file)
        fname = '{}{}{}'.format(file.split('.')[0], file.split('.')[1], file.split('.')[2])
        # mkdir for the fname
        fout_root = os.path.join(proj_root, fname)
        if not os.path.exists(fout_root):
            os.mkdir(fout_root)
        # the shapefile for the run.
        sfile = os.path.join(shapedir, file)

        shapefile_list.append(sfile)
        tile_dir_list.append(fout_root)

        # todo - modify each sample config for the run and put it in the fname dir.
        for c in sample_cfgs:
            if c.endswith('run_param.yml'):
                mod_dict = run_mod_dict
                rd = True
                pd = False
                md = False
            elif c.endswith('path_param.yml'):
                mod_dict = path_mod_dict
                rd = False
                pd = True
                md = False
            elif c.endswith('model_param.yml'):
                mod_dict = model_mod_dict
                rd = False
                pd = False
                md = True

            # load the yaml.
            with open(c, 'r') as rfile:
                out_dict = yaml.safe_load(rfile)

                config_name = os.path.split(c)[1]
                # new place for the config(s) to go.
                cfg_outpath = os.path.join(fout_root, config_name)
                print(out_dict)
                if mod_dict != None:
                    print('modifying')
                    for k, v in mod_dict.items():
                        out_dict[k] = v
                print('modifying shapefile and outroot')

                # these mods need to get made anyways cause the shapes are all different
                if rd:
                    out_dict['shapefile'] = sfile
                elif pd:
                    out_dict['out_root'] = fout_root
                    out_dict['temp_folder'] = proj_root

                print('out dict before it goes in \n', out_dict)

                with open(cfg_outpath, 'w') as wfile:
                    yaml.dump(out_dict, wfile)
print(tile_dir_list, '\n', shapefile_list)


if not testing:
    print('launching model runs')
    for xx, yy in zip(tile_dir_list, shapefile_list):
        tilename = yy.split('.')[-1]
        shapefile = yy
        config_path = xx

        print(f'launching {tilename} outputs in directory {config_path}')
        veggie = VegET(veget_config_path=config_path,
                       tile=tilename,
                       shp=shapefile)
        veggie.run_veg_et()
else:
    print('that was just a test')