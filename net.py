"""
TCP-Server that listens on a specified port for
TCP-Connections. Every request sent to the server has to be one of the special
commands described later on or a string of 0s and 1s each specifying a dot to
be turned on or off respectively. For instance, to display the letter 'T'
on a 4x3 display of this form

::

    1111
    0110
    0110


the following request must be sent to the server: 111101100110.

A simple command line client like nc can send this request to 'server'
listening on port 10101:

.. code-block:: bash

   $ echo 111101100110 | nc server 10101

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

The output lines after show() are coming from the server.

"""

import socket
import displayprovider


DEFAULT_PORT = 10101


class DisplayServer:
    def __init__(self, display):
        self.width = display.width
        self.height = display.height
        self.display = display
        self.on_request = lambda: None

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
                remote_sock, _cl = sock.accept()
                buf = remote_sock.recv(self.width * self.height)
                self.on_request()
                #print("received", len(buf), "bytes")

                try:
                    ans = self.handle_request(buf)
                    remote_sock.send(bytes(ans, "ascii"))
                except Exception as e:
                    print("ERROR", e)

    def handle_request(self, payload):
        s = str(payload, "ascii")

        import lt19fl
        if 'flag' in s.lower():
            return 'wie lautet das motto?'
        elif lt19fl.EXP in s.lower():
            return self.lt19()
            
        # answer with display dimension if desired
        if s.lower().startswith("size"):
            return "SIZE {w}x{h}".format(w=self.width, h=self.height)

        # draw pixels
        else:
            return self._handle_display_update_request(payload)

    def lt19(self):  # TODO remove later
        import lt19fl
        import flipdotfont
        import time

        txt = flipdotfont.TextScroller(
            self.display, 'flag discovered :)', flipdotfont.big_font())
        self.display.show()
        time.sleep(3)
        self.display.clear()
        self.display.show()
        return lt19fl.FL

    def _handle_display_update_request(self, payload):
        for y in range(self.height):
            for x in range(self.width):
                index = y * self.width + x
                if  index < len(payload):
                    val = chr(payload[index])
                else:
                    val = "0"

                if val in ("0", "1"):
                    self.display.px(x, y, val == "1")

        self.display.show()
        return "OK"


class RemoteDisplay(displayprovider.DisplayBase):
    """Remote class to connect with a running display server."""
    def __init__(self, host="0.0.0.0", port=DEFAULT_PORT, width=28, height=13):
        super().__init__(width, height)
        print("Remote display will send data to", host, "on port", port)
        self.host = host
        self.port = port

        self.buffer = []
        for _x in range(width):
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
    import configuration

    disp = displayprovider.get_display(
        width=configuration.WIDTH, height=configuration.HEIGHT,
        fallback=displayprovider.Fallback.SIMULATOR)
    ds = DisplayServer(disp)
    ds.start(host=configuration.display_server["host"],
        port=configuration.display_server["port"])


if __name__ == "__main__":
    main()
