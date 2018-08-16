"""
This service script starts the display server. It is run by a systemd
startup script.
"""

import net
import flipdotdisplay

# Wait so many seconds between display updates
COOLDOWN_TIME = 0.5

# dimension of the display
WIDTH, HEIGHT = 28, 13

# list of GPIO-pins connected to the modules
MODULES = [14]


def main():
    fdd = flipdotdisplay.FlipDotDisplay(
        width=WIDTH, height=HEIGHT, module=MODULES)
    displayserver = net.DisplayServer(fdd, COOLDOWN_TIME)
    displayserver.start()


if __name__ == "__main__":
    main()
