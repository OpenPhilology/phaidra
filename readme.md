Phaidra
===
Phaidra is that system that powers the Historical Language eLearning Project. It will provide distributed eLearning for historical languages such as Greek and Latin, so that more people can delve deeply into primary sources in their original language.

Installing Phaidra
===
Before you begin installing, we make the assumption that:

* You are running Ubuntu 12.04 or later.
* You are installing into `/opt/phaidra`
* You have already installed git
* You have already [generated and added ssh keys to your account](https://help.github.com/articles/generating-ssh-keys/).

Push directly to OpenPhilology/Phaidra
---
*Only for authorized contributors*

```
cd /opt
git clone git@github.com:OpenPhilology/phaidra.git
```

Or use our https clone url.
This will create a directory at `/opt/phaidra`. 

Fork from Github
---
On this page, click "Fork" in the upper right-hand corner.

Clone the project to your local machine.

```
cd /opt
git clone https://github.com/YOUR_USERNAME/phaidra.git
git remote add upstream https://github.com/YOUR_USERNAME/phaidra.git
git fetch upstream
```

This will create a directory at `/opt/phaidra`. 

Build the project
---

```
sudo apt-get update
sudo apt-get install fabric
fab install
```

License
===
Phaidra and Ancient Geek, by the Open Philology Project, is licensed under the Creative Commons Attribution-ShareAlike 4.0 International license:
https://creativecommons.org/licenses/by-sa/4.0/

