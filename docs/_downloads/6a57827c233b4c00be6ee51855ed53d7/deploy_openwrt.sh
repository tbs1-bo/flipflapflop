#!/bin/sh
#
# Install script for OpenWRT - e.g. running on an Orange Pi Zero.
#
# There is a firmware selector that allows to define included packages
# https://firmware-selector.openwrt.org/
#
# DHCP client mode could be setup there as well:
# uci set network.lan.proto="dhcp"
# uci commit network
#
# https://openwrt.org/docs/guide-user/network/openwrt_as_clientdevice#command-line_instructions

echo "Installing packages"
opkg update
opkg install python3-light python3-pyserial nano


# using download instead of git clone to save space

echo "Download files from GitHub"
FILES="fffserial.py binclock.py displayprovider.py net.py \
configuration_sample.py displayserver_service.py demos.py \
deployment/openwrt_service.sh"
BASE_URL="https://raw.githubusercontent.com/tbs1-bo/flipflapflop/refs/heads/master/"
mkdir -p flipflapflop/deployment
for f in $FILES; do wget $BASE_URL/$f -O flipflapflop/$f; done

echo "copy default configuration"
cp -v flipflapflop/configuration_sample.py flipflapflop/configuration.py

echo "copy service file and enable service"
cp -v flipflapflop/deployment/openwrt_service.sh /etc/init.d/flipflapflop
chmod +x /etc/init.d/flipflapflop
/etc/init.d/flipflapflop enable
