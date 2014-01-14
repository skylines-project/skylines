#!/usr/bin/env python

from setuptools import setup, find_packages

requirements = [
    'flask==0.10.1',
    'werkzeug==0.9.4',
    'Flask-Babel==0.9',
    'Flask-Assets==0.8',
    'Flask-Login==0.2.7',
    'Flask-Cache==0.12',
    'Flask-Migrate==1.1.0',
    'Flask-Script==0.6.6',
    'Flask-SQLAlchemy==1.0',
    'Flask-WTF==0.9.3',
    'sqlalchemy==0.8.2',
    'alembic==0.6.0',
    'skylinespolyencode==0.1.3',
    'psycopg2==2.4.6',
    'geoalchemy2==0.2.1',
    'shapely==1.2.18',
    'crc16==0.1.1',
    'markdown==2.3.1',
    'pytz',
    'webassets==0.8',
    'cssmin==0.1.4',
    'twisted==13.1',
    'closure==20121212',
    'WebHelpers==1.3',
    'celery_with_redis==3.0',
    'xcsoar==0.1.1',
    'Pygments==1.6',
]

setup(
    name='SkyLines',
    version='0.1',
    description='',
    author='',
    author_email='',
    url='http://www.skylines-project.org/',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=requirements,
    include_package_data=True,
    package_data={
        'skylines': [
            'i18n/*/LC_MESSAGES/*.mo',
            'templates/*/*',
            'assets/static/*/*'
        ]
    },
    zip_safe=False
)
