## Running a local mapserver

If you want to run the mapserver as fastcgi, install the `python-mapscript`
package (on Debian):

    $ apt-get install python-mapscript

To run it locally as subprocess of mapproxy, change
`mapserver/mapproxy/mapproxy.yaml` to fit it to your needs. You'll need to
install the `cgi-mapserver` package for this.

To import airspaces into the database, you'll need to install the [GDal](http://www.gdal.org/) library.
Install the dependencies of gdal:

    $ sudo apt-get install g++ libgdal1-dev

Get the installed gdal version:

    $ gdal-config --version
    1.10.1

Install the python module pygdal in the corresponding version:

    $ pipenv install pygdal==1.10.1


Finally you can import the required airspace files:

    $ ./manage.py import airspace mapserver/airspace/airspace_list.txt mapserver/airspace/airspace_blacklist.txt
