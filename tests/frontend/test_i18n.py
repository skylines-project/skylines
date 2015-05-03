import os
from glob import glob
from babel.messages.pofile import read_po

TRANSLATION_PATH = os.path.join('skylines', 'frontend', 'translations')


def get_language_code(filename):
    filename = os.path.split(filename)[0]
    filename = os.path.split(filename)[0]
    filename = os.path.split(filename)[1]
    return filename


def pytest_generate_tests(metafunc):
    pattern = os.path.join(TRANSLATION_PATH, '*', 'LC_MESSAGES', 'messages.po')
    languages = map(get_language_code, glob(pattern))
    metafunc.parametrize('language', languages)


def test_pofile(language):
    path = os.path.join(TRANSLATION_PATH, language, 'LC_MESSAGES', 'messages.po')
    with open(path) as fileobj:
        catalog = read_po(fileobj)

        errors = list(catalog.check())
        if errors:
            for message, merrors in errors:

                print 'Translation Error:'
                for error in merrors:
                    s = str(error)
                    if message.lineno:
                        s += ' (line ' + str(message.lineno) + ')'
                    print s

                print
                print str(message.id) + '\n'
                print str(message.string) + '\n\n'

            raise AssertionError("There are errors in the translation files. Please check the captured output.")
