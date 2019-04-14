## Running a local mapserver

If you want to run the map server locally you will need to install the
`mapserver` CLI. On Debian you can do:

    $ apt-get install mapserver-cli

To import airspaces into the database, install the `python-gdal` package (using
gdal extension directly from pypi is not recommended) and import the required
airspace files:

    $ ./manage.py import airspace airspace/airspace_list.txt airspace/airspace_blacklist.txt
