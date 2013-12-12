import pytest
from subprocess import CalledProcessError, check_output as run

FLAKE8_COMMAND = 'flake8'

FLAKE8_INPUTS = [
    'skylines',
    'scripts',
    'tests'
]


def pytest_generate_tests(metafunc):
    metafunc.parametrize('folder', FLAKE8_INPUTS)


def test_flake8(folder):
    """ Run skylines package through flake8 """
    args = [FLAKE8_COMMAND]

    # Append package name that should be checked
    args.append(folder)

    try:
        run(args)
    except CalledProcessError, e:
        print e.output
        raise AssertionError('flake8 has found errors.')
    except OSError:
        raise OSError('Failed to run flake8. Please check that you have '
                      'installed it properly.')


if __name__ == "__main__":
    pytest.main(__file__)
