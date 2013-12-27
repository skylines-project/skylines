import sys
from flask.ext.script import Command, Option

import os
import subprocess
from flask import current_app
from skylines.model import db


class SRTM(Command):
    """ Download and import elevation data """

    SERVER_URL = 'http://download.xcsoar.org/mapgen/data/srtm3/'

    option_list = (
        Option('x', type=int),
        Option('y', type=int),
    )

    def run(self, x, y):
        if not 1 <= x <= 72:
            print 'x has to be between 1 and 72'
            sys.exit(1)

        if not -4 <= y <= 24:
            print 'y has to be between -4 and 24'
            sys.exit(1)

        basename = 'srtm_{x:02}_{y:02}'.format(x=x, y=y)

        # Change path to configured srtm data path
        path = current_app.config['SKYLINES_ELEVATION_PATH']

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
        url = self.SERVER_URL + tif_filename
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
