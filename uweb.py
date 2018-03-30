# uweb.py
"""
Webserver for micropython. It will listen on a specified port for
TCP-Connections. Every request sent to the server has to be a string of 0s
and 1s each specifying a dot to be turned on or off respectively. For instance,
to make a T on a 4x3 display of this form

    1111
    0110
    0110

the following request has to be sent to the server: 111101100110.

A simple command client like nc can send this request to 'server' listening
on port 8123:

$ echo 111101100110 | nc server 8123

If the request just contains the string 'SIZE', the server will respond with the
dimensions of the display (width x height).

To test this class the unix port of micropython can be used. It can be found
in the github repo of micropython
https://github.com/micropython/micropython
"""

# http://docs.micropython.org/en/latest/esp8266/library/usocket.html
import usocket
import flipflapflop


# TODO only send to display every X seconds
class DisplayServer:
    def __init__(self, width, height, display):
        self.width = width
        self.height = height
        self.display = display

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
                self.handle_request(buf, remote_sock)
            except Exception as e:
                print("ERROR", e)
            finally:
                remote_sock.close()

    def handle_request(self, payload, remote_sock):
        s = str(payload, "ascii")

        # answer with display dimension if desired
        if "size" in s.lower():
            resp = str(self.width) + "x" + str(self.height)
            remote_sock.send(bytes(resp, "ascii"))

        # draw pixels if enough bytes have been sent
        elif len(payload) >= self.width * self.height:
            for y in range(self.height):
                for x in range(self.width):
                    val = chr(payload[y * self.width+ x])
                    if val in ("0", "1"):
                        print(val, end="")
                        self.display.px(x, y, val == "1")
                print()

            self.display.show()


if __name__ == "__main__":
    ds = DisplayServer(4, 3, flipflapflop.FlipDisplay())
    ds.start("0.0.0.0", 8123)
