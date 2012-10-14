# SkyLines

Welcome to *SkyLines*, the internet platform for sharing flights!

This project is in an early stage of development.

*SkyLines* is brought to you by the [XCSoar](http://www.xcsoar.org) project.
It is free software; the source code is available [here](http://git.xcsoar.org/cgit/mirror/Skylines.git/)

# Getting the source

The *SkyLines* source code is managed with [git](http://www.git-scm.com/).
It can be downloaded with the following command:

    $ git clone git://git.xcsoar.org/xcsoar/mirror/Skylines.git

For more information, please refer to the [git documentation](http://git-scm.com/documentation).

# Installation and Setup

*SkyLines* is based on the [TurboGears2](http://www.turbogears.org) web framework. For further instructions visit its website. If you don't have it installed yet, install it:

    $ easy_install -i http://tg.gy/current tg.devtools

Install the helper applications from the XCSoar project:

    $ git clone git://git.xcsoar.org/xcsoar/master/xcsoar.git
    $ cd xcsoar
    $ make TARGET=UNIX output/UNIX/bin/AnalyseFlight output/UNIX/bin/FlightPath
    $ cd /opt/
    $ sudo ln -s <path to xcsoar>/output/UNIX skylines

Install the required libraries to run *SkyLines* using the setup.py script:

    $ cd <path to skylines>
    $ python setup.py develop

*(You might have to install the additional debian packages `libxml2-dev`, `libxslt1-dev` and `python-dev` for the `lxml` dependency)*

Install postgres and postgis. On Debian Linux (testing) this is done by:

    $ apt-get install postgresql postgresql-9.1-postgis postgresql-contrib-9.1

Now create a new database and user for *SkyLines*. On Debian Linux, change to the user postgres to log into the database. Second, install postgis into this new created database:

    $ su - postgres
    $ createuser <your username> # you don't need to grant any special privileges now
    $ createdb skylines -O <your username> # create skylines database with owner skylines
    $ psql skylines -c "CREATE EXTENSION postgis"
    $ psql skylines -c "CREATE EXTENSION fuzzystrmatch"
    $ psql skylines -c "GRANT ALL ON geometry_columns TO <your username>"
    $ psql skylines -c "GRANT SELECT ON spatial_ref_sys TO <your username>"

Note: the procedure of installing PostGIS may be different for other versions of postgresql, postgis and other
operating systems. See the approciate documentation and websites for more information.

Adjust the sqlalchemy.url configuration in the development.ini.

Create the project database for any model classes defined:

    $ paster setup-app development.ini

Fill the airport database:

    $ python import_welt2000.py development.ini

If you want to run the mapserver as fastcgi, install python-mapscript package (on Debian). To run it locally as
as subprocess of mapproxy, change assets/mapproxy/mapproxy.yaml to fit it to your needs. You'll need to install
cgi-mapserver package for this.

    $ apt-get install python-mapscript

To import airspaces into the database, install python-gdal package (using gdal extension directly from pypi is not recommended) and import the required airspace files:

    $ python import_airspaces.py development.ini assets/airspace/airspace_list.txt assets/airspace/airspace_blacklist.txt

Start the paste http server:

    $ paster serve development.ini

While developing you may want the server to reload after changes in package files (or its dependencies) are saved. This can be achieved easily by adding the --reload option:

    $ paster serve --reload development.ini

Then you are ready to go.

# Contributing

Submit patches to the XCSoar developer mailing list
(<xcsoar-devel@lists.sourceforge.net>).

- patches should be self-contained
- patches should be self-documenting (add a good description on what
  is changed, and why you are changing it)
- write one patch for one change

# License

    SkyLines - the free internet platform for sharing flights
    Copyright (C) 2012  The XCSoar project

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

# Authors

 * Tobias Bieniek (<tobias.bieniek@gmx.de>)
 * Max Kellermann (<max@duempel.org>)
 * Tobias Lohner (<tobias@lohner-net.de>)
 * Andrey Lebedev (<andrey@lebedev.lt>)
 * Matthew Scutter (<yellowplantain@gmail.com>)
 * Fabian Berstecher (<F.Berstecher@gmx.de>)
