import sys
from flask.ext.script import Command, Option

import os
import subprocess
import shutil
from glob import glob
from flask import current_app
from skylines.model import db


class SRTM(Command):
    """ Download and import elevation data """

    SERVER_URL = 'http://download.xcsoar.org/mapgen/data/srtm3/'

    option_list = (
        Option('--tile', nargs=2, type=int, metavar=('x', 'y'), help='Import SRTM tile x y'),
        Option('--file', nargs='+', metavar=('filename'), help='Import tile from local file(s)'),
    )

    def run(self, tile, file):
        if tile and file:
            print 'Please select either a tile to download or specify local file(s).'
            sys.exit(1)

        # Change path to configured srtm data path
        path = current_app.config['SKYLINES_ELEVATION_PATH']

        if not os.path.exists(path):
            print 'Creating {} ...'.format(path)
            os.mkdir(path)

        if tile:
            os.chdir(path)
            filename = self.download_tile(tile[0], tile[1])
            self.raster2pgsql(filename)

        if file:
            files = []
            for item in file:
                files += glob(item)

            for filename in files:
                abspath = os.path.abspath(filename)
                tiled_tif_filename = os.path.join(path, os.path.basename(abspath))

                if os.path.exists(tiled_tif_filename):
                    print "{} exists already.".format(tiled_tif_filename)
                    continue

                shutil.copy(abspath, tiled_tif_filename)

                self.raster2pgsql(tiled_tif_filename)

    def download_tile(self, x, y):
        if not 1 <= x <= 72:
            print 'x has to be between 1 and 72'
            sys.exit(1)

        if not -4 <= y <= 24:
            print 'y has to be between -4 and 24'
            sys.exit(1)

        basename = 'srtm_{x:02}_{y:02}'.format(x=x, y=y)

        # Check if tiled GeoTIFF file already exists
        tiled_tif_filename = basename + '_tiled.tif'

        if os.path.exists(tiled_tif_filename):
            print "{} exists already.".format(tiled_tif_filename)
            exit()

        # Download TIF file
        tif_filename = basename + '.tif'

        print 'Downloading {} ...'.format(tif_filename)
        url = self.SERVER_URL + tif_filename
        subprocess.check_call(['wget', '-O', tiled_tif_filename, url])

        return tiled_tif_filename

    def raster2pgsql(self, tiled_tif_filename):
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
