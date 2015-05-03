import os
from subprocess import CalledProcessError, check_output as run
from glob import glob

GJSLINT_COMMAND = 'gjslint'

GJSLINT_OPTIONS = []

GJSLINT_ERRORS = [
    # 'blank_lines_at_top_level',
    'indentation',
    'well_formed_author',
    'no_braces_around_inherit_doc',
    'braces_around_type',
    'optional_type_marker',
    'unused_private_members',
]

JS_FOLDER = os.path.join('skylines', 'frontend', 'static', 'js')


def pytest_generate_tests(metafunc):
    paths = glob(os.path.join(JS_FOLDER, '*.js'))
    metafunc.parametrize('path', paths)


def test_gjslint(path):
    args = [GJSLINT_COMMAND]
    args.extend(GJSLINT_OPTIONS)
    for error in GJSLINT_ERRORS:
        args.extend(['--jslint_error', error])

    args.append(path)

    try:
        run(args)
    except CalledProcessError, e:
        print e.output
        raise AssertionError('gjslint has found errors.')
    except OSError:
        raise OSError('Failed to run gjslint. Please check that you have '
                      'installed it properly.')
