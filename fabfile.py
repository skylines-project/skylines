from fabric.api import env, cd, run

env.use_ssh_config = True
env.hosts = ['root@skylines']


def restart():
    with cd('/opt/skylines/src'):
        run('git reset --hard')

        # compile i18n .mo files
        run('./manage.py babel compile')

        # generate JS/CSS assets
        run('./manage.py assets build')

        # do database migrations
        run('sudo -u skylines ./manage.py migrate upgrade')

        # restart services
        run('sv restart skylines-fastcgi')
        run('sv restart mapserver-fastcgi')
        run('sv restart skylines-daemon')
        run('sv restart celery-daemon')
