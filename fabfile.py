from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import comment, uncomment
from contextlib import contextmanager
import os

git_repo = 'git@github.com:OpenPhilology/phaidra.git'
env.directory = os.path.dirname(os.path.abspath(__file__))
env.activate = '. %s/env/bin/activate' % env.directory
env.hosts = ['localhost']

@contextmanager
def virtualenv():
    with lcd(env.directory):
        with prefix(env.activate):
            yield

###############################
# Frontend Utility tasks      #
###############################
@task
def prepare_locale(lang):
    """
    Gathers translation strings based on provided locale.
    """
    with virtualenv():
        local("django-admin.py makemessages --locale=%s --extension=html --ignore=env --ignore=*.py" % lang)
        local("django-admin.py makemessages -d djangojs --locale=%s --ignore=env --ignore=static/admin/* --ignore=static/js/components --ignore=static/collected/*" % lang)

@task
def compile_locale(lang):
    """
    Compiles translations strings into .mo files
    """
    with virtualenv():
        local("django-admin.py compilemessages --locale=%s" % lang)

@task
def propagate_db():
    """
    Creates a dump of the postgres database
    """
    with virtualenv():
        local("./manage.py dumpdata --natural --indent=4 --exclude=contenttypes --exclude=auth --exclude=tastypie > app/fixtures/db.json")

@task
def load_db():
    """
    Migrates the database, then loads db.json
    """
    with virtualenv():
        local('./manage.py migrate')
        local("./manage.py loaddata app/fixtures/db.json")

@task
def load_greek():
    """
    Load greek
    """
    with virtualenv():
        local('python %s/common/utils/neo4j_import/pentecontaetia_import.py' % env.directory)

@task
def load_alignments():
    """
    Load alignment data.
    """
    with virtualenv():
        local('python %s/common/utils/neo4j_import/pentecontaetia_import.py' % env.directory)

###############################
# Backend Utility tasks       #
###############################
def restart_uwsgi():
    """
    Restarts uwsgi.
    """
    with virtualenv(), settings(warn_only=True):
        local('killall uwsgi') 
        local('uwsgi %s/extras/uwsgi/phaidra.ini' % env.directory)

@task
def debug_uwsgi():
    """
    Task for un-daemonizing uwsgi, for debugging purposes
    """
    with virtualenv():
        with settings(warn_only=True):
            local('killall uwsgi') 
        comment('%s/extras/uwsgi/phaidra.ini' % env.directory,
            r'^daemonize'
        )
        restart_uwsgi()

@task
def restart(full=False):
    """
    Reboots neo4j, nginx, and uwsgi.
    """
    with virtualenv():
        # Only restart neo4j if needed
        if full: 
            local('service neo4j-service stop && service neo4j-service start')

        local('service nginx stop && service nginx start')
        uncomment('%s/extras/uwsgi/phaidra.ini' % env.directory,
            r'daemonize'
        )
        restart_uwsgi()

###############################
# Installation tasks          #
###############################
@task
def init():
    """
    Most fundamental steps to initialize Phaidra install.
    """

    local('apt-get install python-software-properties python python-virtualenv python-dev libpq-dev')
    with lcd(env.directory):
        local('virtualenv --no-site-packages env')

    with virtualenv():
        local('pip install -r requirements.txt')
    
@task
def setup_postgres():
    """
    Installs postgres and creates database for Django.
    """
    local("sudo apt-get build-dep python-psycopg2")
    local("sudo apt-get install postgresql-9.1 postgresql-contrib")

    with settings(warn_only=True):
        result = local('sudo -u postgres createdb phaidra', capture=True)
    if result.failed:
        if result.return_code == 1:
            if confirm("WARNING: Database 'phaidra' already exists. Delete database contents?"):
               local('sudo -u postgres dropdb phaidra') 
               local('sudo -u postgres createdb phaidra')
            else:
                abort("You must delete the existing database named 'phaidra'.")
        else:
            abort("Failed for unknown reason. Investigate postgres.")

    password = prompt('Enter a new database password for user `postgres`:')
    local('sudo -u postgres psql template1 -c "ALTER USER postgres with encrypted password \'%s\';"' % password)

@task
def setup_frontend():
    """
    Installs frontend requirements.
    """
    local("add-apt-repository ppa:chris-lea/node.js")
    local("apt-get update")
    local("apt-get install nodejs")
    local("npm install")
    local("npm install bower -g")
    local("bower install --allow-root")

@task
def setup_django():
    """
    Sets up django, prompts to create super user. 
    """
    with virtualenv():
        local("./manage.py collectstatic") 
        local('./manage.py migrate')
        load_db()
        local('./manage.py createsuperuser')

@task
def setup_server():
    """
    Installs and configures Nginx and Uwsgi
    """
    local("apt-get install nginx uwsgi uwsgi-plugin-python python2.7-dev")
    local("pip install -U uwsgi")
    with lcd('/usr/bin'):
        local('mv uwsgi uwsgi-old')
        local('ln -s /usr/local/bin/uwsgi uwsgi')

    # Symlink our config files if the links don't exist already
    nginx_conf = "%s/extras/nginx/phaidra.conf" % env.directory
    uwsgi_conf = "%s/extras/uwsgi/phaidra.ini" % env.directory

    if not os.path.isfile(nginx_conf):
        local('ln -s %s /etc/nginx/sites-enabled/phaidra.conf' % nginx_conf)
    if not os.path.isfile(uwsgi_conf):
        local('ln -s %s /etc/uwsgi/apps-enabled/phaidra.ini' % uwsgi_conf)

    # Create a safe place for the uwsgi socket to exist
    if not os.path.exists('/var/uwsgi'):
        local("mkdir /var/uwsgi")

    # Make user www-data (nginx's user) can access our socket
    local("chown www-data:www-data /var/uwsgi")

    # Create directories and folders needed by uwsgi/nginx
    directories = [
        '%s/logs' % env.directory,
        '/var/log/uwsgi'
    ]
    files = [
        '%s/logs/master.pid' % env.directory,
        '/var/log/uwsgi/phaidra_daemon.log'
    ]

    for d in directories:
        if not os.path.exists(d):
            local('mkdir %s' % d)

    for f in files:
        if not os.path.isfile(f):
            local('touch %s' % f)

@task
def setup_neo4j():
    """
    Adds and installs java and neo4j repositories
    """
    # Install Java
    local('add-apt-repository ppa:webupd8team/java')
    local('apt-get update')
    local('apt-get install oracle-java7-installer')
    local('update-java-alternatives -s java-7-oracle')

    # Install neo4j
    local('wget -O - http://debian.neo4j.org/neotechnology.gpg.key | apt-key add -')
    local("echo 'deb http://debian.neo4j.org/repo stable/' > /etc/apt/sources.list.d/neo4j.list")
    local('apt-get update && apt-get install neo4j && service neo4j-service start')

@task
def install():
    """
    Our beautiful install task for Phaidra.
    """
    code_dir = '/opt/phaidra'
    with cd(code_dir):
        init()
        setup_postgres()
        setup_frontend()
        setup_django()
        setup_server()
        setup_neo4j()
        restart()
