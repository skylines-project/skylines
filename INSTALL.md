# Installing SkyLines

*SkyLines* has quite many dependencies and is not always easy to install for
new developers. Please don't hesitate to
[ask for help](README.md#contact-and-contributing) if you hit any roadblocks.

The production server is running the Debian Linux operating system and most of
our developers use Ubuntu or Debian too. We recommend to use either one of
those systems for development, but it may also be possible to make it work on
OS X or Windows.

There is also a [Vagrant](http://www.vagrantup.com/) environment for
*SkyLines*. This makes it possible to run a virtual machine with Ubuntu
dedicated to *SkyLines* development on OS X or Windows. More information
can be found in [INSTALL.vagrant.md](INSTALL.vagrant.md).


## Python, Flask and other dependencies

Since *SkyLines* is written and based on [Python](http://www.python.org/) you
should install it if you don't have it yet. *SkyLines* is currently targeting
the 2.7 branch of Python. You can check your version by running `python
--version` from the command line.

All the necessary Python libraries are installed using the `pip` tool. If you
don't have it yet please install it using e.g. `sudo apt-get install
python-pip` on Ubuntu/Debian. More information about pip can be found at
<http://www.pip-installer.org/>.

Now you can install the python dependencies by calling:

    $ sudo pip install -e .

*Note: You might have to install the additional Ubuntu/Debian packages
`libpq-dev`, `python-dev` and `g++` for the `psycopg2` dependency.*


## PostGIS database

The *SkyLines* backend is relying on the open source database
[PostgreSQL](http://www.postgresql.org/) and its
[PostGIS 2.x](http://www.postgis.net/) extension, that provides it with
geospatial functionality. The `fuzzystrmatch` extension is also needed which
is provided by the `postgresql-contrib` package on Debian/Ubuntu.

To install PostGIS you should follow the instructions at
<http://postgis.net/install> or
<http://trac.osgeo.org/postgis/wiki/UsersWikiInstall> (for Debian/Ubuntu).
Please note that you will need at least version 2.0 of PostGIS for *SkyLines*.

Once PostGIS is installed you should create a database user for yourself and
a database for *SkyLines* roughly like this:

    # change to the postgres user
    $ sudo su - postgres

    # create a database user account for yourself
    $ createuser -s <your username>

    # create skylines database with yourself as the owner
    $ createdb skylines -O <your username>

    # install PostGIS extensions into the PostgreSQL database
    $ psql -d skylines -c 'CREATE EXTENSION postgis;'

    # install fuzzystrmatch extension into the database
    $ psql -d skylines -c 'CREATE EXTENSION fuzzystrmatch;'

*Note: As of PostGIS 2.1.3, out-of-db rasters and all raster drivers are
disabled by default. In order to re-enable these, you need to set the
following environment variables: POSTGIS_GDAL_ENABLED_DRIVERS=GTiff and
POSTGIS_ENABLE_OUTDB_RASTERS=1 in the server environment. For more
information see the [PostGIS
manual](http://postgis.net/docs/postgis_installation.html#install_short_version)
and your distribution's documentation.*

After creating the database you have to create the necessary tables and indices
by calling `./manage.py db create` from the the command line.


## XCSoar tools

Since the [XCSoar](http://www.xcsoar.org/) project already has much of the code
implemented that is necessary for flight analysis, it makes sense to reuse that
code where applicable. *SkyLines* is using XCSoar as a python library. This library
is built and installed by the `xcsoar` python package. To build this library you
might have to install additional libraries like `libcurl`, which can be installed
on Debian/Ubuntu by executing `apt-get install libcurl4-openssl-dev`. Please have
a look into the XCSoar documentation if you need more help with the building process.


## Running the debug server

If the above steps are completed you should be able to run a base version of
*SkyLines* locally now:

    $ ./manage.py runserver

*(The following chapters are optional!)*


## Adding Airports

Since an empty database is boring, you should at least load the airports from
the [Welt2000](http://www.segelflug.de/vereine/welt2000/) into the database by
calling (the `commit` flag indicates that any data should be written to the
database):

    $ ./manage.py import welt2000 --commit


## Asynchronous tasks

*SkyLines* can use [Celery](http://www.celeryproject.org) with
[Redis](http://www.redis.io) as broker for asynchronous tasks like in-depth
analysis of flights. Celery is one of *SkyLines* requirements and will be
installed by pip, but you need to get Redis on your own. On Debian, all you
need is to install the `redis-server` package:

    $ apt-get install redis-server

To run the Celery worker, call

    $ ./manage.py celery runworker
