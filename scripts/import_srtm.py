#!/usr/bin/env python
#
# Download and import elevation data
#

import argparse
from config import to_envvar

# Parse command line parameters
parser = argparse.ArgumentParser(
    description='Add elevation data to the database.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

parser.add_argument('x', type=int)
parser.add_argument('y', type=int)

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


import os.path
import subprocess
from zipfile import ZipFile
from skylines import app, db

SERVER_URL = 'http://download.xcsoar.org/mapgen/data/srtm3/'


if not 1 <= args.x <= 72:
    parser.error('x has to be between 1 and 72')

if not -4 <= args.y <= 24:
    parser.error('y has to be between -4 and 24')

basename = 'srtm_{x:02}_{y:02}'.format(x=args.x, y=args.y)


# Change path to configured srtm data path
path = app.config['SKYLINES_ELEVATION_PATH']

if not os.path.exists(path):
    print 'Creating {} ...'.format(path)
    os.mkdir(path)

os.chdir(path)


# Check if tiled GeoTIFF file already exists
tiled_tif_filename = basename + '_tiled.tif'

if os.path.exists(tiled_tif_filename):
    print "{} exists already.".format(tiled_tif_filename)
    exit()


# Download TIF file
tif_filename = basename + '.tif'

print 'Downloading {} ...'.format(tif_filename)
url = SERVER_URL + tif_filename
subprocess.check_call(['wget', '-O', tiled_tif_filename, url])


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

    db.session.execute(line)
