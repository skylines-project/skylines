from datetime import time as Time
from skylines.lib.geo.latlon import LatLon


class Fix:
    """
    Represents a single fix record of an IGC file
    """

    def __init__(self, time, latlon, valid, baro_altitude, gps_altitude):
        self.time = time
        self.latlon = latlon
        self.valid = valid
        self.baro_altitude = baro_altitude
        self.gps_altitude = gps_altitude

    def __str__(self):
        return "{0}, {1}, {2}, {3}".format(self.time, self.latlon,
                                           self.baro_altitude,
                                           self.gps_altitude)


class BaseParser:
    """
    BaseParser is a base class for all IGC parser implementations.

    Overwrite the handle_*() functions if you want to use the corresponding
    IGC file records.
    """

    def parse(self, data):
        """
        Parses the contents of the data parameter assuming it is an IGC file.
        """

        for line in data:
            line = line.strip()
            self.handle_line(line[0].upper(), line[1:])

    def parse_time(self, data):
        """
        Parses a time from the data stream

        e.g. 101039
        """

        hour = int(data[0:2])
        minute = int(data[2:4])
        second = int(data[4:6])
        return Time(hour, minute, second)

    def parse_angle(self, data, is_latitude):
        """
        Parses a latitude/longitude angle from the data stream

        e.g. 5049380N or 00611410E
        """

        if is_latitude:
            degrees = int(data[0:2])
            minutes = int(data[2:4])
            minute_fraction = int(data[4:7])
            is_positive = (data[7] != "S")
        else:
            degrees = int(data[0:3])
            minutes = int(data[3:5])
            minute_fraction = int(data[5:8])
            is_positive = (data[8] != "W")

        angle = degrees + (minutes + minute_fraction / 1000.0) / 60.0
        return angle if is_positive else -angle

    def parse_latlon(self, data):
        """
        Parses a latitude/longitude couple from the data stream

        e.g. 5049380N00611410E
        """

        latitude = self.parse_angle(data, True)
        longitude = self.parse_angle(data[8:], False)
        return LatLon(latitude, longitude)

    def parse_fix_validity(self, data):
        """
        Parses a fix validity character

        e.g. A (Valid) or V (Invalid/Void)
        """

        return data[0] == "A"

    def parse_altitude(self, data):
        """
        Parses a meter-based altitude

        e.g. 00212 (= 212m)
        """

        return int(data[0:5])

    def parse_fix(self, data):
        """
        Parses a B record (logger fix)

        e.g. 1010395049380N00611410EA0021200185
        """

        time = self.parse_time(data)
        latlon = self.parse_latlon(data[6:])
        valid = self.parse_fix_validity(data[23:])
        baro_altitude = self.parse_altitude(data[24:])
        gps_altitude = self.parse_altitude(data[29:])

        return Fix(time, latlon, valid, baro_altitude, gps_altitude)

    def handle_line(self, linetype, data):
        """
        Parses a single line from the IGC file.

        linetype is the uppercase character that describes the
        type of the line.
        """

        if linetype == "B":
            try:
                handle_fix = getattr(self, "handle_fix")
            except AttributeError:
                pass
            else:
                handle_fix(self.parse_fix(data))
