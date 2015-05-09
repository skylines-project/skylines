from flask.ext.script import Command, Option

import math
from skylines.database import db
from skylines.model import MountainWaveProject
from skylines.lib.string import isnumeric
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import from_shape
from shapely.geometry import LineString


class MWP(Command):
    """ Import data from the Mountain Wave Project """

    option_list = (
        Option('center_shapefile', metavar='MountainWaveCenterP.shp'),
        Option('extend_shapefile', metavar='MountainWaveExtend.shp'),
    )

    def run(self, center_shapefile, extend_shapefile):
        from osgeo import ogr

        mwp_center_file = ogr.Open(center_shapefile)
        if not mwp_center_file:
            return

        mwp_ext_file = ogr.Open(extend_shapefile)
        if not mwp_ext_file:
            return

        mwp_center_layer = mwp_center_file.GetLayerByIndex(0)
        mwp_ext_layer = mwp_ext_file.GetLayerByIndex(0)

        center_feature = mwp_center_layer.GetFeature(0)
        ext_feature = mwp_ext_layer.GetFeature(0)

        # it seems we have some data in the files. clear mwp table first
        db.session.query(MountainWaveProject).delete()

        i = 0
        j = 0
        while center_feature:
            center_feature = mwp_center_layer.GetFeature(i)
            ext_feature = mwp_ext_layer.GetFeature(i)

            i += 1

            if not center_feature:
                continue

            name = center_feature.GetFieldAsString('name') \
                .strip()
            country = center_feature.GetFieldAsString('country').strip()
            vertical_value = center_feature.GetFieldAsDouble('verticalve')
            synoptical = center_feature.GetFieldAsString('synoptical').strip()

            if center_feature.GetFieldAsString('mainwinddi').strip() != "None":
                main_wind_direction = center_feature \
                    .GetFieldAsString('mainwinddi').strip()
            else:
                main_wind_direction = None

            additional = center_feature.GetFieldAsString('additional').strip()
            source = center_feature.GetFieldAsString('source').strip()
            remark1 = center_feature.GetFieldAsString('remark1').strip()
            remark2 = center_feature.GetFieldAsString('remark2').strip()
            orientation = center_feature.GetFieldAsDouble('orientatio')
            rotor_height = center_feature.GetFieldAsString('rotorheigh').strip()
            weather_dir = self.parse_wind_direction(main_wind_direction)
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
            wave.ellipse = self.ellipse(
                axis_length / 2, axis_length / 8, -orientation,
                location.GetX(), location.GetY())

            db.session.add(wave)

            if i % 100 == 0:
                print "inserting geometry " + str(i)

            j += 1

        mwp_center_file.Destroy()
        mwp_ext_file.Destroy()
        db.session.commit()

        print "added " + str(j) + " waves"

    def ellipse(self, ra, rb, ang, x0, y0, Nb=50):
        """
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
        """

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

    def parse_wind_direction(self, direction):
        if not direction:
            return None

        if isnumeric(direction):
            return float(direction)

        direction = direction.upper().replace('O', 'E')

        if direction == 'N':
            return 0
        elif direction == 'NNE':
            return 22.5
        elif direction == 'NE':
            return 45
        elif direction == 'ENE':
            return 67.5
        elif direction == 'E':
            return 90
        elif direction == 'ESE':
            return 112.5
        elif direction == 'SE':
            return 135
        elif direction == 'SSE':
            return 157.5
        elif direction == 'S':
            return 180
        elif direction == 'SSW':
            return 202.5
        elif direction == 'SW':
            return 225
        elif direction == 'WSW':
            return 247.5
        elif direction == 'W':
            return 270
        elif direction == 'WNW':
            return 292.5
        elif direction == 'NW':
            return 315
        elif direction == 'NNW':
            return 337.5
        else:
            return None
