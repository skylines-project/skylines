from skylines.model.geo import Location


class Waypoint(Location):
    def __init__(self):
        super(Waypoint, self).__init__()

        self.altitude = 0
        self.name = ''
        self.short_name = ''
        self.icao = ''
        self.country_code = ''
        self.surface = None
        self.runway_len = None
        self.runway_dir = None
        self.freq = None
        self.type = None

    def __str__(self):
        return '{}, {}, {}, {}'.format(self.name,
                                       super(Waypoint, self).__str__(),
                                       self.altitude,
                                       self.type)
