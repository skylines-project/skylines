from fabric.api import env, task, local, cd, lcd, run, sudo, put

from tempfile import NamedTemporaryFile

env.use_ssh_config = True
env.hosts = ["skylines@skylines.aero"]

APP_DIR = "/home/skylines"
SRC_DIR = "%s/src" % APP_DIR


@task
def deploy(branch="master", force=False):
    push(branch, force)
    restart()


@task
def deploy_ember():
    with lcd("ember"):
        local("node_modules/.bin/ember deploy production -v")


@task
def push(branch="HEAD", force=False):
    cmd = "git push %s:%s %s:master" % (env.host_string, SRC_DIR, branch)
    if force:
        cmd += " --force"

    local(cmd)


@task
def restart():
    with cd(SRC_DIR):
        run("git reset --hard")

        run("pipenv install")

        # do database migrations
        manage("migrate upgrade")

        # restart services
        restart_service("caddy")
        reload_service("skylines")
        reload_service("mapproxy")
        restart_service("tracking")
        restart_service("celery")


@task
def restart_service(service):
    run("systemctl --user restart %s" % service)


@task
def reload_service(service):
    run("systemctl --user reload %s" % service)


@task
def manage(cmd, user=None):
    with cd(SRC_DIR):
        if user:
            sudo("pipenv run ./manage.py %s" % cmd, user=user)
        else:
            run("pipenv run ./manage.py %s" % cmd)


@task
def clean_mapproxy_cache():
    with cd(SRC_DIR):
        run("rm -rv mapproxy/cache_data/")
