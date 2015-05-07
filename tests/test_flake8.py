from subprocess import CalledProcessError, check_output as run

FLAKE8_COMMAND = 'flake8'

FLAKE8_INPUTS = [
    'skylines',
    'tests'
]

FLAKE8_EXCLUDES = [
    'geoid.py'
]


def pytest_generate_tests(metafunc):
    metafunc.parametrize('folder', FLAKE8_INPUTS)


def test_flake8(folder):
    """ Run skylines package through flake8 """
    try:
        run([FLAKE8_COMMAND, folder, '--exclude=' + ','.join(FLAKE8_EXCLUDES)])
    except CalledProcessError, e:
        print e.output
        raise AssertionError('flake8 has found errors.')
    except OSError:
        raise OSError('Failed to run flake8. Please check that you have '
                      'installed it properly.')
