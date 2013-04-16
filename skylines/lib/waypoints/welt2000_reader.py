import re

from .waypoint import Waypoint


def __parse_line(line, bounds=None):
    # Ignore comments
    if line.startswith('$'):
        return None

    # Parse latitude
    lat = line[45:52]
    lat_neg = lat.startswith('S')
    lat = float(lat[1:3]) + float(lat[3:5]) / 60. + float(lat[5:7]) / 3600.
    if lat_neg:
        lat = -lat

    if bounds and (lat > bounds.top or lat < bounds.bottom):
        return None

    # Parse longitude
    lon = line[52:60]
    lon_neg = lon.startswith('W')
    lon = float(lon[1:4]) + float(lon[4:6]) / 60. + float(lon[6:8]) / 3600.
    if lon_neg:
        lon = -lon

    if bounds and (lon > bounds.right or lon < bounds.left):
        return None

    # Create waypoint instance
    wp = Waypoint()
    wp.latitude = lat
    wp.longitude = lon

    # Parse elevation
    elev = line[41:45].strip()
    if elev != '':
        wp.altitude = float(elev)
    else:
        wp.altitude = 0.0

    # Extract short name
    wp.short_name = line[:6].strip()

    # Parse and strip optional type identifier from short name
    if wp.short_name.endswith('1'):
        wp.type = 'airport'
        wp.short_name = wp.short_name[:5]

    elif wp.short_name.endswith('2'):
        wp.type = 'outlanding'
        wp.short_name = wp.short_name[:5]

    # Extract waypoint name
    wp.name = line[7:41].strip()

    # Check for extra data indicator
    if '*' in wp.name or '#' in wp.name:
        # Split data from waypoint name
        data = wp.name[17:]
        wp.name = wp.name[:16].strip()

        # Check waypoint name for glider site indicator
        if wp.name.endswith('GLD'):
            wp.name = wp.name[:-3].strip()
            wp.type = 'glider_site'

        # Extract ICAO code if possible
        icao = data[:4].strip('!? ')

        # Check icao code field for glider site indicator
        if icao == 'GLD':
            wp.type = 'glider_site'

        # Check icao code field for ultra light indicator
        if icao == 'ULM' and not wp.type:
            wp.type = 'ulm'

        # Save ICAO code
        if len(icao) == 4:
            wp.icao = icao

        # Extract and parse surface character
        if data[4:5] == 'A': wp.surface = 'asphalt'
        elif data[4:5] == 'C': wp.surface = 'concrete'
        elif data[4:5] == 'L': wp.surface = 'loam'
        elif data[4:5] == 'S': wp.surface = 'sand'
        elif data[4:5] == 'Y': wp.surface = 'clay'
        elif data[4:5] == 'G': wp.surface = 'grass'
        elif data[4:5] == 'V': wp.surface = 'gravel'
        elif data[4:5] == 'D': wp.surface = 'dirt'

        # Extract and parse runway length and direction
        runway_len = data[5:8].strip()
        if runway_len != '':
            wp.runway_len = int(runway_len) * 10

        runway_dir = data[8:10].strip()
        if runway_dir != '':
            wp.runway_dir = int(runway_dir) * 10

        # Extract and parse radio frequency
        freq = data[12:17].strip()
        if len(freq) == 5:
            if freq.endswith('2') or freq.endswith('7'):
                freq += '5'
            else:
                freq += '0'
            wp.freq = float(freq) / 1000.

    # Strip uninvited characters from waypoint name
    wp.name = wp.name.rstrip('!?1 ')

    # Find waypoint type from waypoint name if not available yet
    if not wp.type:
        if re.search('(^|\s)BERG($|\s)', wp.name): wp.type = 'mountain top'
        if re.search('(^|\s)COL($|\s)', wp.name): wp.type = 'mountain pass'
        if re.search('(^|\s)PASS($|\s)', wp.name): wp.type = 'mountain pass'
        if re.search('(^|\s)TOP($|\s)', wp.name): wp.type = 'mountain top'
        if re.search('(\s)A(\d){0,3}($|\s)', wp.name): wp.type = 'highway exit'
        if re.search('(\s)AB(\d){0,3}($|\s)', wp.name): wp.type = 'highway exit'
        if re.search('(\s)BAB(\d){0,3}($|\s)', wp.name): wp.type = 'highway exit'
        if re.search('(\s)(\w){0,3}XA(\d){0,3}($|\s)', wp.name): wp.type = 'highway cross'
        if re.search('(\s)(\w){0,3}YA(\d){0,3}($|\s)', wp.name): wp.type = 'highway junction'
        if re.search('(\s)STR($|\s)', wp.name): wp.type = 'road'
        if re.search('(\s)SX($|\s)', wp.name): wp.type = 'road cross'
        if re.search('(\s)SY($|\s)', wp.name): wp.type = 'road junction'
        if re.search('(\s)EX($|\s)', wp.name): wp.type = 'railway cross'
        if re.search('(\s)EY($|\s)', wp.name): wp.type = 'railway junction'
        if re.search('(\s)TR($|\s)', wp.name): wp.type = 'gas station'
        if re.search('(\s)BF($|\s)', wp.name): wp.type = 'railway station'
        if re.search('(\s)RS($|\s)', wp.name): wp.type = 'railway station'
        if re.search('(\s)BR($|\s)', wp.name): wp.type = 'bridge'
        if re.search('(\s)TV($|\s)', wp.name): wp.type = 'tower'
        if re.search('(\s)KW($|\s)', wp.name): wp.type = 'powerplant'

    # Format waypoint name properly
    wp.name = wp.name.title()

    # Strip duplicate spaces from waypoint name
    wp.name = re.sub(r' {2,}', ' ', wp.name)

    # Extract country code
    wp.country_code = line[60:62].strip()

    return wp


def parse_welt2000_waypoints(lines, bounds=None):
    waypoint_list = []

    for line in lines:
        wp = __parse_line(line, bounds)
        if wp:
            waypoint_list.append(wp)

    return waypoint_list
