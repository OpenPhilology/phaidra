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

Install the basics, then build the project.

```
sudo apt-get update
sudo apt-get install python-software-properties python python-virtualenv
cd /opt/phaidra
virtualenv --no-site-packages env
source env/bin/activate
pip install -r requirements.txt
fab install
```
