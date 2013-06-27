from fabric.api import *
from fabric.contrib.console import confirm

# enter the host names to run remotely
# it can be more than one host
# use ssh style. i.e solomon@ninja
env.hosts = ['yourhost.com']

# project related settings
project_name = 'inanlar'
remote_code_dir = '/path/tp/remote/dir'
git_clone = 'yourname@yourhost.com:repo.git'
virtual_env_name = 'venv'

# gunicorn details
remote_gunicorn_pid = '/tmp/gunicorn.pid'

################################################
# Local commands                               #
################################################


def test():
    with settings(warn_only=True):
        result = local('python manage.py test', capture=True)
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


################################################
# Remote commands                              #
################################################


def clone():
    with settings(warn_only=True):
        # Check if the codes are cloned
        if run("test -d %s" % remote_code_dir).failed:
            run("git clone %s %s" % (git_clone, remote_code_dir))


################################################
# Apache commands                              #
################################################


def restart_apache():
    """
    restarts the remote apache server
    """
    # Restart apache
    sudo('/etc/init.d/apache2 restart')


def deploy_apache():
    """
    deploys the project to the remote server
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

    # Restart apache
    restart_apache()


################################################
# Gunicorn commands                            #
################################################


def restart_gunicorn():
    """
    restarts the gunicorn server
    """
    # I started the server before 'python manage.py run_gunicorn domainname.com:8000 -p /tmp/inanlar.pid -D'
    # Restart server
    run('kill -HUP `cat %s`' % remote_gunicorn_pid)


def deploy_gunicorn():
    """
    deploys the project to the remote gunicorn server
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

    restart_gunicorn()


################################################
# Db Migration commands                        #
################################################


def migrate(app_name=None):
    """
    issues a migration using SAUTH db migration tool
    """

    if not app_name:
        abort("Please provide an app to migrate, i.e. fab migrate:app_name=django_myapp")

    with cd(remote_code_dir):
        # Check if there is virtualenv
        if run("test -d %s" % virtual_env_name).failed:
            run("virtualenv %s --distribute" % virtual_env_name)
        run('git pull')

        with prefix('source %s/bin/activate' % virtual_env_name):
            # Run django commands
            run('python %s/manage.py migrate %s' % (project_name, app_name))

    restart_apache()
