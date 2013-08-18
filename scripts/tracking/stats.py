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


from skylines import db
from skylines.model import TrackingFix, User


def get_pilot(user_id):
    pilot = User.get(user_id)
    return dict(name=pilot.name, id=pilot.id)


def get_base_query(user_id):
    return db.session.query(TrackingFix).filter_by(pilot_id=user_id)


def gather_statistics(args):
    stats = dict()
    stats['pilot'] = get_pilot(args.user)
    stats['num_fixes'] = get_base_query(args.user).count()
    return stats


def print_statistics(stats):
    pilot = stats.get('pilot')

    print 'Live tracking statistics for user: {} (ID: {})'.format(pilot.get('name'), pilot.get('id'))
    print
    print 'Number of received fixes: {}'.format(stats.get('num_fixes'))


stats = gather_statistics(args)
print_statistics(stats)
