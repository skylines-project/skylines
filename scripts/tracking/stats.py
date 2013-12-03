#!/usr/bin/env python
#
# Analyse live tracks and output statistics.
#

import sys
import os
import argparse
from config import to_envvar

sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description='Analyse live tracks and output statistics.')
parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')
parser.add_argument('--json', action='store_true',
                    help='enable JSON output')
parser.add_argument('user', type=int,
                    help='A user ID')

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


from datetime import timedelta
from itertools import chain
from skylines import app
from skylines.model import db, TrackingFix, User

app.app_context().push()


def get_pilot(user_id):
    pilot = User.get(user_id)
    return dict(name=pilot.name, id=pilot.id)


def get_base_query(user_id):
    return db.session.query(TrackingFix) \
        .filter_by(pilot_id=user_id) \
        .order_by(TrackingFix.time)


def gather_sessions_statistics(user_id):
    sessions = []

    session = None
    last_fix = None
    for fix in chain(get_base_query(user_id), [None]):
        is_start = (last_fix is None)
        is_end = (fix is None)

        # check if this is a new live tracking session (dt > 3 hours)
        dt = (fix.time - last_fix.time) if (fix and last_fix) else None
        is_new_session = dt and dt > timedelta(hours=3)

        # update current session
        if not (is_start or is_new_session or is_end):
            session['num_fixes'] += 1

            dt_secs = dt.total_seconds()
            session['min_dt'] = min(dt_secs, session.get('min_dt', 999999))
            session['max_dt'] = max(dt_secs, session.get('max_dt', 0))

        # save last_fix in session and append it to the session list
        if last_fix and (is_end or is_new_session):
            session['end'] = last_fix.time

            duration = (session.get('end') - session.get('start')).total_seconds()
            if session.get('num_fixes') > 1 and duration > 0:
                session['avg_dt'] = duration / (session.get('num_fixes') - 1)
                session['quality'] = session.get('min_dt') / session.get('avg_dt')

            sessions.append(session)

        # start a new session
        if fix and (is_start or is_new_session):
            session = dict()
            session['start'] = fix.time
            session['num_fixes'] = 1

        last_fix = fix

    return sessions


def gather_statistics(args):
    stats = dict()
    stats['pilot'] = get_pilot(args.user)
    stats['num_fixes'] = get_base_query(args.user).count()
    stats['sessions'] = gather_sessions_statistics(args.user)
    return stats


def print_statistics(stats):
    pilot = stats.get('pilot')
    sessions = stats.get('sessions')

    print 'Live tracking statistics for user: {} (ID: {})'.format(pilot.get('name'), pilot.get('id'))
    print
    print 'Number of sessions: {}'.format(len(sessions))
    print 'Number of received fixes: {}'.format(stats.get('num_fixes'))

    if sessions:
        print
        print 'Sessions:'
        for session in sessions:
            print_session(session)


def print_session(session):
    start = session.get('start')
    end = session.get('end')
    duration = end - start
    duration -= timedelta(microseconds=duration.microseconds)

    print '{date} - {start}-{end} - {duration} - Q {quality:04.2%} - {num_fixes} fixes (dt: {min_dt:.1f}, avg {avg_dt:.1f})'.format(
        date=start.strftime('%d.%m.%Y'),
        start=start.strftime('%H:%M'),
        end=end.strftime('%H:%M'),
        duration=duration,
        quality=session.get('quality', 1),
        num_fixes=session.get('num_fixes'),
        min_dt=session.get('min_dt', 0),
        avg_dt=session.get('avg_dt', 0))


stats = gather_statistics(args)

if args.json:
    from flask import json
    print json.dumps(stats)
else:
    print_statistics(stats)
