"""
TCP-Server for micropython that listens on a specified port for
TCP-Connections. Every request sent to the server has to be the string 'size'
or a string of 0s and 1s each specifying a dot to be turned on or off
respectively. For instance, to display the letter 'T' on a 4x3 display of this
form

    1111
    0110
    0110

the following request has to be sent to the server: 111101100110.

A simple command client like nc can send this request to 'server' listening
on port 8123:

   $ echo 111101100110 | nc server 8123

There is a cooldown time for requests that update the display. Many Requests
in a short time will therefore be ignored.

If the request contains the string 'SIZE' (ignoring case), the server
will respond with the dimensions of the display (width x height).

The unix port of micropython can be used to test this class . It can be found
in the github repo of micropython https://github.com/micropython/micropython
"""

# http://docs.micropython.org/en/latest/esp8266/library/usocket.html
import usocket
import utime
import uflipdotdisplay as flipdotdisplay


class DisplayServer:
    def __init__(self, display, display_cooldown_time=1):
        self.width = display.width
        self.height = display.height
        self.display = display
        self.last_display_update = utime.time()
        self.display_cooldown_time = display_cooldown_time

    def start(self, host, port):
        print("Starting server for dimension", self.width, "x", self.height)
        sock = usocket.socket()
        print("Listening on", host, "at port", port)
        addr = usocket.getaddrinfo(host, port)[0][-1]
        sock.bind(addr)
        sock.listen(10)

        while True:
            # waiting for connection
            remote_sock, cl = sock.accept()
            print("connection made", remote_sock)
            buf = remote_sock.recv(self.width * self.height)
            print("received", len(buf), "bytes", buf[:20])

            try:
                ans = self.handle_request(buf, remote_sock)
                remote_sock.send(bytes(ans, "ascii"))
            except Exception as e:
                print("ERROR", e)
            finally:
                remote_sock.close()

    def handle_request(self, payload, remote_sock):
        s = str(payload, "ascii")

        # answer with display dimension if desired
        if "size" in s.lower():
            return self._handle_dimension_request(remote_sock)

        # draw pixels if enough bytes have been sent
        elif len(payload) >= self.width * self.height:
            return self._handle_display_update_request(payload, remote_sock)

        else:
            return "unknown request type"

    def _handle_dimension_request(self, remote_sock):
        resp = "SIZE " + str(self.width) + "x" + str(self.height)
        return resp

    def _handle_display_update_request(self, payload, remote_sock):
        since_last_update = utime.time() - self.last_display_update
        if since_last_update < self.display_cooldown_time:
            return "Cooling down. Too many requests."
        else:
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
            self.last_display_update = utime.time()
            return "OK"


def main():
    display = flipdotdisplay.FlipDotDisplay()
    ds = DisplayServer(display,
                       display_cooldown_time=0.0001)
    ds.start("0.0.0.0", 8123)


if __name__ == "__main__":
    main()
