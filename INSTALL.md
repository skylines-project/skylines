# Installing SkyLines

*SkyLines* has quite many dependencies and is not always easy to install for new developers. Please don't hesitate to
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

## Manual Install

*(These instructions are written for Debian/Ubuntu systems.)*

First of all make sure you have [Python](http://www.python.org/) installed! After that install the required Python packages to run *SkyLines* using the setup.py script:

    $ pip install -e .

*(You might have to install the additional debian packages `libxml2-dev`, `libxslt1-dev` and `python-dev` for the `lxml` dependency)*

Install the [PostgreSQL](http://www.postgresql.org/) database server and the [PostGIS](http://postgis.net/) spatial extension. This is done by:

    $ apt-get install postgresql postgresql-9.1-postgis postgresql-contrib-9.1

Now create a new database and user for *SkyLines*. Change to the user `postgres` to log into the database. Second, install PostGIS into this new created database:

    # change to the postgres user
    $ su - postgres

    # create a database user account for yourself
    $ createuser <your username>

    # create skylines database with yourself as the owner
    $ createdb skylines --o <your username>

    # install PostGIS extensions into the database
    $ createlang plpgsql -d skylines
    $ psql -d skylines -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql
    $ psql -d skylines -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql

    # log into postgres using skylines database
    $ psql skylines
    postgres=# grant all on geometry_columns to <your username>;
    postgres=# grant select on spatial_ref_sys to <your username>;
    postgres=# create extension fuzzystrmatch;
    postgres=# \q

*(Note: the location of the postgis sql files may be different for other versions of PostgreSQL, PostGIS and other operating systems. See the approciate documentation and websites for more information.)*


# Database

In the last chapter you have setup the database server and the `skylines` database. Unless you have access and want to sync your development setup with the production server you will need to create the tables in the database now:

    $ paster setup-app development.ini

If you have set up your environment with Vagrant, you must ssh into the virtual machine and run the previous command from within the ```/vagrant``` directory.
Alternatively, you can run:

    vagrant ssh --command "paster setup-app /vagrant/development.ini"

# XCSoar dependencies

Since the [XCSoar project](http://www.xcsoar.org/) already has much of the code implemented that is necessary for flight analysis, it makes sense to reuse that code where applicable. *SkyLines* is using two tools from the range of XCSoar libraries called `AnalyseFlight` and `FlightPath`. The names speak for themselves

## Download

We have uploaded precompiled versions of the two tools to our download server to make the initial setup faster and easier. The tools can be downloaded by calling:

    ./download_xcsoar_tools.sh

## Compiling

If the download does not work, or you want to build the tools yourself, you can follow these instructions:

    # download the XCSoar source code repository
    $ git clone git://git.xcsoar.org/xcsoar/master/xcsoar.git

    # consult the XCSoar README file for further dependency informations

    # the following should be enough for the Vagrant environment
    $ apt-get install libcurl4-openssl-dev libboost-system-dev

    # build the tools
    $ cd xcsoar
    $ make TARGET=UNIX DEBUG=n ENABLE_SDL=n output/UNIX/bin/AnalyseFlight output/UNIX/bin/FlightPath

    # create a symbolic link from skylines to xcsoar (not possible on Vagrant)
    $ cd <path to skylines>
    $ ln -s <path to xcsoar>/output/UNIX/bin bin


# Running the Server

You should now be able to start the server and run your development instance of *SkyLines* (If you have set up your environment with Vagrant, remember to ssh into the virtual machine and run the commands from the ```/vagrant```directory):

    $ paster serve development.ini

While developing you may want the server to reload after changes in package files (or its dependencies) are saved. This can be achieved easily by adding the --reload option:

    $ paster serve --reload development.ini

You are ready to go. Have fun developing!

*(The following chapters are optional!)*


# Adding Airports

Since an empty database is boring, you should at least load the airports from the [Welt2000](http://www.segelflug.de/vereine/welt2000/) into the database by calling:

    $ python import_welt2000.py development.ini


# Running a local mapserver

If you want to run the mapserver as fastcgi, install the `python-mapscript` package (on Debian):

    $ apt-get install python-mapscript

To run it locally as subprocess of mapproxy, change `mapserver/mapproxy/mapproxy.yaml` to fit it to your needs. You'll need to install the `cgi-mapserver` package for this.

To import airspaces into the database, install the `python-gdal` package (using gdal extension directly from pypi is not recommended) and import the required airspace files:

    $ python import_airspaces.py development.ini assets/airspace/airspace_list.txt assets/airspace/airspace_blacklist.txt
