# Installing Phaidra

The easiest way to install Phaidra is simply to run it in a Docker container. First, I will explain how to do this. At the end of the page, there are also instructions for installing all of the Phaidra dependencies by hand.

## Using Phaidra within Docker

### Installing Docker

These instructions will assume that you are running Ubuntu. Phaidra was originally built on Ubuntu 12.04, so you are going to want that or something newer.

```
sudo sh -c "curl https://get.docker.io/gpg | apt-key add -"
sudo sh -c "echo deb http://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list"
sudo apt-get update
sudo apt-get install lxc-docker
```

Since we use Ubuntu 12.04, which comes with a 3.2 kernel, and Docker works best on a 3.8 kernel, we need to upgrade. If you are using a different version of Ubuntu, these steps may not be necessary. See (https://docs.docker.com/installation/ubuntulinux/#ubuntu-precise-1204-lts-64-bit)[Docker Documentation] about this.

```
# install the backported kernel
$ sudo apt-get update
$ sudo apt-get install linux-image-generic-lts-raring linux-headers-generic-lts-raring

# install the backported kernel and xorg if using Unity/Xorg
$ sudo apt-get install --install-recommends linux-generic-lts-raring xserver-xorg-lts-raring libgl1-mesa-glx-lts-raring

# reboot
$ sudo reboot
```
