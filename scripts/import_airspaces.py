#!/usr/bin/env python
#
# Download and import airspace files for the mapserver
#

import sys
import os
import argparse
from config import to_envvar

sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description='Add or update airspace in SkyLines.')
parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')
parser.add_argument('airspace_list', nargs='?',
                    help='airspace list file')
parser.add_argument('airspace_blacklist', nargs='?',
                    help='airspace blacklist file')
parser.add_argument('--country', action='append',
                    help='Update only the airspace of this country.')
parser.add_argument('--url',
                    help='Import single airspace file from file/url. \
                          You need to specify a country and the filetype \
                          when using this option.')
parser.add_argument('--filetype',
                    help='Choose \'sua\' or \'openair\'.')

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


import re
import shutil
import subprocess

from osgeo import ogr
from geoalchemy2.shape import from_shape
from shapely.geometry import polygon
from shapely.wkt import loads
from shapely.geos import ReadingError

from skylines import app, db
from skylines.model import Airspace


blacklist = dict()


def main():
    # the lines in airspace_list contain the following:
    # de openair http://www.daec.de/download/ASDF.txt # for openair files
    # at sua http://www.austrocontrol.at/download/ASDF.sua # for SUA files
    # us sua file://assets/airspace/adsf.sua # for local files

    airspace_re = re.compile(r'^([^#]{1}.*?)\s+(openair|sua)\s+(http://.*|file://.*)')

    if args.airspace_blacklist:
        import_blacklist(args.airspace_blacklist)

    if args.url and len(args.country) == 1 and args.filetype:
        import_airspace(args.url, args.country[0], args.filetype)
    else:
        with open(args.airspace_list, "r") as f:

            for line in f:
                match = airspace_re.match(line)

                if not match:
                    continue

                country_code = match.group(1).strip()
                file_type = match.group(2).strip()
                url = match.group(3).strip()

                if args.country and country_code.lower() not in args.country:
                    continue

                import_airspace(url, country_code, file_type)


def import_blacklist(blacklist_file):
    # import airspace blacklist to remove unwanted airspaces (e.g. borderlines)
    # each line contains the country code and the airspace name to remove
    # see provided file for example
    airspace_blacklist_re = re.compile(r'^([^#]{1}.*?)\s+(.*)')

    with open(blacklist_file, "r") as f:
        for line in f:
            match = airspace_blacklist_re.match(line)
            if not match:
                continue

            country_code = match.group(1).strip()
            name = match.group(2).strip()

            if country_code == '' or name == '':
                continue

            if country_code not in blacklist:
                blacklist[country_code] = list()

            blacklist[country_code].append(name)


def import_airspace(url, country_code, file_type):
    country_code = country_code.lower()

    filename = os.path.join(
        app.config['SKYLINES_TEMPORARY_DIR'], country_code,
        country_code + '.' + file_type)

    if url.startswith('http://'):
        print "\nDownloading " + url
        filename = download_file(filename, url)
    elif url.startswith('file://'):
        filename = url[7:]

    # remove all airspace definitions for the current country
    remove_country(country_code)

    if file_type == 'sua':
        import_sua(filename, country_code)
    elif file_type == 'openair':
        import_openair(filename, country_code)

    if filename.startswith(app.config['SKYLINES_TEMPORARY_DIR']):
        shutil.rmtree(os.path.dirname(filename))


def import_sua(filename, country_code):
    print "reading " + filename
    country_blacklist = blacklist.get(country_code, [])
    temporary_file = os.path.join(app.config['SKYLINES_TEMPORARY_DIR'], os.path.basename(filename) + '.tmp')

    # try to uncomment a CLASS definition, as many SUA files from soaringweb.org have a CLASS comment
    with open(filename, 'r') as in_file:
        with open(temporary_file, 'w') as out_file:
            for line in in_file.xreadlines():
                out_file.write(line.replace('# CLASS', 'CLASS'))

    airspace_file = ogr.Open(temporary_file)
    if not airspace_file:
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

        airspace_class = feature.GetFieldAsString('class').strip()
        airspace_type = parse_airspace_type(feature.GetFieldAsString('type').strip())

        if not airspace_class:
            if airspace_type:
                airspace_class = airspace_type
            else:
                print name + " has neither class nor type"
                continue

        added = add_airspace(
            country_code,
            airspace_class,
            name,
            feature.GetFieldAsString('base'),
            feature.GetFieldAsString('tops'),
            "POLYGON" + str(feature.geometry())[8:])

        if not added:
            continue

        if i % 100 == 0:
            print "inserting geometry " + str(i)

        j += 1

    airspace_file.Destroy()
    db.session.commit()

    os.remove(temporary_file)

    print "added " + str(j) + " features for country " + country_code


def import_openair(filename, country_code):
    print "reading " + filename
    country_blacklist = blacklist.get(country_code, [])

    airspace_file = ogr.Open(filename)
    if not airspace_file:
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

        added = add_airspace(
            country_code,
            feature.GetFieldAsString('class').strip(),
            name,
            feature.GetFieldAsString('floor'),
            feature.GetFieldAsString('ceiling'),
            "POLYGON" + str(feature.geometry())[8:])

        if not added:
            continue

        if i % 100 == 0:
            print "inserting geometry " + str(i)

        j += 1

    airspace_file.Destroy()
    db.session.commit()

    print "added " + str(j) + " features for country " + country_code


def remove_country(country_code):
    print "removing all entries for country_code " + country_code
    query = db.session.query(Airspace) \
        .filter(Airspace.country_code == country_code)
    query.delete(synchronize_session=False)
    db.session.commit()


def download_file(path, url):
    # Create data folder if necessary
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    # Download the current file
    # (only if server file is newer than local file)
    subprocess.check_call(['wget', '-q', '-N', '-P', os.path.dirname(path), '-O', path, url])

    # Check if download succeeded
    if not os.path.exists(path):
        raise RuntimeError('File not found at {}'.format(path))

    # Return path to the file
    return path


def parse_airspace_type(airspace_type):

    if re.search('^C$', airspace_type): return 'CTR'
    if re.search('^CTA$', airspace_type): return 'CTR'
    if re.search('^CTR$', airspace_type): return 'CTR'
    if re.search('^CTA/CTR$', airspace_type): return 'CTR'
    if re.search('^CTR/CTA$', airspace_type): return 'CTR'

    if re.search('^R$', airspace_type): return 'R'
    if re.search('RESTRICTED', airspace_type): return 'R'
    if re.search('CYR', airspace_type): return 'R'

    if re.search('^P$', airspace_type): return 'P'
    if re.search('PROHIBITED', airspace_type): return 'P'

    if re.search('^D$', airspace_type): return 'Q'
    if re.search('DANGER', airspace_type): return 'Q'
    if re.search('CYD', airspace_type): return 'Q'

    if re.search('^G$', airspace_type): return 'W'
    if re.search('GSEC', airspace_type): return 'W'

    if re.search('^T$', airspace_type): return 'TMZ'
    if re.search('TMZ', airspace_type): return 'TMZ'

    if re.search('CYA', airspace_type): return 'F'

    # Military Aerodrome Traffic Zone, not in SUA / OpenAir definition
    if re.search('MATZ', airspace_type): return 'W'

    return None


def add_airspace(country_code, airspace_class, name, base, top, geom_str):
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

    base = normalise_height(base, name)
    top = normalise_height(top, name)

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
    airspace.the_geom = from_shape(geom, srid=4326)

    db.session.add(airspace)

    return True


msl_re = re.compile(r'^(\d+)\s*(f|ft|m)?\s*([a]?msl|asl|alt)')
flightlevel_re = re.compile(r'^fl\s?(\d+)$')
agl_re = re.compile(r'^(\d+)\s*(f|ft|m)?\s*(agl|gnd|asfc|sfc)')
unl_re = re.compile(r'^unl')
notam_re = re.compile(r'^notam')


def normalise_height(height, name):
    height = height.lower().strip()

    # is it GND or SFC?
    if re.search('^(ground|gnd|sfc|msl)$', height): return 'GND'

    # is it a flightlevel?
    match = flightlevel_re.match(height)
    if match: return 'FL {0}'.format(int(match.group(1)))

    # is it AGL?
    match = agl_re.match(height)
    if match and match.group(2) == 'm':
        return '{0} AGL'.format((int(match.group(1)) * 3.2808399))
    elif match:
        return '{0} AGL'.format(int(match.group(1)))

    # is it MSL?
    match = msl_re.match(height)
    if match and match.group(2) == 'm':
        return '{0} MSL'.format(int(match.group(1)) * 3.2808399)
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


if __name__ == '__main__':
    main()
