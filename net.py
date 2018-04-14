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

Lets start a server. Here we use a thread in order to be able to run the client
afterwards. In practice the server will run on a different platform and can be
started directly.

    >>> import net
    >>> import displayprovider
    >>> import threading
    >>> ds = net.DisplayServer(displayprovider.DisplayBase())
    >>> th = threading.Thread(target=ds.start)
    >>> th.setDaemon(True)
    >>> th.start()
    Starting server for dimension 4 x 3 on 0.0.0.0 at port 10101

Now we can start a client and send some pixels to the server.

    >>> cl = net.RemoteDisplay(host="0.0.0.0")
    Remote display will send data to 0.0.0.0 on port 10101
    >>> cl.px(1, 1, True)
    >>> cl.px(2, 3, True)
    >>> cl.show()
    Listening on 0.0.0.0 at port 10101
    received 12 bytes

The output lines after show() come from the server.

"""

import socket
import time
import displayprovider


DEFAULT_PORT = 10101


class DisplayServer:
    def __init__(self, display, display_cooldown_time=1.0):
        self.width = display.width
        self.height = display.height
        self.display = display
        self.last_display_update = time.time()
        self.display_cooldown_time = display_cooldown_time

    def start(self, host="0.0.0.0", port=DEFAULT_PORT):
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

        self.display.show2()  # TODO must be changed to show() if this is stable
        self.last_display_update = time.time()
        return "OK"


class RemoteDisplay(displayprovider.DisplayBase):
    """Remote class to connect with a running display server."""
    def __init__(self, host="0.0.0.0", port=DEFAULT_PORT, width=28, height=13):
        super().__init__(width, height)
        print("Remote display will send data to", host, "on port", port)
        self.host = host
        self.port = port

        self.buffer = []
        for x in range(width):
            col = [False] * height
            self.buffer.append(col)

    def px(self, x, y, val):
        self.buffer[x][y] = val

    def show(self):
        with socket.socket() as sock:
            sock.connect((self.host, self.port))
            payload = self._buffer_to_payload()
            sock.sendall(payload)

    def _buffer_to_payload(self):
        payload = ""
        for y in range(self.height):
            for x in range(self.width):
                payload += "1" if self.buffer[x][y] else "0"

        return bytes(payload, "utf8")


def main():
    import displayprovider
    disp = displayprovider.get_display(fallback=displayprovider.Fallback.SIMULATOR)
    ds = DisplayServer(disp, display_cooldown_time=0.0001)
    ds.start()


if __name__ == "__main__":
    main()
