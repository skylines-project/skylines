import os
import subprocess

from flask import current_app

from .welt2000_reader import parse_welt2000_waypoints


def __get_database_file(dir_data):
    path = os.path.join(dir_data, 'WELT2000.TXT')

    # Create Welt2000 data folder if necessary
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    # Download the current file
    # (only if server file is newer than local file)
    url = 'http://www.segelflug.de/vereine/welt2000/download/WELT2000.TXT'
    subprocess.check_call(['wget', '-N', '-P', os.path.dirname(path), url])

    # Check if download succeeded
    if not os.path.exists(path):
        raise RuntimeError('Welt2000 database not found at {}'.format(path))

    # Return path to the Welt2000 file
    return path


def get_database(bounds=None, path=None):
    delete_file = False

    if not path:
        # Get Welt2000 file
        path = __get_database_file(current_app.config['SKYLINES_TEMPORARY_DIR'])
        delete_file = True

    # Parse Welt2000 file
    with open(path, "r") as f:
        parsed = parse_welt2000_waypoints(f, bounds)

    if delete_file:
        os.remove(path)

    # Return parsed WaypointList
    return parsed
