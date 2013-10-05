# Installing SkyLines

*SkyLines* has quite many dependencies and is not always easy to install for
new developers. Please don't hesitate to
[ask for help](README.md#contact-and-contributing) if you hit any roadblocks.

The production server is running the Debian Linux operating system and most of
our developers use Ubuntu or Debian too. We recommend to use either one of
those systems for development, but it may also be possible to make it work on
OS X or Windows.

There is also a currently unmaintained [Vagrant](http://www.vagrantup.com/) /
[Chef](http://www.opscode.com/chef/) environment for *SkyLines*. This makes it
possible to run a virtual machine with Ubuntu dedicated to *SkyLines*
development on OS X or Windows. This may or may not work currently and for now
we don't recommend using it. More information can be found in
[INSTALL.vagrant.md](INSTALL.vagrant.md).


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
    $ psql -d skylines -f /usr/share/postgresql/9.1/contrib/postgis-2.0/legacy_minimal.sql

    # install fuzzystrmatch extension into the database
    $ psql -d skylines -c 'CREATE EXTENSION fuzzystrmatch;'

*Note: The location of the legacy_minimal.sql file may be different for other
versions of PostgreSQL, PostGIS and other operating systems. See the
appropriate documentation and websites for more information.*

After creating the database you have to create the necessary tables and indices
by calling the `./scripts/initialise_database.py` file from the the command
line.


## XCSoar tools

Since the [XCSoar](http://www.xcsoar.org/) project already has much of the code
implemented that is necessary for flight analysis, it makes sense to reuse that
code where applicable. *SkyLines* is using two tools from the range of XCSoar
libraries called `AnalyseFlight` and `FlightPath`. These tools are installed
and build by the `xcsoar` python package, which also includes wrappers for both
tools. To build the tools you might have to install additional libraries like
`libcurl`, which can be installed on Debian/Ubuntu by executing `apt-get
install libcurl4-openssl-dev`. Please have a look into the XCSoar documentation
if you need more help with the building process.


## Running the debug server

If the above steps are completed you should be able to run a base version of
*SkyLines* locally now:

    $ ./debug.py

*(The following chapters are optional!)*


## Adding Airports

Since an empty database is boring, you should at least load the airports from
the [Welt2000](http://www.segelflug.de/vereine/welt2000/) into the database by
calling:

    $ ./scripts/import_welt2000.py


## Asynchronous tasks

*SkyLines* can use [Celery](http://www.celeryproject.org) with
[Redis](http://www.redis.io) as broker for asynchronous tasks like in-depth
analysis of flights. Celery is one of *SkyLines* requirements and will be
installed by pip, but you need to get Redis on your own. On Debian, all you
need is to install the `redis-server` package:

    $ apt-get install redis-server

To run the Celery worker, call

    $ ./celery_worker.py
