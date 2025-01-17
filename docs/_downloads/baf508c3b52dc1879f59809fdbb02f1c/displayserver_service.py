"""
This service script starts the display server. It is run by a systemd
startup script. The server shows a clock display until a request is
detected. In this case the server will handle the request and updates the
display according to the content of the request. If there is are
no further request wihtin a specified time period, the clock will be shown again.
"""

import net
import time
import displayprovider
import binclock
import threading


# time to wait for request before clock should be turned on again
REQUEST_TIMEOUT = 5  # seconds

def on_request():
    """Turn off the clock on a request and wait for some time."""
    global clock, timer

    clock.visible = False
    timer.cancel()
    timer = threading.Timer(REQUEST_TIMEOUT, time_over)
    timer.start()


def time_over():
    """Time has exceeded without request. Turn the clock on again."""
    print("long time no request, restarting clock")
    clock.visible = True


clock = None
timer = threading.Timer(0, time_over)


def main():
    print("starting display service. Request timeout is", REQUEST_TIMEOUT, "seconds")
    fdd = None
    while fdd is None:
        try:
            fdd = displayprovider.get_display(fallback=None)          
        except Exception as e:
            print("Unable to create display:", e)
            time.sleep(5)
            

    print("starting display", fdd)
    displayserver = net.DisplayServer(fdd)
    displayserver.on_request = on_request

    global clock
    clock = binclock.BinClock(fdd)
    th = threading.Thread(target=clock.run)
    th.start()

    displayserver.start()


if __name__ == "__main__":
    main()
