#!/usr/bin/env python

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
                'extensions': 'jinja2.ext.with_, jinja2.ext.do, webassets.ext.jinja2.AssetsExtension'
            }),
            ('public/**', 'ignore', None)]},

    zip_safe=False
)
