from fabric.api import env, cd, run

env.use_ssh_config = True
env.hosts = ['root@skylines']


def restart():
    with cd('/opt/skylines/src'):
        run('git reset --hard')
        run('./restart.sh')
