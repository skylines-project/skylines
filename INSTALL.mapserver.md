## Running a local mapserver

If you want to run the mapserver as fastcgi, install the `python-mapscript`
package (on Debian):

    $ apt-get install python-mapscript

To run it locally as subprocess of mapproxy, change
`mapserver/mapproxy/mapproxy.yaml` to fit it to your needs. You'll need to
install the `cgi-mapserver` package for this.

To import airspaces into the database, install the `python-gdal` package (using
gdal extension directly from pypi is not recommended) and import the required
airspace files:

    $ ./manage.py import-airspaces mapserver/airspace/airspace_list.txt mapserver/airspace/airspace_blacklist.txt
