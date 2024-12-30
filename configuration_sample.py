"""
Some default configuration options with default values.
Copy this file to configuration.py and change the values as needed.
"""

# the small one
WIDTH, HEIGHT = 28, 13

# the medium one
#WIDTH, HEIGHT = 126, 16

flipdotdisplay = {
    #"serialdevice": "spy:///dev/ttyUSB0",  # use this for debugging
    "serialdevice": "/dev/ttyUSB0",
    "serialbaudrate": 115200,
    "i2c_address": 0x20,
    "modules": [18],
    "buffered": False
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
    "fps": 60,
    "implementation": "pygame" # or "pyxel"
}


mqtt_broker = 'localhost' # 'test.mosquitto.org'
mqtt_topic_display = 'fff_display'
mqtt_topic_info = 'fff_display_info'

# maximum time to allow for blocking the display
web_max_show_time_ms = 10000
