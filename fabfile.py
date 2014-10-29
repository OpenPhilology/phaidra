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
    sudo('service neo4j-service stop && service neo4j-service start')
    sudo('service nginx stop && service nginx start')
    sudo('killall uwsgi && uwsgi %s/extras/phaidra.ini' % env.directory)

def setup_postgres():
    sudo("apt-get build-deb python-psycopg2")
    sudo("apt-get install postgresql postgresql-contrib")
    password = prompt('Set the password for postgres (default: "phaidra"): ')
    sudo("psql postgres -U postgres -c %s" % password, user="postgres")
    sudo("createdb phaidra", user="postgres")

def setup_frontend():
    sudo("add-apt-repository ppa:chris-lea/node.js")
    sudo("apt-get update")
    sudo("apt-get install nodejs")
    sudo("npm install")
    local("bower install")

def setup_django():
    with virtualenv():
        local("./manage.py collectstatic") 

def setup_server():
    sudo("apt-get install nginx uwsgi uwsgi-plugin-python python2.7-dev")
    version = local("uwsgi --version")

    if Decimal(version) < 1.9:
        sudo("pip install -U uwsgi")
        with cd('/user/bin'):
            sudo('mv uwsgi uwsgi-old')
            sudo('ln -s /usr/local/bin/uwsgi uwsgi')

    sudo("ln -s %s/extras/nginx/phaidra.conf /etc/nginx/sites-enabled/phaidra.conf" % env.directory)
    sudo("ln -s %s/extras/uwsgi/phaidra.ini /etc/uwsgi/apps-enabled/phaidra.ini" % env.directory)
    sudo("mkdir /var/uwsgi")
    sudo("chown www-data:www-data /var/uwsgi")
    sudo("mkdir %s/logs && touch %s/logs/master.pid && mkdir /var/log/uwsgi && touch /var/log/uwsgi/phaidra_daemon.log" % env.directory)

def setup_neo4j():
    version = local('java -version')

    if Decimal(version) < 1.7:
        sudo('add-apt-repository ppa:webupd8team/java')
        sudo('apt-get update')
        sudo('apt-get install oracle-java7-installer')
        sudo('update-java-alternatives -s java-7-oracle')

    sudo('wget -O - http://debian.neo4j.org/neotechnology.gpg.key | apt-key add -')
    sudo("echo 'deb http://debian.neo4j.org/repo stable/' > /etc/apt/sources.list.d/neo4j.list")
    sudo('apt-get update && apt-get install neo4j && service neo4j start')

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
