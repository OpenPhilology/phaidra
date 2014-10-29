from fabric.api import *
from contextlib import contextmanager

env.directory = '/opt/phaidra'
env.activate = '. /opt/phaidra/env/bin/activate'

@contextmanager
def virtualenv():
    with cd(env.directory):
        with prefix(env.activate):
            yield

def prepare_locale(lang):
    with virtualenv():
        local("django-admin.py makemessages --locale=%s --extension=html --ignore=env --ignore=*.py" % lang)
        local("django-admin.py makemessages -d djangojs --locale=%s --ignore=env --ignore=static/admin/* --ignore=static/js/components --ignore=static/collected/*" % lang)

def compile_locale(lang):
    with virtualenv():
        local("django-admin.py compilemessages --locale=%s" % lang)

def propagate_db():
    with virtualenv():
        local("./manage.py dumpdata --natural --indent=4 --exclude=contenttypes --exclude=auth --exclude=tastypie > app/fixtures/db.json")

def load_db():
    with virtualenv():
        local('./manage.py migrate')
        local("./manage.py loaddata app/fixtures/db.json")

def restart():
    local('service neo4j-service stop && service neo4j-service start')
    local('service nginx stop && service nginx start')
    local('killall uwsgi && uwsgi %s/extras/phaidra.ini' % env.directory)

def setup_postgres():
    local("sudo apt-get build-dep python-psycopg2")
    local("sudo apt-get install postgresql-9.1 postgresql-contrib")
    local('sudo service postgres start')

    # TODO: If user sets alternate password, update their settings.py
    password = prompt('Set the password for postgres (default: "phaidra"): ')

    with settings(user='postgres'):
        # Look in the right place for postgres and related tools
        # local('export PATH=$PATH:/usr/lib/postgresql/9.1/bin/')
        # local('pg_ctl -w start ')
        local('psql -U postgres -c "ALTER USER postgres WITH ENCRYPTED PASSWORD \'%s\'"' % password)
        local('sudo -u postgres createdb phaidra')

def setup_frontend():
    local("add-apt-repository ppa:chris-lea/node.js")
    local("apt-get update")
    local("apt-get install nodejs")
    local("npm install")
    local("bower install")

def setup_django():
    with virtualenv():
        local("./manage.py collectstatic") 

def setup_server():
    local("apt-get install nginx uwsgi uwsgi-plugin-python python2.7-dev")
    version = local("uwsgi --version")

    if Decimal(version) < 1.9:
        local("pip install -U uwsgi")
        with cd('/usr/bin'):
            local('mv uwsgi uwsgi-old')
            local('ln -s /usr/local/bin/uwsgi uwsgi')

    local("ln -s %s/extras/nginx/phaidra.conf /etc/nginx/sites-enabled/phaidra.conf" % env.directory)
    local("ln -s %s/extras/uwsgi/phaidra.ini /etc/uwsgi/apps-enabled/phaidra.ini" % env.directory)
    local("mkdir /var/uwsgi")
    local("chown www-data:www-data /var/uwsgi")
    local("mkdir %s/logs && touch %s/logs/master.pid && mkdir /var/log/uwsgi && touch /var/log/uwsgi/phaidra_daemon.log" % env.directory)

def setup_neo4j():
    version = local('java -version')

    if Decimal(version) < 1.7:
        local('add-apt-repository ppa:webupd8team/java')
        local('apt-get update')
        local('apt-get install oracle-java7-installer')
        local('update-java-alternatives -s java-7-oracle')

    local('wget -O - http://debian.neo4j.org/neotechnology.gpg.key | apt-key add -')
    local("echo 'deb http://debian.neo4j.org/repo stable/' > /etc/apt/sources.list.d/neo4j.list")
    local('apt-get update && apt-get install neo4j && service neo4j start')

def install():
    code_dir = '/opt/phaidra'
    with cd(code_dir):
        setup_postgres()
        setup_frontend()
        setup_django()
        setup_server()
        load_db()
        setup_neo4j()
        restart()
