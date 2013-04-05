#!/usr/bin/python

from setuptools import setup, find_packages

requirements = open('requirements.txt').readlines()
test_requirements = [r for r in open('test-requirements.txt').readlines()
                     if not r.startswith('http')]

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
    install_requires=requirements,
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=requirements + test_requirements,
    package_data={'skylines': ['i18n/*/LC_MESSAGES/*.mo',
                               'templates/*/*',
                               'public/*/*']},
    message_extractors={'skylines': [
            ('**.py', 'python', None),
            ('templates/**.html', 'genshi', None),
            ('templates/**.jinja', 'jinja2', {
                'encoding': 'utf-8',
                'extensions': 'jinja2.ext.with_, jinja2.ext.do'
            }),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = skylines.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
    dependency_links=[
        "http://www.turbogears.org/2.1/downloads/current/",
        "http://github.com/Turbo87/geoalchemy2/tarball/82c76fd#egg=geoalchemy2-0.2dev",
    ],
    zip_safe=False
)
