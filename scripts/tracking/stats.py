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
parser.add_argument('user', type=int,
                    help='A user ID')

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


from datetime import timedelta
from itertools import chain
from skylines import db
from skylines.model import TrackingFix, User


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


        # save last_fix in session and append it to the session list
        if is_end or is_new_session:
            session['end'] = last_fix.time
            sessions.append(session)

        # start a new session
        if is_start or is_new_session:
            session = dict()
            session['start'] = fix.time

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
    print
    print 'Sessions:'
    for session in sessions:
        print '{date}: {start}-{end}'.format(
            date=session.get('start').strftime('%d.%m.%Y'),
            start=session.get('start').strftime('%H:%M'),
            end=session.get('end').strftime('%H:%M'))


stats = gather_statistics(args)
print_statistics(stats)
