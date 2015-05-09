from flask.ext.script import Command, Option

import re
import shutil
import os.path
import subprocess

from flask import current_app
from geoalchemy2.shape import from_shape
from shapely.geometry import polygon
from shapely.wkt import loads
from shapely.geos import ReadingError
from sqlalchemy.sql.expression import case
from sqlalchemy import func
from skylines.database import db
from skylines.model import Airspace
from skylines.lib.geo import FEET_PER_METER

airspace_re = re.compile(r'^([^#]{1}.*?)\s+(openair|sua)\s+(https?://.*|file://.*)')
airspace_blacklist_re = re.compile(r'^([^#]{1}.*?)\s+(.*)')

msl_re = re.compile(r'^(\d+)\s*(f|ft|m)?\s*([a]?msl|asl|alt)')
msld_re = re.compile(r'^(\d+)\s*(f|ft|m)?$')
flightlevel_re = re.compile(r'^fl\s?(\d+)$')
agl_re = re.compile(r'^(\d+)\s*(f|ft|m)?\s*(agl|gnd|asfc|sfc)')
unl_re = re.compile(r'^unl')
notam_re = re.compile(r'^notam')

airspace_tnp_class = [
    ("A", "CLASSA"),
    ("B", "CLASSB"),
    ("C", "CLASSC"),
    ("D", "CLASSD"),
    ("E", "CLASSE"),
    ("F", "CLASSF"),
    ("G", "CLASSG"),
]

airspace_tnp_types = [
    ("C", "CTR"),
    ("CTA", "CTR"),
    ("CTR", "CTR"),
    ("CTA/CTR", "CTR"),
    ("CTR/CTA", "CTR"),
    ("R", "RESTRICT"),
    ("RESTRICTED", "RESTRICT"),
    ("P", "PROHIBITED"),
    ("PROHIBITED", "PROHIBITED"),
    ("D", "DANGER"),
    ("DANGER", "DANGER"),
    ("G", "WAVE"),
    ("GSEC", "WAVE"),
    ("T", "TMZ"),
    ("TMZ", "TMZ"),
    ("CYR", "RESTRICT"),
    ("CYD", "DANGER"),
    ("CYA", "CLASSF"),
    ("MATZ", "MATZ"),
    ("RMZ", "RMZ"),
]

airspace_openair_class = [
    ("R", "RESTRICT"),
    ("Q", "DANGER"),
    ("P", "PROHIBITED"),
    ("CTR", "CTR"),
    ("A", "CLASSA"),
    ("B", "CLASSB"),
    ("C", "CLASSC"),
    ("D", "CLASSD"),
    ("GP", "NOGLIDER"),
    ("W", "WAVE"),
    ("E", "CLASSE"),
    ("F", "CLASSF"),
    ("TMZ", "TMZ"),
    ("G", "CLASSG"),
    ("RMZ", "RMZ"),
]


class AirspaceCommand(Command):
    """ Download and import airspace files for the mapserver """

    option_list = (
        Option('airspace_list', nargs='?',
               help='airspace list file'),
        Option('airspace_blacklist', nargs='?',
               help='airspace blacklist file'),
        Option('--country', action='append',
               help='Update only the airspace of this country.'),
        Option('--url',
               help='Import single airspace file from file/url. '
                    'You need to specify a country and the filetype '
                    'when using this option.'),
        Option('--filetype',
               help='Choose \'sua\' or \'openair\'.'),
        Option('--debug', action='store_true',
               help='Be more verbose'),
    )

    def run(self, airspace_list, airspace_blacklist, country, url, filetype, debug):
        # the lines in airspace_list contain the following:
        # de openair http://www.daec.de/download/ASDF.txt # for openair files
        # at sua http://www.austrocontrol.at/download/ASDF.sua # for SUA files
        # us sua file://assets/airspace/adsf.sua # for local files

        self.blacklist = {}
        if airspace_blacklist:
            self.import_blacklist(airspace_blacklist)

        if url and len(country) == 1 and filetype:
            self.import_airspace(url, country[0], filetype, debug)
        else:
            with open(airspace_list, "r") as f:

                for line in f:
                    match = airspace_re.match(line)

                    if not match:
                        continue

                    country_code = match.group(1).strip()
                    file_type = match.group(2).strip()
                    url = match.group(3).strip()

                    if debug:
                        print "Found {} with filetype {} and URL {}".format(country_code, file_type, url)

                    if country and country_code.lower() not in country:
                        continue

                    self.import_airspace(url, country_code, file_type, debug)

    def import_blacklist(self, blacklist_file):
        # import airspace blacklist to remove unwanted airspaces (e.g. borderlines)
        # each line contains the country code and the airspace name to remove
        # see provided file for example

        with open(blacklist_file, "r") as f:
            for line in f:
                match = airspace_blacklist_re.match(line)
                if not match:
                    continue

                country_code = match.group(1).strip()
                name = match.group(2).strip()

                if country_code == '' or name == '':
                    continue

                if country_code not in self.blacklist:
                    self.blacklist[country_code] = list()

                self.blacklist[country_code].append(name)

    def import_airspace(self, url, country_code, file_type, debug):
        country_code = country_code.lower()

        filename = os.path.join(
            current_app.config['SKYLINES_TEMPORARY_DIR'], country_code,
            country_code + '.' + file_type)

        if url.startswith('http://') or url.startswith('https://'):
            print "\nDownloading " + url
            filename = self.download_file(filename, url)
        elif url.startswith('file://'):
            filename = url[7:]

        # remove all airspace definitions for the current country
        self.remove_country(country_code)

        if file_type == 'sua':
            self.import_sua(filename, country_code, debug)
        elif file_type == 'openair':
            self.import_openair(filename, country_code, debug)

        if filename.startswith(current_app.config['SKYLINES_TEMPORARY_DIR']):
            shutil.rmtree(os.path.dirname(filename))

    def import_sua(self, filename, country_code, debug):
        from osgeo import ogr

        print "reading " + filename
        country_blacklist = self.blacklist.get(country_code, [])
        temporary_file = os.path.join(
            current_app.config['SKYLINES_TEMPORARY_DIR'],
            os.path.basename(filename) + '.tmp'
        )

        # try to uncomment a CLASS definition, as many SUA files from soaringweb.org have a CLASS comment
        with open(filename, 'r') as in_file:
            with open(temporary_file, 'w') as out_file:
                for line in in_file.xreadlines():
                    out_file.write(line.replace('# CLASS', 'CLASS'))

        if debug:
            print "Trying to open " + temporary_file

        airspace_file = ogr.Open(temporary_file)
        if not airspace_file:
            if debug:
                print "OGR doesn't think that's a airspace file..."
            return

        layer = airspace_file.GetLayerByIndex(0)

        feature = layer.GetFeature(0)
        i = 0
        j = 0
        while(feature):
            feature = layer.GetFeature(i)
            i += 1

            if not feature:
                continue

            name = unicode(feature.GetFieldAsString('title'), 'latin1').strip()

            if name in country_blacklist:
                print name + " is in blacklist"
                continue

            if debug:
                print "Adding " + name

            airspace_class = feature.GetFieldAsString('class').strip()
            airspace_type = feature.GetFieldAsString('type').strip()

            if airspace_type:
                airspace_class = self.parse_airspace_type_tnp(airspace_type)
            elif airspace_class:
                airspace_class = self.parse_airspace_class_tnp(airspace_class)
            else:
                print name + " has neither class nor type"
                continue

            added = self.add_airspace(
                country_code,
                airspace_class,
                name,
                feature.GetFieldAsString('base'),
                feature.GetFieldAsString('tops'),
                "POLYGON" + str(feature.geometry())[8:]
            )

            if not added:
                continue

            if i % 100 == 0:
                print "inserting geometry " + str(i)

            j += 1

        airspace_file.Destroy()
        db.session.commit()

        os.remove(temporary_file)

        print "added " + str(j) + " features for country " + country_code

    def import_openair(self, filename, country_code, debug):
        from osgeo import ogr

        print "reading " + filename
        country_blacklist = self.blacklist.get(country_code, [])

        airspace_file = ogr.Open(filename)
        if not airspace_file:
            if debug:
                print "OGR doesn't think that's a airspace file..."
            return

        layer = airspace_file.GetLayerByIndex(0)

        feature = layer.GetFeature(0)
        i = 0
        j = 0
        while(feature):
            feature = layer.GetFeature(i)
            i += 1

            if not feature:
                continue

            name = unicode(feature.GetFieldAsString('name'), 'latin1').strip()

            if name in country_blacklist:
                print name + " is in blacklist"
                continue

            if debug:
                print "Adding " + name

            airspace_class = feature.GetFieldAsString('class').strip()

            if airspace_class:
                airspace_class = self.parse_airspace_class_openair(airspace_class)
            else:
                print name + " has no class"
                continue

            added = self.add_airspace(
                country_code,
                airspace_class,
                name,
                feature.GetFieldAsString('floor'),
                feature.GetFieldAsString('ceiling'),
                "POLYGON" + str(feature.geometry())[8:]
            )

            if not added:
                continue

            if i % 100 == 0:
                print "inserting geometry " + str(i)

            j += 1

        airspace_file.Destroy()
        db.session.commit()

        print "added " + str(j) + " features for country " + country_code

    def remove_country(self, country_code):
        print "removing all entries for country_code " + country_code
        query = db.session.query(Airspace) \
            .filter(Airspace.country_code == country_code)
        query.delete(synchronize_session=False)
        db.session.commit()

    def download_file(self, path, url):
        # Create data folder if necessary
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        # Download the current file
        # (only if server file is newer than local file)
        subprocess.check_call(['wget',
                               '-q',
                               '-N',
                               '--no-check-certificate',
                               '-U', 'Mozilla/5.0 (Windows NT 5.1; rv:30.0) Gecko/20100101 Firefox/30.0',
                               '-P', os.path.dirname(path),
                               '-O', path,
                               url])

        # Check if download succeeded
        if not os.path.exists(path):
            raise RuntimeError('File not found at {}'.format(path))

        # Return path to the file
        return path

    def parse_airspace_type_tnp(self, airspace_type):
        if airspace_type.startswith('CLASS '):
            as_class = self.parse_airspace_class_tnp(airspace_type[6:])

            if as_class != "OTHER":
                return as_class

        for airspace in airspace_tnp_types:
            if re.search("^" + airspace[0] + "$", airspace_type):
                return airspace[1]

        return "OTHER"

    def parse_airspace_class_tnp(self, airspace_class):
        for airspace in airspace_tnp_class:
            if re.search("^" + airspace[0] + "$", airspace_class[0]):
                return airspace[1]

        return "OTHER"

    def parse_airspace_class_openair(self, airspace_class):
        for airspace in airspace_openair_class:
            if re.search("^" + airspace[0] + "$", airspace_class):
                return airspace[1]

        return "OTHER"

    def add_airspace(self, country_code, airspace_class, name, base, top, geom_str):
        try:
            geom = loads(geom_str)
        except ReadingError:
            print name + "(" + airspace_class + ") is not a polygon (maybe not enough points?)"
            return False

        # orient polygon clockwise
        geom = polygon.orient(geom, sign=-1)

        if not airspace_class:
            print name + " has no airspace class"
            return False

        base = self.normalise_height(base, name)
        top = self.normalise_height(top, name)

        flightlevel_re = re.compile(r'^FL (\d+)$')
        match = flightlevel_re.match(base)
        if match and int(match.group(1)) >= 200:
            print name + " has it's base above FL 200 and is therefore disregarded"
            return False

        airspace = Airspace()
        airspace.country_code = country_code
        airspace.airspace_class = airspace_class
        airspace.name = name
        airspace.base = base
        airspace.top = top

        # Check geometry type, disregard everything except POLYGON
        if geom.geom_type != 'Polygon':
            print name + " is not a polygon (it's a " + geom.geom_type + ")"
            return False

        wkb = from_shape(geom, srid=4326)

        # Try to fix invalid (self-intersecting) geometries
        valid_dump = (func.ST_Dump(func.ST_MakeValid(wkb))).geom
        valid_query = db.session.query(func.ST_SetSRID(valid_dump, 4326)).order_by(func.ST_Area(valid_dump).desc()).first()

        if not valid_query:
            print 'Error importing ' + name
            print 'Could not validate geometry'
            return False
        else:
            wkb = valid_query[0]

        geom_type = db.session.query(func.ST_GeometryType(wkb)).first()[0]

        if geom_type != 'ST_Polygon':
            print name + " got some errors makeing it valid..."
            return False

        tolerance = 0.0000001
        simplify = lambda x: func.ST_SimplifyPreserveTopology(x, tolerance)

        airspace.the_geom = case(
            [
                (func.ST_IsValid(wkb), wkb),
                (func.ST_IsValid(simplify(wkb)), simplify(wkb)),
            ],
            else_=None)

        db.session.add(airspace)

        return True

    def normalise_height(self, height, name):
        height = height.lower().strip()

        # is it GND or SFC?
        if re.search('^(ground|gnd|sfc|msl)$', height): return 'GND'

        # is it a flightlevel?
        match = flightlevel_re.match(height)
        if match: return 'FL {0}'.format(int(match.group(1)))

        # is it AGL?
        match = agl_re.match(height)
        if match and match.group(2) == 'm':
            return '{0} AGL'.format((int(match.group(1)) * FEET_PER_METER))
        elif match:
            return '{0} AGL'.format(int(match.group(1)))

        # is it MSL?
        match = msl_re.match(height)
        if match and match.group(2) == 'm':
            return '{0} MSL'.format(int(match.group(1)) * FEET_PER_METER)
        elif match:
            return '{0} MSL'.format(int(match.group(1)))

        # is it MSL without the msl moniker?
        match = msld_re.match(height)
        if match and match.group(2) == 'm':
            return '{0} MSL'.format(int(match.group(1)) * FEET_PER_METER)
        elif match:
            return '{0} MSL'.format(int(match.group(1)))

        # is it unlimited?
        match = unl_re.match(height)
        if match:
            return 'FL 999'

        # is it notam limited?
        match = notam_re.match(height)
        if match:
            return 'NOTAM'

        print name + " has unknown height format: '" + height + "'"
        return height
