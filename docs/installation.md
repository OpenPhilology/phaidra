**Note** Make sure you have already followed Github's instructions on how to [generate and add ssh keys to your account](https://help.github.com/articles/generating-ssh-keys/).

***

# Installing Phaidra

These instructions have been tested on Ubuntu 12.04, but will likely work on newer versions of Ubuntu as well. You may need to make adjustments to the installation if you prefer to run on another operating system.

First things first, clone the repo.

**If you're an authorized contributor**
```
cd /opt
git clone git@github.com:OpenPhilology/phaidra.git
```

**If you want to simply fork the repo**
```
cd /opt
git clone https://github.com/YOUR_USERNAME/phaidra.git
git remote add upstream https://github.com/YOUR_USERNAME/phaidra.git
git fetch upstream
```

**Build the project**

```
sudo apt-get update
sudo apt-get install fabric
fab install
```

***

Troubleshooting
---

## Postgres

If, while you're installing, you encounter problems with postgres, such as:
```
locale: Cannot set LC_MESSAGES to default locale: No such file or directory
locale: Cannot set LC_ALL to default locale: No such file or directory
```

Try copying the environment file we've provided in `/extras/etc/`.

```
sudo cp /opt/phaidra/extras/etc/environment /etc/environment
sudo reboot
```

This has to do with the virtual machine you're on being incorrectly configured. See related [Stackoverflow post](http://stackoverflow.com/questions/17399622/postgresql-9-2-installation-on-ubuntu-12-04).

***

## Bad Gateway

This generally indicates that uwsgi is not actually running. You can debug uwsgi by stopping the process, uncommenting the daemon line in its config file, and launching it again.

```
killall uwsgi
vim extras/uwsgi/phaidra.ini
fab debug_uwsgi
```

Try loading a page. You should see an error come up in the terminal. Fix the errors you see, and re-run `fab restart`. Once things are working normally, you can simply `git checkout extras/uwsgi/phaidra.ini` to discard your changes, and once again, run `fab restart`. 
