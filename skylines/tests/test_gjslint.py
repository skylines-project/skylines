import os
import sys
import nose
from subprocess import CalledProcessError, check_output as run
from functools import partial

GJSLINT_COMMAND = 'gjslint'

GJSLINT_OPTIONS = []

JS_BASE_FOLDER = os.path.join('skylines', 'public', 'js')

JS_FILES = [
    'flight.js',
    'general.js',
    'map.js',
    'topbar.js',
    'tracking.js',
    'units.js',
]


def get_language_code(filename):
    filename = os.path.split(filename)[0]
    filename = os.path.split(filename)[0]
    filename = os.path.split(filename)[1]
    return filename


def test_js_files():
    for filename in JS_FILES:
        f = partial(run_gjslint, filename)
        f.description = 'gjslint {}'.format(filename)
        yield f


def run_gjslint(filename):
    path = os.path.join(JS_BASE_FOLDER, filename)

    args = [GJSLINT_COMMAND]
    args.extend(GJSLINT_OPTIONS)
    args.append(path)

    try:
        run(args)
    except CalledProcessError, e:
        print e.output
        raise AssertionError('gjslint has found errors.')
    except OSError:
        raise OSError('Failed to run gjslint. Please check that you have '
                      'installed it properly.')


if __name__ == "__main__":
    sys.argv.append(__name__)
    nose.run()
