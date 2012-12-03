import os
from collections import namedtuple
from skylines.lib import files
from skylines.lib.xcsoar.path import helper_path


FlightPathFix = namedtuple('FlightPathFix', ['seconds_of_day', 'latitude', 'longitude', 'altitude', 'enl'])

def flight_path(igc_file, max_points = 1000):
    path = files.filename_to_path(igc_file.filename)
    f = os.popen(helper_path('FlightPath') + ' --max-points=' + str(max_points) + ' "' + path + '"')

    path = []
    for line in f:
        line = line.split()
        path.append(FlightPathFix(int(line[0]), float(line[1]), float(line[2]), int(line[3]), int(line[4])))
    return path
