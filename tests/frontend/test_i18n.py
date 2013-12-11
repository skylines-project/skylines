import os
import sys
import glob
from babel.messages.pofile import read_po
import nose


def get_language_code(filename):
    filename = os.path.split(filename)[0]
    filename = os.path.split(filename)[0]
    filename = os.path.split(filename)[1]
    return filename


def test_pofiles():
    for filename in glob.glob(os.path.join('skylines', 'frontend', 'translations', '*', 'LC_MESSAGES', 'messages.po')):
        test_pofiles.func_doc = ('Python string format placeholders must match '
                                 '(lang: {})'.format(get_language_code(filename)))
        yield check_pofile, filename


def check_pofile(filename):
    with open(filename) as fileobj:
        catalog = read_po(fileobj)
        for error in catalog.check():
            print 'Error in message: ' + str(error[0])
            raise AssertionError(error[1][0])


if __name__ == "__main__":
    sys.argv.append(__name__)
    nose.run()
