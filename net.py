

import socket
import displayprovider


DEFAULT_PORT = 10101


class DisplayServer:
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
    def __init__(self, display):
        self.width = display.width
        self.height = display.height
        self.display = display
        self.on_request = lambda: None
        self.server_running = False

    def start(self, host="0.0.0.0", port=DEFAULT_PORT):
        print("Starting display server for dimension", self.width, "x", self.height,
              "on", host, "at port", port)
        addr = (host, port)
        self.server_running = True
        with socket.socket() as sock:
            sock.bind(addr)
            print("Listening on", host, "at port", port)
            sock.listen(10)

            while self.server_running:
                # waiting for connection
                remote_sock, _cl = sock.accept()
                buf = remote_sock.recv(self.width * self.height)
                self.on_request()
                #print("received", len(buf), "bytes")

                try:
                    ans = self.handle_request(buf)
                    remote_sock.send(bytes(ans, "ascii"))
                    remote_sock.close()
                except Exception as e:
                    print("ERROR", e)

    def handle_request(self, payload):
        s = str(payload, "ascii")

        # answer with display dimension if desired
        if s.lower().startswith("size"):
            return "SIZE {w}x{h}".format(w=self.width, h=self.height)

        # draw pixels
        else:
            return self._handle_display_update_request(payload)

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
    "Remote class to connect with a running DisplayServer instance."

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
    
    def led(self, on_off):
        pass
        # TODO led support for remote display


class PixelflutServer(displayprovider.DisplayBase):
    """
    PixeflutServer that conforms to the Pixelflut protocol outlined at
    https://c3pixelflut.de/how.html

    PX <x> <y> <rrggbb|aarrggbb> # set pixel at x,y with color rrggbb
    PX <x> <y>                   # get pixel color info for pixel at x,y
    SIZE                         # get size of the display
    OFFSET <x> <y>               # set offset for following commands
    """
    def __init__(self, display):
        self.width = display.width
        self.height = display.height
        self.display = display
        self.offset_x = 0
        self.offset_y = 0
        self.server_running = False

    def start(self, host="0.0.0.0", port=DEFAULT_PORT):
        print("Starting Pixelflut server for dimension", self.width, "x", self.height,
              "on", host, "at port", port)

        addr = (host, port)
        self.server_running = True
        with socket.socket() as sock:
            sock.bind(addr)
            print("Listening on", host, "at port", port)
            sock.listen(10)

            while self.server_running:
                remote_sock, _ = sock.accept()
                with remote_sock:
                    while True:
                        buf = remote_sock.recv(1024)
                        if not buf:
                            break
                        try:
                            ans = self.handle_request(buf)
                            if ans:
                                remote_sock.send(bytes(ans, "ascii"))
                        except Exception as e:
                            print("ERROR", e)

    def handle_request(self, payload):
        """
        Handle incoming requests and execute commands based on the payload.
        The payload is expected to be a string of ASCII-encoded commands 
        separated by newlines.
        Each command is processed and appropriate actions are taken.
        Commands:
        - PX x y color: Set the pixel at (x, y) to the specified color.
        - PX x y: Get the color of the pixel at (x, y).
        - SIZE: Get the dimensions of the grid.
        - OFFSET x y: Set the offset for the grid coordinates.
        Args:
            payload (bytes): The ASCII-encoded command string.
        Returns:
            str: The responses to the commands, joined by newlines.
        """

        commands = str(payload, "ascii").strip().split('\n')
        responses = []

        for command in commands:
            parts = command.strip().split()
            if not parts:
                continue

            cmd = parts[0].upper()
            if cmd == "PX":
                if len(parts) == 4: # PX x y color
                    x = int(parts[1]) + self.offset_x
                    y = int(parts[2]) + self.offset_y
                    color = parts[3]
                    self.set_pixel(x, y, color)
                elif len(parts) == 3: # PX x y
                    x = int(parts[1]) + self.offset_x
                    y = int(parts[2]) + self.offset_y
                    responses.append(self.get_pixel(x, y))
            elif cmd == "SIZE":
                responses.append(f"{self.width} {self.height}")
            elif cmd == "OFFSET": # OFFSET x y
                if len(parts) == 3:
                    self.offset_x = int(parts[1])
                    self.offset_y = int(parts[2])

        return "\n".join(responses)

    def set_pixel(self, x, y, color):
        """
        Set the color of a specific pixel on the display.
        Parameters:
        x (int): The x-coordinate of the pixel.
        y (int): The y-coordinate of the pixel.
        color (str): The color to set the pixel to, represented as a hex string. 
                 If the color is "000000", the pixel will be turned off. 
                 Otherwise it will be turned on.
        """

        if 0 <= x < self.width and 0 <= y < self.height:
            self.display.px(x, y, color != "000000")
            self.display.show()

    def get_pixel(self, x, y):
        """
        Get the color of a specific pixel on the display. Will return the color
        of the pixel at the specified coordinates as a hex string.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return "FFFFFF" if self.display.buffer[y][x] else "000000"
        return "000000"

def test_networking():
    import flipdotsim
    import threading
    import time

    TEST_PORT = 1212

    fdd = flipdotsim.FlipDotSim(width=15, height=15)
    ds = DisplayServer(fdd)
    th = threading.Thread(target=ds.start,
                          kwargs={'host':'127.0.0.1', 'port':TEST_PORT})
    th.daemon = True
    th.start()
    time.sleep(0.2)  # wait for server to start
    
    remote_display = RemoteDisplay(host="127.0.0.1", port=TEST_PORT, width=15, height=15)
    remote_display.px(1, 1, True)
    remote_display.px(2, 1, True)
    remote_display.show()
    time.sleep(0.5)

    import demos
    demo = demos.RotatingPlasmaDemo(remote_display)
    demo.fps = 30  # reduce fps for networking
    demo.run(2)
    
    ds.server_running = False
    th.join(2)
    fdd.close()
    #exit()

def test_networking_pixelflut():
    import flipdotsim
    import threading
    import time

    TEST_PORT = 1234

    fdd = flipdotsim.FlipDotSim(width=15, height=15)
    ps = PixelflutServer(fdd)
    th = threading.Thread(target=ps.start,
                          kwargs={'host':'127.0.0.1', 'port':TEST_PORT})
    th.daemon = True
    th.start()
    time.sleep(0.2)  # wait for server to start
    
    remote_display = RemoteDisplay(host="127.0.0.1", port=TEST_PORT, width=15, height=15)
    remote_display.px(1, 1, True)
    remote_display.px(2, 1, True)
    remote_display.show()
    time.sleep(0.5)

    import demos
    demo = demos.RotatingPlasmaDemo(remote_display)
    demo.fps = 30  # reduce fps for networking
    demo.run(2)
    
    ps.server_running = False
    th.join(2)
    fdd.close()




def main():
    import displayprovider
    import configuration

    disp = displayprovider.get_display(
        width=configuration.WIDTH, height=configuration.HEIGHT,
        fallback=displayprovider.Fallback.SIMULATOR)
    #ds = DisplayServer(disp)
    #ds.start(host=configuration.display_server["host"],
    #    port=configuration.display_server["port"])

    server = PixelflutServer(disp)
    server.start(host=configuration.display_server["host"],
                 port=configuration.display_server["port"])

if __name__ == "__main__":
    main()