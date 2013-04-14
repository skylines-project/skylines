#!/usr/bin/python
#
# Download and import elevation data
#

import os.path
import argparse
import subprocess
from zipfile import ZipFile
from tempfile import NamedTemporaryFile
from paste.deploy.loadwsgi import appconfig
from tg import config
from skylines.config.environment import load_environment
from skylines.model.session import DBSession

SERVER_URL = 'http://download.xcsoar.org/mapgen/data/srtm3/'

# Parse command line parameters
parser = argparse.ArgumentParser(
    description='Add elevation data to the database.')

parser.add_argument('--config', metavar='config.ini',
                    default='/etc/skylines/production.ini',
                    help='path to the configuration INI file')

parser.add_argument('x', type=int)
parser.add_argument('y', type=int)

args = parser.parse_args()

if not 1 <= args.x <= 72:
    parser.error('x has to be between 1 and 72')

if not -4 <= args.y <= 24:
    parser.error('y has to be between -4 and 24')

basename = 'srtm_{x:02}_{y:02}'.format(x=args.x, y=args.y)


# Load configuration file
conf = appconfig('config:' + os.path.abspath(args.config))
load_environment(conf.global_conf, conf.local_conf)


# Change path to configured srtm data path
path = config['skylines.elevation_path']

if not os.path.exists(path):
    print 'Creating {} ...'.format(path)
    os.mkdir(path)

os.chdir(path)


# Check if tiled GeoTIFF file already exists
tiled_tif_filename = basename + '_tiled.tif'

if os.path.exists(tiled_tif_filename):
    print "{} exists already.".format(tiled_tif_filename)
    exit()


# Check if original GeoTIFF file exists
tif_filename = basename + '.tif'
zip_filename = basename + '.zip'

if not os.path.exists(tif_filename):

    # Check if ZIP file already exists and download if necessary
    if not os.path.exists(zip_filename):
        print 'Downloading {} ...'.format(zip_filename)
        url = SERVER_URL + zip_filename
        subprocess.check_call(['wget', '-N', url])

    # Unzip elevation data
    print 'Extracting {} ...'.format(zip_filename)
    zip = ZipFile(zip_filename)
    zip.extract(tif_filename)


# Make GeoTIFF file tiled and compressed
args = [
    'gdal_translate',
    '-co', 'COMPRESS=DEFLATE',  # Compress the file with DEFLATE
    '-co', 'TILED=YES',  # Use a tiled GeoTIFF format
    tif_filename,  # Input file
    tiled_tif_filename,  # Output file
]
subprocess.check_call(args)


# Create SQL statements
print 'Converting {} to SQL ...'.format(tiled_tif_filename)
args = [
    'raster2pgsql',
    '-a',  # Append to existing table
    '-s', '4326',  # SRID 4326 (WGS 84)
    '-t', '100x100',  # 100x100 tiles
    '-R',  # Out-of-DB raster
    os.path.abspath(tiled_tif_filename),
    'elevations',
]
raster2pgsql = subprocess.Popen(args, stdout=subprocess.PIPE)

print 'Adding SQL to the database ...'
for i, line in enumerate(raster2pgsql.stdout):
    if i % 100 == 0 and i != 0:
        print i

    DBSession.execute(line)


# Delete temporary files
print "Cleaning up ..."

if os.path.exists(zip_filename):
    os.unlink(zip_filename)

if os.path.exists(tif_filename):
    os.unlink(tif_filename)
