# -*- coding: utf-8 -*-

import os
from lxml import etree
from skylines import files

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
    f = os.popen('/opt/skylines/bin/AnalyseFlight "' + path + '"')
    doc = etree.parse(f)
    f.close()
    root = doc.getroot()

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
