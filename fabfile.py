from fabric.api import env, run

env.use_ssh_config = True
env.hosts = ['root@skylines']


def restart():
    run('./restart.sh')
