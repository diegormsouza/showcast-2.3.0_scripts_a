#######################################################################################################
# LICENSE
# Copyright (C) 2021 - INPE - NATIONAL INSTITUTE FOR SPACE RESEARCH - BRAZIL
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU 
# General Public License as published by the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without 
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
# Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. 
# If not, see http://www.gnu.org/licenses/.
#######################################################################################################
__author__ = "Diego Souza"
__copyright__ = "Copyright (C) 2021 - INPE - NATIONAL INSTITUTE FOR SPACE RESEARCH - BRAZIL"
__credits__ = ["Diego Souza"]
__license__ = "GPL"
__version__ = "2.3.0"
__maintainer__ = "Diego Souza"
__email__ = "diego.souza@inpe.br"
__status__ = "Production"
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Required modules
#--------------------------------
#to run in a pure text terminal:
import matplotlib
matplotlib.use('Agg')
#--------------------------------
from netCDF4 import Dataset                                  # Read / Write NetCDF4 files
from mpl_toolkits.axes_grid1.inset_locator import inset_axes # Add a child inset axes to this existing axes.
from datetime import datetime, timedelta                     # Library to convert julian day to dd-mm-yyyy
from cpt_convert import loadCPT                              # Import the CPT convert function
from matplotlib.colors import LinearSegmentedColormap        # Linear interpolation for color maps
import matplotlib.pyplot as plt                              # Plotting library
import matplotlib.colors                                     # Matplotlib colors
import numpy as np                                           # Scientific computing with Python
import cartopy, cartopy.crs as ccrs                          # Plot maps
import cartopy.io.shapereader as shpreader                   # Import shapefiles
import time as t                                             # Time access and conversion
import math                                                  # Import math
import re                                                    # re
import glob                                                  # Unix style pathname pattern expansion
import sys                                                   # Import the "system specific parameters and functions" module
import os 												     # Miscellaneous operating system interfaces
from os.path import dirname, abspath                         # Return a normalized absolutized version of the pathname path 
import platform                                              # To check which OS is being used
from html_update import update                               # Update the HTML animation 
import warnings
warnings.filterwarnings("ignore")
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Start the time counter
print('Script started.')
start = t.time()  

# SHOWCast directory:
main_dir = dirname(dirname(abspath(__file__)))

# Band 13 file
path_ch13 = (sys.argv[1])
#path_ch13 = ("..//Samples//OR_ABI-L2-CMIPF-M6C13_G16_s20192931650344_e20192931700064_c20192931700142.nc")
#path_ch13 = ("..//Samples//OR_ABI-L2-CMIPF-M6C13_G17_s20192931650341_e20192931659418_c20192931659465-132020_0.nc")

# For the log
path = path_ch13

#print(path)
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Remove the identification
path_ch13 = path_ch13[:-4]

# Get the Band 15, same file
osystem = platform.system()
if osystem == "Windows":
    path_ch15 = re.sub('Band13\\\\OR_ABI-L2-CMIPF*(.*)', '', path_ch13)
else:
    path_ch15 = re.sub('Band13/OR_ABI-L2-CMIPF*(.*)', '', path_ch13)

# Get the start of scan from the file name
scan_start = (path_ch13[path_ch13.find("_s")+2:path_ch13.find("_e")])

file = []
for filename in sorted(glob.glob(path_ch15+'Band15//OR_ABI-L2-CMIPF-M*C15_G1*.nc')):
    file.append(filename)
    
# Seek for a GOES-16 file (same time) in the directory
matching = [s for s in file if scan_start in s]     

# If the file is not found, exit the loop
if not matching:
    print("File Not Found! Exiting Script.")
    sys.exit()
else: # If the file is found, continue
    print("File OK!")
    matching = matching[0]
    index = file.index(matching)
    path_ch15 = file[index]

#print(path_ch13)
#print(path_ch15)
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Read the image
file_ch13 = Dataset(path_ch13)

# Read the satellite 
satellite = getattr(file_ch13, 'platform_ID')

# Read the band number
band = str(file_ch13.variables['band_id'][0]).zfill(2)

# Desired resolution
resolution = int(sys.argv[6])

# Read the resolution
band_resolution_km = getattr(file_ch13, 'spatial_resolution')
band_resolution_km = float(band_resolution_km[:band_resolution_km.find("km")])

# Division factor to reduce image size
f = math.ceil(float(resolution / band_resolution_km))

# Read the central longitude
longitude = file_ch13.variables['goes_imager_projection'].longitude_of_projection_origin

# Calculate the image extent 
H = file_ch13.variables['goes_imager_projection'].perspective_point_height
x1 = file_ch13.variables['x_image_bounds'][0] * H 
x2 = file_ch13.variables['x_image_bounds'][1] * H 
y1 = file_ch13.variables['y_image_bounds'][1] * H 
y2 = file_ch13.variables['y_image_bounds'][0] * H 

# Getting the file time and date
add_seconds = int(file_ch13.variables['time_bounds'][0])
date = datetime(2000,1,1,12) + timedelta(seconds=add_seconds)
date_formated = date.strftime('%Y-%m-%d %H:%M UTC')
date_file = date.strftime('%Y%m%d%H%M')
year = date.strftime('%Y')
month = date.strftime('%m')
day = date.strftime('%d')
hour = date.strftime('%H')
minutes = date.strftime('%M')

# Get the pixel values
data_ch13 = file_ch13.variables['CMI'][:,:][::f ,::f ]
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Read the image
file_ch15 = Dataset(path_ch15)

# Read the resolution
band_resolution_km = getattr(file_ch15, 'spatial_resolution')
band_resolution_km = float(band_resolution_km[:band_resolution_km.find("km")])

# Division factor to reduce image size
f = math.ceil(float(resolution / band_resolution_km))

# Get the pixel values
data_ch15 = file_ch15.variables['CMI'][:,:][::f ,::f ]
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Create the SWD
data = data_ch13 - data_ch15
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# SWD    
colors = ["#ff00ff", "#0000ff", "#00ff00", "#ffff00", "#ff0000", "#ffffff", "#ffffff"]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors)
vmin = -1
vmax = 12
thick_interval = 1   

# Product Name
product = "SWDIFF_FDK" 
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------    
# Plot configuration
plot_config = {
"resolution": band_resolution_km, 
"dpi": 150, 
"states_color": 'white', "states_width": data.shape[0] * 0.00006, 
"countries_color": 'black', "countries_width": data.shape[0] * 0.00012,
"continents_color": 'black', "continents_width": data.shape[0] * 0.00025,
"grid_color": 'white', "grid_width": data.shape[0] * 0.00025, "grid_interval": 10.0,
"vmin": vmin, "vmax": vmax, "cmap": cmap,
"title_text": "GOES-" + satellite[1:3] + " SWD ", "title_size": int(data.shape[1] * 0.005), "title_x_offset": int(data.shape[1] * 0.01), "title_y_offset": data.shape[0] - int(data.shape[0] * 0.016), 
"thick_interval": thick_interval, "cbar_labelsize": int(data.shape[0] * 0.005), "cbar_labelpad": -int(data.shape[0] * 0.0),
"file_name_id_1": satellite,  "file_name_id_2": product
}
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Choose the plot size (width x height, in inches)
fig = plt.figure(figsize=(data_ch13.shape[1]/float(plot_config["dpi"]), data_ch13.shape[0]/float(plot_config["dpi"])), dpi=plot_config["dpi"])
  
# Define the projection
proj = ccrs.Geostationary(central_longitude=longitude, satellite_height=H)
img_extent = (x1,x2,y1,y2)

# Use the Geostationary projection in cartopy
ax = plt.axes([0, 0, 1, 1], projection=proj)

# Plot the image
img = ax.imshow(data, vmin=plot_config["vmin"], vmax=plot_config["vmax"], origin='upper', extent=img_extent, cmap=plot_config["cmap"], zorder=1)

# To put colorbar inside picture
axins1 = inset_axes(ax, width="100%", height="1%", loc='lower center', borderpad=0.0)
  
# Add states and provinces
shapefile = list(shpreader.Reader(main_dir + '//Shapefiles//ne_10m_admin_1_states_provinces.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor=plot_config["states_color"],facecolor='none', linewidth=plot_config["states_width"], zorder=2)

# Add countries
shapefile = list(shpreader.Reader(main_dir + '//Shapefiles//ne_50m_admin_0_countries.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor=plot_config["countries_color"],facecolor='none', linewidth=plot_config["countries_width"], zorder=3)

# Add continents
shapefile = list(shpreader.Reader(main_dir + '//Shapefiles//ne_10m_coastline.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor=plot_config["continents_color"],facecolor='none', linewidth=plot_config["continents_width"], zorder=4)
  
# Add coastlines, borders and gridlines
ax.gridlines(color=plot_config["grid_color"], alpha=0.5, linestyle='--', linewidth=plot_config["grid_width"], xlocs=np.arange(-180, 180, plot_config["grid_interval"]), ylocs=np.arange(-180, 180, plot_config["grid_interval"]), draw_labels=False, zorder=5)

# Remove the outline border
ax.outline_patch.set_visible(False)
  
# Add a title
plt.annotate(plot_config["title_text"] + " " + date_formated , xy=(plot_config["title_x_offset"], plot_config["title_y_offset"]), xycoords='figure pixels', fontsize=plot_config["title_size"], fontweight='bold', color='white', bbox=dict(boxstyle="round",fc=(0.0, 0.0, 0.0), ec=(1., 1., 1.)), zorder=6)

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Add labels to specific coordinates

import configparser
conf = configparser.ConfigParser()
if (satellite == 'G16'):
    conf.read(main_dir + '//Utils//Labels//labels_g16.ini')
elif (satellite == 'G17'):
    conf.read(main_dir + '//Utils//Labels//labels_g17.ini')

labels, city_lons, city_lats, x_offsets, y_offsets, sizes, colors, marker_types, marker_colors, marker_sizes = [],[],[],[],[],[],[],[],[],[]

for each_section in conf.sections():
    for (each_key, each_val) in conf.items(each_section):
        if (each_key == 'label'): labels.append(each_val)
        if (each_key == 'lon'): city_lons.append(float(each_val))
        if (each_key == 'lat'): city_lats.append(float(each_val))
        if (each_key == 'x_offset'): x_offsets.append(float(each_val))
        if (each_key == 'y_offset'): y_offsets.append(float(each_val))
        if (each_key == 'size'): sizes.append(int(each_val))
        if (each_key == 'color'): colors.append(each_val)
        if (each_key == 'marker_type'): marker_types.append(each_val)
        if (each_key == 'marker_color'): marker_colors.append(each_val)
        if (each_key == 'marker_size'): marker_sizes.append(each_val)
 
import matplotlib.patheffects as PathEffects
for label, xpt, ypt, x_offset, y_offset, size, col, mtype, mcolor, msize in zip(labels, city_lons, city_lats, x_offsets, y_offsets, sizes, colors, marker_types, marker_colors, marker_sizes):
    ax.plot(xpt, ypt, str(mtype), color=str(mcolor), markersize=int(msize), transform=ccrs.Geodetic(), markeredgewidth=1.0, markeredgecolor=(0, 0, 0, 1), zorder=10)
    txt = ax.text(xpt+x_offset , ypt+y_offset, label, fontsize=int(size), fontweight='bold', color=str(col), transform=ccrs.Geodetic(), zorder=11)
    txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='black')])
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------

# Add logos / images to the plot
my_logo = plt.imread(main_dir + '//Logos//my_logo.png')
newax = fig.add_axes([0.01, 0.03, 0.10, 0.10], anchor='SW', zorder=12) #  [left, bottom, width, height]. All quantities are in fractions of figure width and height.
newax.imshow(my_logo)
newax.axis('off')

# Add a colorbar
ticks = np.arange(plot_config["vmin"], plot_config["vmax"], plot_config["thick_interval"]).tolist()     
ticks = plot_config["thick_interval"] * np.round(np.true_divide(ticks,plot_config["thick_interval"]))
ticks = ticks[1:]
cb = fig.colorbar(img, cax=axins1, orientation="horizontal", ticks=ticks)
cb.outline.set_visible(False)
cb.ax.tick_params(width = 0)
cb.ax.xaxis.set_tick_params(pad=plot_config["cbar_labelpad"])
cb.ax.xaxis.set_ticks_position('top')
cb.ax.tick_params(axis='x', colors='lightgray', labelsize=plot_config["cbar_labelsize"])

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------

# Create the satellite output directory if it doesn't exist
out_dir = main_dir + '//Output//' + satellite
if not os.path.exists(out_dir):
   os.mkdir(out_dir)

# Create the product output directory if it doesn't exist
out_dir = main_dir + '//Output//' + satellite + '//' + product + '//'
if not os.path.exists(out_dir):
   os.mkdir(out_dir)
   
# Save the image
plt.savefig(out_dir + plot_config["file_name_id_1"] + "_" + plot_config["file_name_id_2"] + "_" + date_file + '.png', facecolor='black')#, bbox_inches='tight', pad_inches=0, facecolor='black')

# Update the animation
nfiles = 20
update(satellite, product, nfiles)

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# Put the processed file on the log
import datetime # Basic Date and Time types
with open(main_dir + '//Logs//gnc_log_' + str(datetime.datetime.now())[0:10] + '.txt', 'a') as log:
 log.write(str(datetime.datetime.now()))
 log.write('\n')
 log.write(path + '\n')
 log.write('\n')
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------

print('Total processing time:', round((t.time() - start),2), 'seconds.') 