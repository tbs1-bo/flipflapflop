# ESP8266 startup file
#
# This file is executed on every boot (including wake-boot from deepsleep)

#import esp
#esp.osdebug(None)

import gc
import time
import network
import udisplayserver


#import webrepl
#webrepl.start()
gc.collect()

SSID = "flipdotdisplay"
PASSWORD = "micropythoN"
# Currently setting password does not work
# sticking to the default password micropythoN

print("waiting some safety seconds before starting")
time.sleep(3)

print("setup network SSID:", SSID, "Password:", PASSWORD)
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=SSID)  # , password=PASSWORD)

udisplayserver.main()
