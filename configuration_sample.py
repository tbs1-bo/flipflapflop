"""
Some default configuration options with default valies.
Copy this file to configuration.py and change the values as needed.
"""

WIDTH = 28
HEIGHT = 13

flipdotdisplay = {
    "serialdevice": "/dev/ttyUSB0",
    "i2c_address": 0x20,
    "modules": [18]
}

display_server = {
    "host": "0.0.0.0",
    "port": 10101
}

remote_display = {
    "host": "localhost",
    "port": 10101
}

simulator = {
    "fps": 30
}
