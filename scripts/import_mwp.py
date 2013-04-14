#!/usr/bin/python
#
# Download and import airspace files for the mapserver
#

import sys
import os
import re
import shutil
import math
import subprocess
import transaction
from osgeo import ogr
from paste.deploy.loadwsgi import appconfig
from skylines.config.environment import load_environment
from skylines.model import DBSession, MountainWaveProject
from sqlalchemy import func
from sqlalchemy.sql.expression import not_
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import from_shape
from shapely.geometry import LineString
from tg import config

sys.path.append(os.path.dirname(sys.argv[0]))

conf_path = '/etc/skylines/production.ini'
if len(sys.argv) > 2:
    conf_path = sys.argv[1]
    del sys.argv[1]

if len(sys.argv) != 3:
    print >>sys.stderr, "Usage: %s [config.ini] MountainWaveCenterP.shp \
        MountainWaveExtend.shp" % sys.argv[0]
    sys.exit(1)

conf = appconfig('config:' + os.path.abspath(conf_path))
load_environment(conf.global_conf, conf.local_conf)


def main():
    mwp_center_file = ogr.Open(sys.argv[1])
    if not mwp_center_file:
        return

    mwp_ext_file = ogr.Open(sys.argv[2])
    if not mwp_ext_file:
        return

    mwp_center_layer = mwp_center_file.GetLayerByIndex(0)
    mwp_ext_layer = mwp_ext_file.GetLayerByIndex(0)

    center_feature = mwp_center_layer.GetFeature(0)
    ext_feature = mwp_ext_layer.GetFeature(0)
    i = 0
    j = 0
    while(center_feature):
        center_feature = mwp_center_layer.GetFeature(i)
        ext_feature = mwp_ext_layer.GetFeature(i)

        i += 1

        if not center_feature:
            continue

        name = unicode(center_feature.GetFieldAsString('name'), 'utf-8') \
            .strip()
        country = center_feature.GetFieldAsString('country').strip()
        vertical_value = center_feature.GetFieldAsDouble('verticalve')
        synoptical = center_feature.GetFieldAsString('synoptical').strip()
        main_wind_direction = center_feature.GetFieldAsString('mainwinddi') \
            .strip()
        additional = center_feature.GetFieldAsString('additional').strip()
        source = center_feature.GetFieldAsString('source').strip()
        remark1 = center_feature.GetFieldAsString('remark1').strip()
        remark2 = center_feature.GetFieldAsString('remark2').strip()
        orientation = center_feature.GetFieldAsDouble('orientatio')
        rotor_height = center_feature.GetFieldAsString('rotorheigh').strip()
        weather_dir = center_feature.GetFieldAsInteger('weatherdir')
        location = center_feature.geometry()

        if ext_feature:
            axis_length = ext_feature.GetFieldAsDouble('shape_leng')
            axis = ext_feature.geometry().ExportToWkt()
        else:
            axis_length = None
            axis = None

        wave = MountainWaveProject()
        wave.name = name
        wave.country = country
        wave.vertical_value = vertical_value
        wave.synoptical = synoptical
        wave.main_wind_direction = main_wind_direction
        wave.additional = additional
        wave.source = source
        wave.remark1 = remark1
        wave.remark2 = remark2
        wave.orientation = orientation
        wave.rotor_height = rotor_height
        wave.weather_dir = weather_dir
        wave.axis = WKTElement(axis, srid=4326)
        wave.axis_length = axis_length
        wave.location = WKTElement(location.ExportToWkt(), srid=4326)
        wave.ellipse = ellipse(axis_length / 2,
                               axis_length / 8,
                               -orientation,
                               location.GetX(),
                               location.GetY())

        DBSession.add(wave)

        if i % 100 == 0:
            print "inserting geometry " + str(i)

        j += 1

    mwp_center_file.Destroy()
    mwp_ext_file.Destroy()
    DBSession.flush()
    transaction.commit()

    print "added " + str(j) + " waves"


def ellipse(ra, rb, ang, x0, y0, Nb=50):
    '''
    ra - major axis length
    rb - minor axis length
    ang - angle
    x0,y0 - position of centre of ellipse
    Nb - No. of points that make an ellipse

    based on matlab code ellipse.m written by D.G. Long,
    Brigham Young University, based on the
    CIRCLES.m original
    written by Peter Blattner, Institute of Microtechnology,
    University of
    Neuchatel, Switzerland, blattner@imt.unine.ch
    '''

    def xfrange(start, stop, steps):
        step = (stop - start) / steps
        while start < stop:
            yield start
            start += step

    xpos, ypos = x0, y0
    radm, radn = ra, rb
    an = math.radians(ang)

    co, si = math.cos(an), math.sin(an)

    X = []
    Y = []

    for the in xfrange(0, 2 * math.pi, Nb):
        X.append(radm * math.cos(the) * co - si * radn * math.sin(the) + xpos)
        Y.append(radm * math.cos(the) * si + co * radn * math.sin(the) + ypos)

    # Convert the coordinate into a list of tuples
    coordinates = zip(X, Y)

    # Create a shapely LineString object from the coordinates
    linestring = LineString(coordinates)

    # Save the new path as WKB
    ellipse = from_shape(linestring, srid=4326)

    return ellipse


if __name__ == '__main__':
    main()
