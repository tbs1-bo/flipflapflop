"""
The flipdotdisplay package allows for controlling a physical flipdotdisplay. 
It relies on a portexpander that is connected to the display via I²C or SPI
on one hand and to a RaspberryPi on the other hand.
"""

try:
    import RPi.GPIO as GPIO
    import MCP23017
except ImportError as ex:
    print("Some modules cannot be imported", ex)
import time
import displayprovider


class FlipDotDisplay(displayprovider.DisplayBase):
    def __init__(self, address = 0x20, width=28, height=13, module = [18]):
        """Create a display connected via a port expander on the given 
        I²C-address."""
        super().__init__(width, height)
        GPIO.setmode(GPIO.BCM)
        for m in module:
            GPIO.setup(m, GPIO.OUT)
        self.pulsewidth = 0.0001
        self.module = module
        self.ioexp = MCP23017.Portexpander(address, 1)
        self.ioexp.config_inout('A', 0b00000000)
        self.ioexp.config_inout('B', 0b11100000)
        self.ioexp.write_value('A', 0x00)
        self.ioexp.write_value('B', 0x00)
        self.buffer = []
        self.oldbuffer = []
        for x in range(width):
            col = [False]*height
            oldcol = [True]*height
            self.buffer.append(col)
            self.oldbuffer.append(oldcol)

    def px(self, x, y, val):
        """
        Write a pixel at (x|y) into the buffer.
        """
        assert 0 <= x < self.width
        assert 0 <= y < self.height
        self.buffer[x][y] = val

    def flipdot(self, x, y, val):
        """Immediately flip the dot at (x|y) to the given value."""
        mod = x // 28                   # module number
        col = x % 28                    # column of current module
        a = (y//7<<3) + y%7 + 1         # address of row (y) -> bank A of I/O-Expander
        b = (col//7<<3) + col%7 + 1     # address of column  -> bank B of I/O-Expander
        if(val):
            a = a + 0b10000000
            self.ioexp.write_value('A', a)
            self.ioexp.write_value('B', b)
        else:
            a = a + 0b01100000
            self.ioexp.write_value('A', a)
            self.ioexp.write_value('B', b)
        GPIO.output(self.module[mod], GPIO.HIGH)    # create a short pulse to enable module
        time.sleep(self.pulsewidth)
        self.ioexp.write_value('A', 0x00)
        GPIO.output(self.module[mod], GPIO.LOW)

    def printbuffer(self):
        """
        Print the buffer onto the terminal.
        """ 
        for y in range(self.height):
            print("")
            for x in range(self.width):
                if self.buffer[x][y]:
                    print("O", end="")
                else:
                    print(".", end="")

    def show(self, fullbuffer = False):
        """
        Show the current buffer on the flip dot display.
        Set the fullbuffer-flag to show the whole buffer on the display and 
        not only the changes.
        """
        #self.printbuffer()
        for x in range(self.width):
            for y in range(self.height):
                if (self.buffer[x][y] != self.oldbuffer[x][y] or fullbuffer):
                    self.flipdot(x, y, self.buffer[x][y])
                    self.oldbuffer[x][y] = self.buffer[x][y]

    def show2(self):
        """
        Maybe a bit faster than show(True)
        """
        for x in range(self.width):
            mod = x // 28
            col = x % 28
            b = (col//7<<3) + col%7 + 1
            self.ioexp.write_value('B', b)
            for y in range(self.height):
                a = (y//7<<3) + y%7 + 1
                if self.buffer[x][y]:
                    a = a + 0b10000000
                else:
                    a = a + 0b01100000
                self.ioexp.write_value('A', a)
                GPIO.output(self.module[mod], GPIO.HIGH)
                time.sleep(self.pulsewidth)
                #self.ioexp.write_value('A', 0x00)
                GPIO.output(self.module[mod], GPIO.LOW)

