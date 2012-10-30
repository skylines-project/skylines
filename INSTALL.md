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
    $ createdb skylines --o <your username> # create skylines database with owner skylines
    $ createlang plpgsql -d skylines
    $ psql -d skylines -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql
    $ psql -d skylines -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql
    $ psql skylines # log into postgres using skylines database
    postgres=# grant all on geometry_columns to <your username>;
    postgres=# grant select on spatial_ref_sys to <your username>;
    postgres=# create extension fuzzystrmatch;
    postgres=# \q

Note: the location of the postgis sql files may be different for other versions of postgresql, postgis and other
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
