## Running a local mapserver

If you want to run the map server locally you will need to install the
`mapserver` CLI. On Debian you can do:

    $ apt-get install mapserver-cli

To import airspaces into the database, you'll need to install the [GDal](http://www.gdal.org/) library
(already included in the provisioning of the Vagrant box).
Install the dependencies of gdal:

    $ sudo apt-get install g++ libgdal1-dev

Get the installed gdal version:

    $ gdal-config --version
    1.10.1

Install the python module pygdal in the corresponding version:

    $ pipenv install pygdal==1.10.1


Finally you can import the required airspace files:

    $ ./manage.py import airspace airspace/airspace_list.txt airspace/airspace_blacklist.txt
