import datetime

import xcsoar
from flask import current_app
from skylines.model import db
from skylines.lib import files
from skylines.lib.datetime import from_seconds_of_day
from skylines.lib.xcsoar_.flightpath import flight_path
from skylines.model import (
    Airport, Trace, FlightPhase, TimeZone, Location
)


def read_location(node):
    """
    Reads the latitude and longitude attributes of the node
    and returns a Location instance if the node was parsed correctly.
    """

    if node is None:
        return None

    if 'latitude' not in node or 'longitude' not in node:
        return None

    try:
        latitude = float(node['latitude'])
        longitude = float(node['longitude'])
        return Location(latitude=latitude, longitude=longitude)
    except ValueError:
        return None


def import_location_attribute(node, name):
    """
    Reads a Location instance from an attribute of the node
    with the given name.
    """

    if node is None or name not in node:
        return None

    location = node[name]
    return read_location(location)


def import_datetime_attribute(node, name):
    if node is None or name not in node:
        return None
    if isinstance(node[name], datetime.datetime):
        return node[name]
    else:
        return None


def find_contest(root, name):
    if 'contests' not in root:
        return None

    if name not in root['contests']:
        return None

    return root['contests'][name]


def find_trace(contest, name):
    if not name in contest:
        return None

    return contest[name]


def read_time_of_day(turnpoint, flight):
    if 'time' not in turnpoint:
        return None

    return from_seconds_of_day(flight.takeoff_time.date(),
                               int(turnpoint['time']))


def delete_trace(contest_name, trace_name, flight):
    q = Trace.query(
        flight=flight, contest_type=contest_name, trace_type=trace_name)
    q.delete()


def save_trace(contest_name, trace_name, node, flight):
    delete_trace(contest_name, trace_name, flight)

    if 'turnpoints' not in node:
        return

    locations = []
    times = []
    for turnpoint in node['turnpoints']:
        location = read_location(turnpoint['location'])
        time = read_time_of_day(turnpoint, flight)

        if location is None or time is None:
            continue

        locations.append(location)
        times.append(time)

    if len(locations) < 2 or len(times) < 2:
        return

    trace = Trace()
    trace.contest_type = contest_name
    trace.trace_type = trace_name
    trace.locations = locations
    trace.times = times

    if 'duration' in node:
        trace.duration = datetime.timedelta(seconds=int(node['duration']))

    if 'distance' in node:
        trace.distance = int(node['distance'])

    flight.traces.append(trace)


def save_contest(contest_name, traces, flight):
    for trace_name, trace in traces.iteritems():
        save_trace(contest_name, trace_name, trace, flight)


def save_contests(root, flight):
    if 'contests' not in root or flight.takeoff_time is None:
        # The takeoff_time is needed to convert the
        # time integer to a DateTime instance
        return

    for contest_name, traces in root['contests'].iteritems():
        save_contest(contest_name, traces, flight)


def get_takeoff_date(flight):
    if flight.takeoff_location is None:
        return flight.takeoff_time

    timezone = TimeZone.by_location(flight.takeoff_location)
    if timezone is None:
        return flight.takeoff_time

    return timezone.fromutc(flight.takeoff_time).date()


def save_takeoff(event, flight):
    flight.takeoff_time = import_datetime_attribute(event, 'time')
    flight.takeoff_location = read_location(event['location'])
    if flight.takeoff_location is not None:
        flight.takeoff_airport = Airport.by_location(flight.takeoff_location,
                                                     date=flight.takeoff_time)

    flight.date_local = get_takeoff_date(flight)


def save_landing(event, flight):
    flight.landing_time = import_datetime_attribute(event, 'time')
    flight.landing_location = read_location(event['location'])
    if flight.landing_location is not None:
        flight.landing_airport = Airport.by_location(flight.landing_location,
                                                     date=flight.landing_time)


def save_events(events, flight):
    if 'takeoff' in events:
        save_takeoff(events['takeoff'], flight)
    if 'landing' in events:
        save_landing(events['landing'], flight)


def save_phases(root, flight):
    flight.delete_phases()

    if 'phases' not in root or 'performance' not in root:
        return

    PT_IDX = {'': None,
              'powered': FlightPhase.PT_POWERED,
              'cruise': FlightPhase.PT_CRUISE,
              'circling': FlightPhase.PT_CIRCLING}

    CD_IDX = {'': None,
              'left': FlightPhase.CD_LEFT,
              'mixed': FlightPhase.CD_MIXED,
              'right': FlightPhase.CD_RIGHT,
              'total': FlightPhase.CD_TOTAL}

    for phdata in root['phases']:
        ph = FlightPhase()
        ph.flight = flight
        ph.aggregate = False
        ph.start_time = import_datetime_attribute(phdata, 'start_time')
        ph.end_time = import_datetime_attribute(phdata, 'end_time')
        ph.phase_type = PT_IDX[phdata['type']]
        ph.circling_direction = CD_IDX[phdata['circling_direction']]
        ph.alt_diff = phdata['alt_diff']
        ph.duration = datetime.timedelta(seconds=phdata['duration'])
        ph.distance = phdata['distance']
        ph.speed = phdata['speed']
        ph.vario = phdata['vario']
        ph.glide_rate = phdata['glide_rate']
        ph.count = 1

        db.session.add(ph)

    for statname in ["total", "left", "right", "mixed"]:
        phdata = root['performance']["circling_%s" % statname]
        ph = FlightPhase(flight=flight)
        ph.aggregate = True
        ph.phase_type = FlightPhase.PT_CIRCLING
        ph.fraction = round(phdata['fraction'] * 100)
        ph.circling_direction = CD_IDX[statname]
        ph.alt_diff = phdata['alt_diff']
        ph.duration = datetime.timedelta(seconds=phdata['duration'])
        ph.vario = phdata['vario']
        ph.count = phdata['count']

        db.session.add(ph)

    phdata = root['performance']['cruise_total']
    ph = FlightPhase(flight=flight)
    ph.aggregate = True
    ph.phase_type = FlightPhase.PT_CRUISE
    ph.circling_direction = FlightPhase.CD_TOTAL
    ph.alt_diff = phdata['alt_diff']
    ph.duration = datetime.timedelta(seconds=phdata['duration'])
    ph.fraction = round(phdata['fraction'] * 100)
    ph.distance = phdata['distance']
    ph.speed = phdata['speed']
    ph.vario = phdata['vario']
    ph.glide_rate = phdata['glide_rate']
    ph.count = phdata['count']

    db.session.add(ph)


def get_limits():
    iter_limit = int(current_app.config.get('SKYLINES_ANALYSIS_ITER', 10e6))
    # Each node of the triangle solver has a size of 92 bytes...
    tree_size_limit = int(current_app.config.get('SKYLINES_ANALYSIS_MEMORY', 256)) \
        * 1024 * 1024 / 92

    return dict(iter_limit=iter_limit, tree_size_limit=tree_size_limit)


def get_analysis_times(times):
    chosen_period_seconds = 0
    chosen_period = None

    has_release = [key for key, value in enumerate(times) if 'release' in value]

    if has_release:
        for i in has_release:
            scoring_periods = []

            # gather all possible scoring periods of this flight
            if times[i]['power_states'] and \
                [not state['powered'] for state in times[i]['power_states']
                 if not state['powered']]:
                scoring_start = min(next(state for state in times[i]['power_states']
                                         if not state['powered']),
                                    times[i]['release'],
                                    key=lambda x: x['time'])
            else:
                scoring_start = times[i]['release']

            if times[i]['power_states']:
                for state in times[i]['power_states']:
                    if state['powered'] and state['time'] > scoring_start['time']:
                        scoring_periods.append(
                            dict(takeoff=times[i]['takeoff'],
                                 scoring_start=scoring_start,
                                 scoring_end=min(state,
                                                 times[i]['landing'],
                                                 key=lambda x: x['time']),
                                 landing=times[i]['landing']))

                    elif not state['powered'] and state['time'] > scoring_start['time']:
                        scoring_start = state

            if scoring_start['time'] < times[i]['landing']['time']:
                scoring_periods.append(dict(takeoff=times[i]['takeoff'],
                                            scoring_start=scoring_start,
                                            scoring_end=times[i]['landing'],
                                            landing=times[i]['landing']))

            for period in scoring_periods:
                total_seconds = (period['scoring_end']['time']
                                 - period['scoring_start']['time']).total_seconds()

                if total_seconds > chosen_period_seconds:
                    chosen_period_seconds = total_seconds
                    chosen_period = period

    else:
        for i in range(len(times)):
            total_seconds = (times[i]['landing']['time']
                             - times[i]['takeoff']['time']).total_seconds()

            if total_seconds > chosen_period_seconds:
                chosen_period_seconds = total_seconds
                chosen_period = dict(takeoff=times[i]['takeoff'],
                                     scoring_start=None,
                                     scoring_end=None,
                                     landing=times[i]['landing'])

    return chosen_period


def run_analyse_flight(filename, full=None, triangle=None, sprint=None):
    limits = get_limits()

    flight = xcsoar.Flight(flight_path(filename, add_elevation=True, max_points=None))

    analysis_times = get_analysis_times(flight.times())

    if analysis_times:
        analysis = flight.analyse(analysis_times['takeoff']['time'],
                                  analysis_times['scoring_start']['time']
                                  if analysis_times['scoring_start'] else None,
                                  analysis_times['scoring_end']['time']
                                  if analysis_times['scoring_end'] else None,
                                  analysis_times['landing']['time'],
                                  full=full,
                                  triangle=triangle,
                                  sprint=sprint,
                                  max_iterations=limits['iter_limit'],
                                  max_tree_size=limits['tree_size_limit'])
        analysis['events'] = analysis_times

        return analysis

    else:
        return None


def analyse_flight(flight, full=512, triangle=1024, sprint=64):
    path = files.filename_to_path(flight.igc_file.filename)
    current_app.logger.info('Analyzing ' + path)

    root = run_analyse_flight(
        path, full=full, triangle=triangle, sprint=sprint)

    if root is None:
        current_app.logger.warning('Analyze flight failed.')
        return False

    if 'events' in root:
        save_events(root['events'], flight)

    if flight.takeoff_time is None \
       or flight.landing_time is None:
        return False

    contest = find_contest(root, 'olc_plus')
    if contest is not None:
        trace = find_trace(contest, 'classic')
        if trace is not None and 'distance' in trace:
            flight.olc_classic_distance = int(trace['distance'])
        else:
            flight.olc_classic_distance = None

        trace = find_trace(contest, 'triangle')
        if trace is not None and 'distance' in trace:
            flight.olc_triangle_distance = int(trace['distance'])
        else:
            flight.olc_triangle_distance = None

        trace = find_trace(contest, 'plus')
        if trace is not None and 'score' in trace:
            flight.olc_plus_score = trace['score']
        else:
            flight.olc_plus_score = None

    save_contests(root, flight)
    save_phases(root, flight)

    flight.needs_analysis = False
    return True
