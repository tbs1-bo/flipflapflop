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

"""

# http://docs.micropython.org/en/latest/esp8266/library/usocket.html
import usocket

# TODO import flipflapflop

HOST = "0.0.0.0"
PORT = 8123
WIDTH = 4   # display.width
HEIGHT = 3  # display.height


class DisplayServer:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def start(self, host, port):
        print("Starting server for dimension", self.width, "x", self.height)
        sock = usocket.socket()
        print("Listening on", host, "at port", port)
        addr = usocket.getaddrinfo(host, port)[0][-1]
        sock.bind(addr)
        sock.listen(10)

        while True:
            # waiting for connection
            s, cl = sock.accept()
            print("connection made", s)
            buf = s.recv(self.width*self.height)
            print("received", len(buf), "bytes")
            s.close()

            try:
                self.handle_request(buf)
            except Exception as e:
                print("ERROR", e)
                del buf
            del buf

    def handle_request(self, bytes_):
        if len(bytes_) != self.width * self.height:
            print("Error: Wrong dimension of request")
            return

        print("Visualizing")
        for i, b in enumerate(bytes_):
            if i % self.width == 0:
                print()

            print("1" if b == ord("1") else "0", end="")

        print()

        # TODO flipflapflop.show(bytes)


if __name__ == "__main__":
    ds = DisplayServer(28, 16)
    ds.start(HOST, PORT)
