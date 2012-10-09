# Gunicorn Deployment Fabric Script
# Author: suleyman@melikoglu.info
# 
# Use it to deploy your project to the remote server
# 
# Usage:
# fab prepare_deploy()
# fab deploy()

from fabric.api import *
from fabric.contrib.console import confirm

# enter the host names to run remotely
# it can be more than one host
# use ssh style. i.e solomon@myserver.com
env.hosts = ['solomon@myserver.com']

# project related settings
remote_code_dir = '/srv/project/myproject'
remote_gunicorn_pid = '/tmp/gunicorn.pid'
# git clone url, I haven't tested with projects on github
git_clone = 'solomon@localhost:/home/solomon/my_project.git'
virtual_env_name = 'venv'
apps_to_test = ('django_youtube', 'django_leaderboard')

def test():
    with settings(warn_only=True):
        result = local('python manage.py test %s' % " ".join(apps_to_test), capture=True)
    if result.failed and not confirm("Test failed, Continue anyway?"):
        abort("Aborting at user request.")

def commit():
    local("git add -p && git commit")

def push():
    local("git push")

def prepare_deploy():
    """tests, commits and pushes the project"""
    test()
    commit()
    push()

def clone():
    with settings(warn_only=True):
        # Check if the codes are cloned
        if run("test -d %s" % remote_code_dir).failed:
            run("git clone %s %s" % (git_clone, remote_code_dir))

def deploy():
    """
    deploys the project to the remote server
    restarts the gunicorn server
    """
    clone()

    with cd(remote_code_dir):
        # Check if there is virtualenv 
        if run("test -d %s" % virtual_env_name).failed:
            run("virtualenv %s --distribute" % virtual_env_name)
        run('git pull')

        with prefix('source %s/bin/activate' % virtual_env_name):
            # Install pip requirements
            run('pip install -r requirements.txt')

            # Run django commands
            #run('python manage.py syncdb')

            # I started the server before 'python manage.py run_gunicorn 46.19.36.179:8000 -p /tmp/gunicorn.pid -D'
            # Restart server
            run('kill -HUP `cat %s`' % remote_gunicorn_pid)

