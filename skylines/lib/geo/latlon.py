class LatLon:
    """
    LatLng is a point defined by it's geographical latitude and longitude.
    """

    def __init__(self, latitude, longitude, check_validity = False):
        """
        Sets the given latitude and longitude values.

        If check_validity is set to True the values will be validated
        to have plausible values and ValueError is thrown if not.
        """

        if check_validity:
            if not (-90 < latitude < 90):
                raise ValueError("Latitude out of bounds")
            if not (-180 < longitude < 180):
                raise ValueError("Longitude out of bounds")

        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        """
        Converts the LatLon instance into a string.

        e.g. "+55.35676, -007.32153"
        """

        return "{0:+09.5f}, {1:+010.5f}".format(self.latitude, self.longitude)
