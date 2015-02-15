from fabric.api import task, env, run, sudo, prefix, cd
from fabric.contrib.files import append
import cuisine
import fabtools
from fabtools import require


@task
def provision():
    print('Provision')

    if env.user != 'vagrant':
        print('This task must be run as vagrant:')
        print('ex.: fab vagrant provision')
    else:
        _setup_users()
        _install_build_essential()
        _install_virtualenv_wrapper()
        _mkvirtualenv('skylines')
        _install_skylines_python_requirements()
        _install_postgres()
        _install_mapserver()


def _setup_users():
    if not fabtools.user.exists('skylines'):
        fabtools.user.create('skylines', password='skylines')

    if not cuisine.file_exists('/etc/sudoers.d/vagrant'):
        vagrant_sudo = 'vagrant ALL=(ALL) NOPASSWD:ALL'
        cuisine.file_write('/etc/sudoers.d/vagrant', vagrant_sudo,
                           owner='root', group='root', sudo=True)


def _install_build_essential():
    require.deb.packages([
        'autoconf',
        'binutils-doc',
        'bison',
        'build-essential',
        'flex',
        'gettext',
        'ncurses-dev',
        'libpq-dev',
        'g++',
        'git',
        'python',
        'python-pip',
        'python-dev',
        'libcurl4-openssl-dev',
        'redis-server'
    ])


def _install_virtualenv_wrapper():
    if not fabtools.python.is_installed('virtualenvwrapper'):
        fabtools.python.install('virtualenvwrapper', use_sudo=True)
        workon_home = 'export WORKON_HOME=$HOME/.virtualenvs'
        virtualenvwrapper = 'source /usr/local/bin/virtualenvwrapper.sh'
        append('/home/vagrant/.bashrc', workon_home)
        append('/home/vagrant/.bashrc', virtualenvwrapper)


def _mkvirtualenv(name):
    with prefix('export WORKON_HOME=$HOME/.virtualenvs'):
        with prefix('source /usr/local/bin/virtualenvwrapper.sh'):
            run("mkvirtualenv %s" % name)

    postactivate = '/home/vagrant/.virtualenvs/skylines/bin/postactivate'
    if not cuisine.file_exists(postactivate):
        cuisine.file_write(postactivate, '#!/bin/bash\n\n')
    append(postactivate, "cd /vagrant")


def _install_skylines_python_requirements():
    with cd('/vagrant'):
        with prefix('export WORKON_HOME=$HOME/.virtualenvs'):
            with prefix('source /usr/local/bin/virtualenvwrapper.sh'):
                with prefix("workon skylines"):
                    run("pip install -e .")


def _install_postgres():
    require.deb.packages([
        'postgresql-9.3-postgis-2.1',
        'postgresql-contrib',
    ])

    require.postgres.user('vagrant', 'vagrant', superuser=True, createdb=True,
                          createrole=True, inherit=True, login=True)
    require.postgres.database('vagrant', 'vagrant')

    require.postgres.user('skylines', 'skylines')
    require.postgres.database('skylines', 'skylines')
    require.postgres.database('skylines_test', 'skylines')

    print('create extensions skylines')
    sudo("psql -d skylines -c 'CREATE EXTENSION IF NOT EXISTS postgis;'", user='postgres')
    sudo('psql -d skylines -c "CREATE EXTENSION IF NOT EXISTS postgis_topology;"', user='postgres')
    sudo("psql -d skylines -c 'CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;'", user='postgres')

    print('create extensions skylines_test')
    sudo("psql -d skylines_test -c 'CREATE EXTENSION IF NOT EXISTS postgis;'", user='postgres')
    sudo('psql -d skylines_test -c "CREATE EXTENSION IF NOT EXISTS postgis_topology;"', user='postgres')
    sudo("psql -d skylines_test -c 'CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;'", user='postgres')

    print('setup postgres variables')
    append('/home/vagrant/.bashrc', 'export POSTGIS_GDAL_ENABLED_DRIVERS=GTiff')
    append('/home/vagrant/.bashrc', 'export POSTGIS_ENABLE_OUTDB_RASTERS=1')


def _install_mapserver():
    require.deb.packages([
        'python-mapscript',
        'cgi-mapserver',
        'python-gdal'
    ])
