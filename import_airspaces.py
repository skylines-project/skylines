#!/usr/bin/python
#
# Download and import airspace files for the mapserver
#

import sys, os, re, shutil
import subprocess
from osgeo import ogr

import transaction
from paste.deploy.loadwsgi import appconfig
from skylines.config.environment import load_environment
from skylines.model import DBSession, Airspace
from sqlalchemy import func
from sqlalchemy.sql.expression import not_
from geoalchemy import WKTSpatialElement
from geoalchemy.functions import functions
from tg import config

sys.path.append(os.path.dirname(sys.argv[0]))

conf_path = '/etc/skylines/production.ini'
if len(sys.argv) > 2:
    conf_path = sys.argv[1]
    del sys.argv[1]

if len(sys.argv) != 3:
    print >>sys.stderr, "Usage: %s [config.ini] airspace_list.txt airspace_blacklist.txt" % sys.argv[0]
    sys.exit(1)

airspace_list = sys.argv[1]
airspace_blacklist = sys.argv[2]
blacklist = dict()

conf = appconfig('config:' + os.path.abspath(conf_path))
load_environment(conf.global_conf, conf.local_conf)


def main():
    # the lines in airspace_list contain the following:
    # de openair http://www.daec.de/download/ASDF.txt # for openair files
    # at sua http://www.austrocontrol.at/download/ASDF.sua # for SUA files
    # us sua file://assets/airspace/adsf.sua # for local files

    airspace_re = re.compile(r'^([^#]{1}.*?)\s+(openair|sua)\s+(http://.*|file://.*)')

    # import airspace blacklist to remove unwanted airspaces (e.g. borderlines)
    # each line contains the country code and the airspace name to remove
    # see provided file for example
    airspace_blacklist_re = re.compile(r'^([^#]{1}.*?)\s+(.*)')

    with open(airspace_blacklist, "r") as f:
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

    with open(airspace_list, "r") as f:

        for line in f:
            match = airspace_re.match(line)

            if not match:
                continue
 
            country_code = match.group(1).strip()
            url = match.group(3).strip()
            filename = os.path.join(config['skylines.temporary_dir'], country_code, \
                match.group(1).strip() + '.' + match.group(2))

            if url.startswith('http://'):
                print "\nDownloading " + url
                filename = download_file(filename, url)
            elif url.startswith('file://'):
                filename = url[7:]

            # remove all airspace definitions for the current country
            remove_country(country_code)

            if filename.endswith('sua'):
                import_sua(filename, country_code)
            elif filename.endswith('openair'):
                import_openair(filename, country_code)

            if filename.startswith(config['skylines.temporary_dir']):
                shutil.rmtree(os.path.dirname(filename))


def import_sua(filename, country_code):
    print "reading " + filename
    country_blacklist = blacklist.get(country_code, [])
    temporary_file = os.path.join(config['skylines.temporary_dir'], os.path.basename(filename) + '.tmp')

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

        geom_str = "POLYGON" + str(feature.geometry())[8:]
        name = unicode(feature.GetFieldAsString('title'), 'latin1').strip()
        airspace_class = feature.GetFieldAsString('class').strip()
        airspace_type = parse_airspace_type(feature.GetFieldAsString('type').strip())

        # this is a real kludge to determine if the polygon has more than 3 points...
        if (geom_str.count(',') < 3):
            print name + "(" + airspace_class + ") has not enough points to be a polygon"
            continue

        if not airspace_class:
            if airspace_type:
                airspace_class = airspace_type
            else:
                print name + " has neither class nor type"
                continue

        if name in country_blacklist:
            print name + " is in blacklist"
            continue

        airspace = Airspace()
        airspace.country_code = country_code
        airspace.airspace_class = airspace_class
        airspace.name = name
        airspace.base = feature.GetFieldAsString('base')
        airspace.top = feature.GetFieldAsString('tops')
        airspace.the_geom = WKTSpatialElement(geom_str)

        if i%100 == 0:
            print "inserting geometry " + str(i)

        j += 1
        DBSession.add(airspace)

    airspace_file.Destroy()
    DBSession.flush()
    transaction.commit()

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

        geom_str = "POLYGON" + str(feature.geometry())[8:]
        name = unicode(feature.GetFieldAsString('name'), 'latin1').strip()
        airspace_class = feature.GetFieldAsString('class').strip()

        # this is a real kludge to determine if the polygon has more than 3 points...
        if (geom_str.count(',') < 3):
            print name + "(" + airspace_class + ") has not enough points to be a polygon"
            continue

        if not airspace_class:
            print name + " has no airspace class"
            continue

        if name in country_blacklist:
            print name + " is in blacklist"
            continue

        airspace = Airspace()
        airspace.country_code = country_code
        airspace.airspace_class = airspace_class
        airspace.name = name
        airspace.base = feature.GetFieldAsString('floor')
        airspace.top = feature.GetFieldAsString('ceiling')
        airspace.the_geom = WKTSpatialElement(geom_str)

        if i%100 == 0:
            print "inserting geometry " + str(i)

        j += 1
        DBSession.add(airspace)

    airspace_file.Destroy()
    DBSession.flush()
    transaction.commit()

    print "added " + str(j) + " features for country " + country_code

def remove_country(country_code):
    print "removing all entries for country_code " + country_code
    query = DBSession.query(Airspace) \
        .filter(Airspace.country_code == country_code)
    query.delete(synchronize_session=False)
    DBSession.flush()
    transaction.commit()


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


if __name__ == '__main__':
    main()
