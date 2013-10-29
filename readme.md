Phaidra
===
Phaidra is that system that powers the Historical Language eLearning Project. It will provide distributed eLearning for historical languages such as Greek and Latin, so that more people can delve deeply into primary sources in their original language.

Installing Phaidra
===
These instructions will assume you are running Ubuntu 12.04, and that you are installing Phaidra in `/opt/phaidra`.

Push directly to OpenPhilology/Phaidra
---
*Only for authorized contributors*

		$ cd /opt
		$ git clone git@github.com:OpenPhilology/phaidra.git

This will create a directory at `/opt/phaidra`. 

Fork from Github
---
On this page, click "Fork" in the upper right-hand corner.

Clone the project to your local machine.

		$ cd /opt
		$ git clone https://github.com/YOUR_USERNAME/phaidra.git
		$ git remote add upstream https://github.com/YOUR_USERNAME/phaidra.git
		$ git fetch upstream

This will create a directory at `/opt/phaidra`. 

Set up Virtualenv
---

		$ sudo apt-get install python-virtualenv 
		$ cd /opt/phaidra
		# The name of our virtualenv is "env"
		$ virtualenv --no-site-packages env

Now, in front of your command prompt, you should see `(env)`, which indicates that you are operating within that environment.

Install Requirements
---
Presuming you are starting with a new machine, you need to install Python-related tools.

		$ source env/bin/activate
		$ sudo pip install -r requirements.txt
		$ deactivate

Install and configure Nginx with Uwsgi
---
Phaidra runs on nginx as its web server.

		$ sudo apt-get install nginx uwsgi uwsgi-plugin-python

Make sure you are running the latest version of Uwsgi (at time of writing, 1.9) with `uwsgi --version`. If this gives you an older version, you will need to upgrade by doing the following:

		$ pip install -U uwsgi
		$ cd /usr/bin
		$ mv uwsgi uwsgi-old
		$ ln -s /usr/local/bin/uwsgi uwsgi

Open `/opt/phaidra/extras/nginx/phaidra.conf` and set the variables to be appropriate for your server:

		# Can also just be an IP Address
		server_name YOUR_SERVER.com www.YOUR_SERVER.com 

Next we must create a symlink so Nginx uses our configuration file:

		$ ln -s /opt/phaidra/extras/nginx/phaidra.conf /etc/nginx/sites-enabled/phaidra.conf

And do the same to enable Uwsgi:

		$ ln -s /opt/phaidra/extras/uwsgi/phaidra.ini /etc/uwsgi/apps-enabled/phaidra.ini

Create a safe space for the socket to exist, which can be accessed by both Nginx and Uwsgi:

		$ sudo mkdir /var/uwsgi
		$ sudo chown www-data:www-data /var/uwsgi

Touch necessarily files so that Uwsgi can write to them.

		$ mkdir /opt/phaidra/logs
		$ touch /opt/phaidra/logs/master.pid

Start up services:

		$ sudo service nginx start
		$ sudo service uwsgi start

Install and configure the Neo4j database
---
Make sure you installed java 1.7. Do this outside your virtualenv.

		$ java -version

If not or less, install java as you prefer (e.g. http://www.cyberciti.biz/faq/howto-installing-oracle-java7-on-ubuntu-linux/) or follow:

		$ sudo add-apt-repository ppa:webupd8team/java
		$ sudo apt-get update
		$ sudo apt-get install oracle-java7-installer
		$ sudo update-java-alternatives -s java-7-oracle

Installing neo4j (http://www.neo4j.org/download):

		$ sudo -s
		$ wget -O - http://debian.neo4j.org/neotechnology.gpg.key | apt-key add - 
		$ echo 'deb http://debian.neo4j.org/repo stable/' > /etc/apt/sources.list.d/neo4j.list
		$ apt-get update
		$ apt-get install neo4j
		$ neo4j start
