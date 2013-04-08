from subprocess import Popen, PIPE
from collections import namedtuple
from skylines.lib import files
from skylines.lib.xcsoar.path import helper_path

FlightPathFix = namedtuple('FlightPathFix', ['seconds_of_day', 'latitude', 'longitude', 'altitude', 'enl'])


def flight_path(igc_file, max_points=1000):
    args = [
        helper_path('FlightPath'),
        '--max-points=' + str(max_points),
        files.filename_to_path(igc_file.filename),
    ]

    p = Popen(args, stdout=PIPE)

    path = []
    for line in p.stdout:
        line = line.split()
        path.append(FlightPathFix(int(line[0]), float(line[1]), float(line[2]), int(line[3]), int(line[4])))

    return path
