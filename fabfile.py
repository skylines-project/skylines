from fabric.api import env, task, local, cd, run, sudo, put

from tempfile import NamedTemporaryFile

env.use_ssh_config = True
env.hosts = ['root@skylines']

WORKING_DIR = '/opt/skylines/src/'


@task
def deploy(branch='master', force=False):
    push(branch, force)
    restart()


@task
def push(branch='master', force=False):
    cmd = 'git push %s:%s %s:master' % (env.host_string, WORKING_DIR, branch)
    if force:
        cmd += ' --force'

    local(cmd)


@task
def restart():
    with cd(WORKING_DIR):
        run('git reset --hard')

        # compile i18n .mo files
        manage('babel compile')

        # generate JS/CSS assets
        manage('assets build')

        # do database migrations
        manage('migrate upgrade', user='skylines')

        # restart services
        restart_service('skylines-fastcgi')
        restart_service('mapserver-fastcgi')
        restart_service('skylines-daemon')
        restart_service('celery-daemon')


@task
def restart_service(service):
    run('sv restart ' + service)


@task
def manage(cmd, user=None):
    with cd(WORKING_DIR):
        if user:
            sudo('./manage.py %s' % cmd, user=user)
        else:
            run('./manage.py %s' % cmd)


@task
def update_mapproxy():
    with NamedTemporaryFile() as f:
        content = open('mapserver/mapproxy/mapproxy.yaml').read()

        content = content.replace(
            'base_dir: \'/tmp/cache_data\'',
            'base_dir: \'/opt/skylines/var/cache/mapproxy\'',
        )

        content = content.replace(
            'lock_dir: \'/tmp/cache_data/locks\'',
            'lock_dir: \'/opt/skylines/var/cache/mapproxy/locks\'',
        )

        f.write(content)
        f.flush()

        put(f.name, '/opt/skylines/etc/mapproxy.yaml')


@task
def clean_mapproxy_cache():
    with cd('/opt/skylines/var/cache/mapproxy'):
        run('rm -rv *')
