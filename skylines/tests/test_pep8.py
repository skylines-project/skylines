import sys
import nose
from subprocess import CalledProcessError, check_output as run

PEP8_COMMAND = 'pep8'

PEP8_OPTIONS = []

PEP8_IGNORE_ERRORS = [
    'E501',
    'E701',
    'E126',
    'E711',
]


def test_pep8():
    """ Run skylines package through pep8 """
    args = [PEP8_COMMAND]

    # Append custom options
    args.extend(PEP8_OPTIONS)

    # Append ignored errors
    if len(PEP8_IGNORE_ERRORS) != 0:
        args.append('--ignore=' + ','.join(PEP8_IGNORE_ERRORS))

    # Append package name that should be checked
    args.append('skylines')

    try:
        run(args)
    except CalledProcessError, e:
        print e.output
        raise AssertionError('pep8 has found errors.')
    except OSError:
        raise OSError('Failed to run pep8. Please check that you have '
                      'installed it properly.')


if __name__ == "__main__":
    sys.argv.append(__name__)
    nose.run()
