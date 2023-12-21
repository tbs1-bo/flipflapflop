"""
This service script starts the display server. It is run by a systemd
startup script. The server shows a clock display until a request is
detected. In this case the server handle the request and updates the
display accorading to the content of the request. If there is are
no further request, the clock will be shown again.
"""

import net
import flipdotdisplay
import binclock
import threading

# dimension of the display
WIDTH, HEIGHT = 28, 13

# list of GPIO-pins connected to the modules
MODULES = [14]

# time to wait for request before clock should be turned on again
REQUEST_TIMEOUT = 5  # seconds


def on_request():
    """Turn of the clock on a request and wait for some time."""
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
    fdd = flipdotdisplay.FlipDotDisplay(
        width=WIDTH, height=HEIGHT, module=MODULES)
    displayserver = net.DisplayServer(fdd)
    displayserver.on_request = on_request

    global clock
    clock = binclock.BinClock(fdd)
    th = threading.Thread(target=clock.run)
    th.start()

    displayserver.start()


if __name__ == "__main__":
    main()
