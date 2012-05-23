# SkyLines

Welcome to *SkyLines*, the internet platform for sharing flights!

This project is in an early stage of development.

*SkyLines* is brought to you by the [XCSoar](http://www.xcsoar.org) project.
It is free software; the source code is available [here](http://git.xcsoar.org/cgit/mirror/Skylines.git/)

# Installation and Setup

*SkyLines* is based on the [TurboGears2](http://www.turbogears.org) web framework. For further instructions visit its website. If you don't have it installed yet, install it:

    $ easy_install -i http://tg.gy/current tg.devtools

Clone the *SkyLines* repository to your local drive:

    $ git clone git://git.xcsoar.org/xcsoar/mirror/Skylines.git
    $ cd Skylines

Install the required libraries to run *SkyLines* using the setup.py script:

    $ python setup.py develop

(You might have to install the additional debian packages `libxml2-dev`, `libxslt1-dev` and `python-dev` for the `lxml` dependency)

Create the project database for any model classes defined:

    $ paster setup-app development.ini

Start the paste http server:

    $ paster serve development.ini

While developing you may want the server to reload after changes in package files (or its dependencies) are saved. This can be achieved easily by adding the --reload option:

    $ paster serve --reload development.ini

Then you are ready to go.
