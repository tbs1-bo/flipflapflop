#!/bin/sh
#
# Install script for OpenWRT - e.g. running on an Orange Pi Zero.
#

echo "Installing packages"
opkg update
opkg install python3-light python3-pyserial git nano

echo "Cloning the repository with a depth of 1"
git clone --depth 1 https://github.com/tbs1-bo/flipflapflop

# Alternative: Download the repository as a zip file
#wget -v https://github.com/tbs1-bo/flipflapflop/archive/refs/heads/master.zip
#unzip master.zip
#mv -v flipflapflop-master flipflapflop
#rm -v master.zip

echo "copy default configuration"
cp -v flipflapflop/configuration_sample.py flipflapflop/configuration.py
