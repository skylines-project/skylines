from fabric.api import env, task, local, cd, run, sudo

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
