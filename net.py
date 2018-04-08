"""
TCP-Server for micropython that listens on a specified port for
TCP-Connections. Every request sent to the server has to be one of the special
commands described later on or a string of 0s and 1s each specifying a dot to
be turned on or off respectively. For instance, to display the letter 'T'
on a 4x3 display of this form

    1111
    0110
    0110

the following request has to be sent to the server: 111101100110.

A simple command line client like nc can send this request to 'server' listening
on port 8123:

   $ echo 111101100110 | nc server 8123

There is a cooldown time for requests that update the display. Many Requests
in a short time will therefore be ignored. If the request contains the
string 'COOLDOWN' (ignoring case), the server will respond with the cooldown
time of the display - i.e. the time to wait between screen updates.

If the request contains the string 'SIZE' (ignoring case), the server
will respond with the dimensions of the display (width x height).

"""

import socket
import time


class DisplayServer:
    def __init__(self, display, display_cooldown_time=1.0):
        self.width = display.width
        self.height = display.height
        self.display = display
        self.last_display_update = time.time()
        self.display_cooldown_time = display_cooldown_time

    def start(self, host="0.0.0.0", port=8123):
        print("Starting server for dimension", self.width, "x", self.height,
              "on", host, "at port", port)
        addr = (host, port)
        with socket.socket() as sock:
            sock.bind(addr)
            print("Listening on", host, "at port", port)
            sock.listen(10)

            while True:
                # waiting for connection
                remote_sock, cl = sock.accept()
                buf = remote_sock.recv(self.width * self.height)
                print("received", len(buf), "bytes")

                try:
                    ans = self.handle_request(buf)
                    remote_sock.send(bytes(ans, "ascii"))
                except Exception as e:
                    print("ERROR", e)

    def handle_request(self, payload):
        s = str(payload, "ascii")

        # answer with display dimension if desired
        if s.lower().startswith("size"):
            return "SIZE {w}x{h}".format(w=self.width, h=self.height)
        elif s.lower().startswith("cooldown"):
            return "cooldown time: " + str(self.display_cooldown_time)

        # draw pixels if enough bytes have been sent
        elif len(payload) >= self.width * self.height:
            return self._handle_display_update_request(payload)

        else:
            return "unknown request type"

    def _handle_display_update_request(self, payload):
        since_last_update = time.time() - self.last_display_update
        if since_last_update < self.display_cooldown_time:
            return "Cooling down. Too many requests."

        for y in range(self.height):
            for x in range(self.width):
                val = chr(payload[y * self.width + x])
                if val in ("0", "1"):
                    print(val, end="")
                    self.display.px(x, y, val == "1")
                else:
                    return "bad payload:" + val
            print()

        self.display.show2()
        self.last_display_update = time.time()
        return "OK"


class DummyDisplay:
    def __init__(self):
        self.width = 4
        self.height = 3
    def px(self, x,y,val):
        pass
    def show(self):
        pass
    def show2(self):
        pass


def main():
    import flipdotdisplay
    display = flipdotdisplay.FlipDotDisplay()
    # display = DummyDisplay()
    ds = DisplayServer(display,
                       display_cooldown_time=0.0001)
    ds.start("0.0.0.0", 8123)


if __name__ == "__main__":
    main()
