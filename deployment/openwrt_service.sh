#!/bin/sh /etc/rc.common

# Running service script for OpenWRT
# https://openwrt.org/docs/guide-developer/procd-init-script-example

# must be copied to /etc/init.d/flipflapflop
# and enabled with /etc/init.d/flipflapflop enable

START=99
USE_PROCD=1

start_service() {
    procd_open_instance
    procd_set_param command /bin/sh -c 'cd /root/flipflapflop && /usr/bin/python -u displayserver_service.py'
    procd_set_param stdout 1
    procd_set_param stderr 1
    #  respawn threshold timeout retry
    procd_set_param respawn 3600 5 5
    procd_close_instance
}
