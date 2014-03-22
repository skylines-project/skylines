## Complete Installation instructions for Ubuntu Server 12.04.4 LTS

The following test describes how to perform all the install steps mentioned in INSTALL.md on a newly installed Ubuntu Server 12.04.4 LTS distribution. This process was last tested on 20. March 2014.


    # change to the postgres user
    $ sudo su - postgres

    # Bring newly installed system up to date
    $ sudo apt-get update
    $ sudo apt-get upgrade

    # Include package archive of Porstgres
    $ sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" >> /etc/apt/sources.list'
    $ wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | sudo apt-key add -

    # Update local package repo
    $ sudo apt-get update

    # Install all required software
    $ sudo apt-get install libpq-dev Postgresql-9.3-postgis pgadmin3 postgresql-contrib python-pip git libcurl4-openssl-dev nedit python-dev g++ python-virtualenv make redis-server openjdk-7-jre

    # Clone GIT-Server
    $ cd 
    $ git clone git://github.com/skylines-project/skylines

    # Setup virtual python environment for skylines
    $ cd
    $ virtualenv ~/skylines-virtualenv
    
    # Activate virtual environment for skylines
    $ source ~/skylines-virtualenv/bin/activate

    # Change user to postgres
    $ sudo su - postgres

    # create a database user account for yourself
    $ createuser -s <your username>

    # create skylines database with yourself as the owner
    $ createdb skylines -O <your username>

    # install PostGIS extensions into the PostgreSQL database
    $ psql -d skylines -c 'CREATE EXTENSION postgis;'

    # install fuzzystrmatch extension into the database
    $ psql -d skylines -c 'CREATE EXTENSION fuzzystrmatch;'

    # Create database
    $ ./manage.py db create

    # Run python-pip to install all required software in virtual environment
    $ cd skylines
    $ pip install -e .

    # Add airports to database - this may take a while
    $ ./manage.py import welt2000 --commit

    # Run skylines server
    $ ./manage.py runserver

