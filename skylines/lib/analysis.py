# -*- coding: utf-8 -*-

import os
import datetime
from lxml import etree
from skylines import files
from tg import config
from skylines.model.geo import Location
import logging

log = logging.getLogger(__name__)


def helper_path(helper):
    return os.path.join(config['skylines.analysis.path'], helper)


def import_location_attribute(node):
    if node is None:
        return None

    try:
        latitude = float(node.attrib['latitude'])
        longitude = float(node.attrib['longitude'])
        return Location(latitude=latitude, longitude=longitude)
    except ValueError:
        return None


def import_datetime_attribute(node, name):
    if node is None or not name in node.attrib:
        return None
    try:
        return datetime.datetime.strptime(node.attrib[name], '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        return None


def find_contest(root, name):
    for contest in root.findall('contest'):
        if contest.attrib['name'] == name:
            return contest
    return None


def find_trace(contest, name):
    for contest in contest.findall('trace'):
        if contest.attrib['name'] == name:
            return contest
    return None


def analyse_flight(flight):
    path = files.filename_to_path(flight.filename)

    with os.popen(helper_path('AnalyseFlight') + ' "' + path + '"') as f:
        try:
            doc = etree.parse(f)
        except etree.Error:
            log.error('Parsing the output of AnalyseFlight failed.')

            if log.isEnabledFor(logging.DEBUG):
                with os.popen(helper_path('AnalyseFlight') + ' "' + path + '"') as f_debug:
                    log.debug(f_debug.readlines())

            return False

    root = doc.getroot()

    times = root.find('times')
    flight.takeoff_time = import_datetime_attribute(times, "takeoff")
    flight.landing_time = import_datetime_attribute(times, "landing")

    locations = root.find('locations')
    if locations:
        flight.takeoff_location = import_location_attribute(locations.find('takeoff'))
        flight.landing_location = import_location_attribute(locations.find('landing'))

    contest = find_contest(root, 'olc_plus')
    if contest is not None:
        trace = find_trace(contest, 'classic')
        if trace is not None:
            flight.olc_classic_distance = int(float(trace.attrib['distance']))
        else:
            flight.olc_classic_distance = None

        trace = find_trace(contest, 'triangle')
        if trace is not None:
            flight.olc_triangle_distance = int(float(trace.attrib['distance']))
        else:
            flight.olc_triangle_distance = None

        trace = find_trace(contest, 'plus')
        if trace is not None:
            flight.olc_plus_score = int(float(trace.attrib['score']))
        else:
            flight.olc_plus_score = None

    return True


def flight_path(flight, max_points = 1000):
    path = files.filename_to_path(flight.filename)
    f = os.popen(helper_path('FlightPath') + ' --max-points=' + str(max_points) + ' "' + path + '"')

    path = []
    for line in f:
        line = line.split()
        path.append((int(line[0]), float(line[1]), float(line[2]), int(line[3])))
    return path
