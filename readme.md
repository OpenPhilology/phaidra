Phaidra
===

WIP -- do not use this installation document yet.

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
		$ cd env
		$ source bin/activate

Now, in front of your command prompt, you should see `(env)`, which indicates that you are operating within that environment.

Install Requirements
---
Presuming you are starting with a new machine, you need to install Python-related tools.

		$ sudo pip install -r requirements.txt


Install and configure Nginx with Uwsgi
---
Phaedra runs on nginx as its web server.

		$ sudo apt-get install nginx uwsgi uwsgi-plugin-python

Make sure you are running the latest version of Uwsgi (at time of writing, 1.9) with `uwsgi --version`. If this gives you an older version, you will need to upgrade by doing the following:

		$ pip install -U uwsgi
		$ cd /usr/bin
		$ mv uwsgi uwsgi-old
		$ ln -s /usr/local/bin/uwsgi uwsgi

Open `/opt/phaidra/extras/nginx/phaidra.conf` and set the variables to be appropriate for your server:

		server_name YOUR_SERVER.com www.YOUR_SERVER.com

Next we must create a symlink so Nginx uses our configuration file:

		$ ln -s /etc/nginx/sites-enabled/phaidra.conf /opt/phaedra/extras/nginx/phaidra.conf

And do the same to enable Uwsgi:

		$ ln -s /etc/uwsgi/apps-enabled/phaidra.ini /opt/phaedra/extras/uwsgi/phaidra.ini

Edit the main nginx.conf to import our conf file. For example:

		http {
			# ...
			include /opt/phaidra/extras/nginx/phaidra.conf;
			# ...
		}

Start up both services:

		$ sudo service nginx start
		$ sudo service uwsgi start


