# SkyLines

*SkyLines* is a web platform where pilots can share their flights with others
after, or even during flight via live tracking.  *SkyLines* is a sort of social
network for pilots including rankings, statistics and other interesting
features.  Most of all *SkyLines* is truly open in all regards compared to
other similar platforms.

*SkyLines* has started development in 2012 as a spin-off from the popular
[XCSoar](http://www.xcsoar.org/) glide computer. Internally *SkyLines* is still
sharing some code with XCSoar in the algorithmic areas and is providing the
base for XCSoar's live tracking functionalities.

*SkyLines* is far from finished yet, but it has been running in production for
quite some time now. You can reach the official server at
<http://www.skylinescondor.com>.

Build Status: [![Build Status](https://travis-ci.org/skylines-project/skylines.png?branch=master)](https://travis-ci.org/skylines-project/skylines)

## Getting the source

The *SkyLines* source code is managed with [git](http://www.git-scm.com/).
It can be downloaded with the following command:

    $ git clone git://github.com/hess8/skylinesC.git

For more information, please refer to the [git documentation](http://git-scm.com/documentation).

## Installation and Setup

*SkyLines* is based on Python and depends on the following major components:

* [PostgreSQL](http://www.postgresql.org/) database with
  [PostGIS 2.x](http://www.postgis.net/) extension
* [Flask](http://flask.pocoo.org/) web application microframework for Python
* [SQLAlchemy](http://www.sqlalchemy.org/) ORM framework with
  [GeoAlchemy 2](https://geoalchemy-2.readthedocs.org) extension
* [gevent](http://www.gevent.org/) coroutine-based network library for Python (used for
  the live tracking server)

The process of installing these components and setting up a server for local
development is described in the [INSTALL.md](INSTALL.md) file.

## Contact and Contributing

You read about news on [Facebook](https://www.facebook.com/skylines.project) and
[Twitter](https://twitter.com/skylinesproject). If you want to talk to us directly
join our [Slack](https://skylines-slack.herokuapp.com/) community.

Bugs and feature request can be submitted here on
[GitHub](https://github.com/hess8/skylinesC/issues). New ideas can
also be discussed in the
[Wiki](https://github.com/hess8/skylinesC/wiki) first.

Patches should be submitted using the
[Pull Request](https://github.com/hess8/skylinesC/pulls) system of
GitHub because of the integration with
[TravisCI](https://travis-ci.org/skylines-project/skylines).

Here are a few guidelines for creating patches:

- patches should be self-contained
- patches should be self-documenting  
  (add a good description on what is changed, and why you are changing it)
- write one patch for one change

## License

    SkyLines - the free internet platform for sharing flights
    Copyright (C) 2012-2019  The SkyLines Team (see AUTHORS.md)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

You can find the full license text in the [LICENSE](LICENSE) file.
