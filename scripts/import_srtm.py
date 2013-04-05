#!/usr/bin/python
#
# Download and import elevation data
#

import os.path
import argparse
import subprocess
from zipfile import ZipFile
from tempfile import NamedTemporaryFile

BASE_URL = 'http://download.xcsoar.org/mapgen/data/srtm3/'

# Parse command line parameters
parser = argparse.ArgumentParser(
    description='Add elevation data to the database.')

parser.add_argument('x', type=int)
parser.add_argument('y', type=int)

args = parser.parse_args()

if not 1 <= args.x <= 72:
    parser.error('x has to be between 1 and 72')

if not -4 <= args.y <= 24:
    parser.error('y has to be between -4 and 24')


def download(filename):
    print 'Downloading {} ...'.format(filename)
    url = BASE_URL + filename
    subprocess.check_call(['wget', '-N', url])


def extract(filename, foldername):
    print 'Extracting {} ...'.format(filename)
    zip = ZipFile(filename)
    zip.extractall(path=foldername)


def raster2pgsql(filename, output):
    print 'Converting {} to {} ...'.format(filename, output.name)
    subprocess.check_call(
        ['raster2pgsql', '-a', '-t', '100x100', filename, 'elevations'],
        stdout=output)


def apply_sql(filename):
    print 'Applying {} ...'.format(filename)
    subprocess.check_call(['psql', '-d', 'skylines', '-f', filename])


basename = 'srtm_{x:02}_{y:02}'.format(x=args.x, y=args.y)

tif_filename = basename + '.tif'
tif_path = os.path.join(basename, tif_filename)

if not os.path.exists(tif_path):

    zip_filename = basename + '.zip'

    # Download the elevation data
    download(zip_filename)

    # Create output folder
    if not os.path.exists(basename):
        os.mkdir(basename)

    # Unzip elevation data
    extract(zip_filename, basename)

with NamedTemporaryFile(delete=False) as sql_file:
    raster2pgsql(tif_path, sql_file)

apply_sql(sql_file.name)

os.unlink(sql_file.name)
