#!/bin/sh
#
# setup script for picore (UNTESTED)
# http://tinycorelinux.net/9.x/armv6/releases/RPi/
#
# After installing picore, the device is reachable under tc@box with
# the default password "piCore". Follow the instructions in the README
# of picore to repartition the sdcard.
#

INSTALL_DIR=/opt/flipflapflop
TCE_PACKAGES="firmware-rpi3-wireless wifi avahi python3.4 python3.4-dev git compiletc libffi-dev"
PIP_PACKAGES="RPi.GPIO smbus-cffi spidev"
# Wifi Settings
SSID="testssid"
PASSWORD="wlanpass"

# extra package index for pip
EXTRA_PIP_INDEX=https://www.piwheels.org/simple

# Backup files
BACKUP_DIR="$(mktemp -d setup-picore-XXXXXX)"
echo "Making Backups in $BACKUP_DIR"

# setup system and installing packages
tce-load -wi $TCE_PACKAGES || exit 1
# enable pip
python3.4 -m ensurepip
pip3.4 install --extra-index-url=$EXTRA_PIP_INDEX --user $PIP_PACKAGES || exit 1

# add entry to wifi.db
cp -v /home/tc/wifi.db $BACKUP_DIR
echo -e "$SSID\t$PASSWORD\tWPA" >> /home/tc/wifi.db

# setup bootlocal.sh
cp -v /opt/bootlocal.sh $BACKUP_DIR
cat <<EOF >> /opt/bootlocal.sh
# setup hostname
/usr/bin/sethostname picore

# start the wifi and connect to the first entry in wifi.db
/usr/local/bin/wifi.sh -a &

# start the avahi daemon
/usr/local/etc/init.d/avahi start
EOF

# cloning repo
rm -rf $INSTALL_DIR
mkdir -p $INSTALL_DIR
git -C $INSTALL_DIR clone https://github.com/tbs1-bo/flipflapflop.git || exit 1

# adding system start entry
cp -v /home/tc/.profile $BACKUP_DIR
echo "sudo python3.4 $INSTALL_DIR/flipflapflop.py" >> /home/tc/.profile

# making changes persistant
filetool.sh -b
