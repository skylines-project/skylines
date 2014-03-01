from collections import namedtuple
from skylines.lib import files
from xcsoar import Flight


flightpathfix_fields = ['datetime', 'seconds_of_day',
                        'location', 'altitude', 'pressure_altitude',
                        'enl', 'track', 'groundspeed', 'tas', 'ias',
                        'siu', 'elevation']


class FlightPathFix(namedtuple('FlightPathFix', flightpathfix_fields)):
    def __new__(cls, *args, **kwargs):
        values = [None] * 12

        values[:min(12, len(args))] = args[:12]

        for i, key in enumerate(flightpathfix_fields):
            if key in kwargs:
                values[i] = kwargs[key]

        return super(FlightPathFix, cls).__new__(cls, *values)


def run_flight_path(path, max_points=None):
    flight = Flight(path)

    if max_points:
        flight.reduce(threshold=0, max_points=max_points)

    return flight.path()


def flight_path(igc_file, max_points=1000):
    path = files.filename_to_path(igc_file.filename)
    output = run_flight_path(path, max_points=max_points)
    return map(lambda line: FlightPathFix(*line), output)
