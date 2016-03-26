#!/usr/bin/env python

from setuptools import setup, find_packages

about = {}
with open("skylines/__about__.py") as fp:
    exec(fp.read(), about)

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__summary__'],
    author=about['__author__'],
    author_email=about['__email__'],
    url=about['__uri__'],
    packages=find_packages(),
    install_requires=[
        'flask==0.10.1',
        'werkzeug==0.9.6',
        'Flask-Babel==0.9',
        'Flask-Assets==0.8',
        'Flask-Login==0.2.9',
        'Flask-Cache==0.12',
        'Flask-Migrate==1.2.0',
        'Flask-Script==0.6.7',
        'Flask-SQLAlchemy==1.0',
        'Flask-WTF==0.9.5',
        'sqlalchemy==0.8.2',
        'alembic==0.6.3',
        'psycopg2==2.5.2',
        'GeoAlchemy2==0.2.3',
        'Shapely==1.3.0',
        'crc16==0.1.1',
        'Markdown==2.4',
        'pytz',
        'webassets==0.8',
        'cssmin==0.1.4',
        'closure==20140110',
        'WebHelpers==1.3',
        'celery[redis]>=3.1,<3.2',
        'xcsoar==0.5',
        'Pygments==1.6',
        'aerofiles==0.1.1',
        'enum34==1.0',
        'pyproj==1.9.3',
        'gevent==1.0.1',
        'webargs==1.2.0',
        'marshmallow==2.6.1',
        'Flask_OAuthlib==0.9.2',
        'oauthlib==0.7.2',
    ],
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
