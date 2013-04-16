from collections import namedtuple
from subprocess import Popen, PIPE

from .path import helper_path
from skylines.lib import files

FlightPathFix = namedtuple('FlightPathFix', ['seconds_of_day', 'latitude', 'longitude', 'altitude', 'enl'])


def flight_path(igc_file, max_points=1000):
    args = [
        helper_path('FlightPath'),
        '--max-points=' + str(max_points),
        files.filename_to_path(igc_file.filename),
    ]

    return map(line_to_fix, Popen(args, stdout=PIPE).stdout)


def line_to_fix(line):
    line = line.split()
    return FlightPathFix(int(line[0]), float(line[1]), float(line[2]),
                         int(line[3]), int(line[4]))
