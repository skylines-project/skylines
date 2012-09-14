# -*- coding: utf-8 -*-
#quckstarted Options:
#
# sqlalchemy: True
# auth:       sqlalchemy
# mako:       False
#
#

import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

testpkgs = [
    'WebTest >= 1.2.3',
    'nose',
    'coverage',
    'wsgiref',
    'repoze.who-testutil >= 1.0.1',
]

install_requires = [
    "TurboGears2 >= 2.1.4",

    # Pylons 1.0.1 breaks, because it depends on "WebOb>=1.1.1", but
    # TurboGears2 depends on "WebOb==1.0.8"
    "Pylons >= 0.9.7",
    "Pylons <= 1.0",

    "Genshi",
    "zope.sqlalchemy >= 0.4",
    "repoze.tm2 >= 1.0a5",
    "sqlalchemy",
    "sqlalchemy-migrate",
    "repoze.what >= 1.0.8",
    "repoze.who-friendlyform >= 1.0.4",
    "repoze.what-pylons >= 1.0",
    "repoze.who==1.0.19",
    "tgext.admin >= 0.3.11",
    "repoze.what-quickstart>=1.0.9",
    "repoze.what.plugins.sql>=1.0.1",
    "tw.forms",
    "simplejson",
    "skylinespolyencode",
    "psycopg2",
    "geoalchemy",
    "crc16",
    "markdown",
    "pytz",
]

if sys.version_info[:2] == (2, 4):
    testpkgs.extend(['hashlib', 'pysqlite'])
    install_requires.extend(['hashlib', 'pysqlite'])

print install_requires

setup(
    name='SkyLines',
    version='0.1',
    description='',
    author='',
    author_email='',
    #url='',
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=testpkgs,
    package_data={'skylines': ['i18n/*/LC_MESSAGES/*.mo',
                               'templates/*/*',
                               'public/*/*']},
    message_extractors={'skylines': [
            ('**.py', 'python', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = skylines.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [paste.filter_app_factory]
    root = skylines.config.filter:make_root_prefix_middleware
    """,
    dependency_links=[
        "http://www.turbogears.org/2.1/downloads/current/"
    ],
    zip_safe=False
)
