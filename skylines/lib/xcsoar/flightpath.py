from collections import namedtuple
from subprocess import Popen, PIPE

from .path import helper_path
from skylines.lib import files

FlightPathFix = namedtuple('FlightPathFix', ['seconds_of_day', 'latitude', 'longitude', 'altitude', 'enl'])


def run_flight_path(path, max_points=None):
    args = [helper_path('FlightPath')]

    if max_points:
        args.append('--max-points={:d}'.format(max_points))

    args.append(path)

    return Popen(args, stdout=PIPE).stdout


def flight_path(igc_file, max_points=1000):
    path = files.filename_to_path(igc_file.filename)
    output = run_flight_path(path, max_points=max_points)
    return map(line_to_fix, output)


def line_to_fix(line):
    line = line.split()
    return FlightPathFix(int(line[0]), float(line[1]), float(line[2]),
                         int(line[3]), int(line[4]))
