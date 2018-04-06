#import RPi.GPIO as GPIO
import machine
import uMCP23017 as MCP23017
import time

"""
TODO Anpassen für den ESP8266
http://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/pins.html
http://docs.micropython.org/en/latest/esp8266/library/machine.Pin.html

Aufrufe auf RPi.GPIO müssen umgelenkt werden an die Äquivalente aus dem ESP.

Pin Deklaration:

    import machine
    pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
    
Pin auslesen oder setzen
    
    val = pin.value()    
    pin.value(1)
    
http://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/pwm.html

einen PWM-Pin deklarieren

    pin0 = machine.Pin(0)
    pwm0 = machine.PWM(pin0, freq=1000)
    pwm0.duty(512)  # zwischen 0 und 1023    
    # aus
    pwm0.deinit()


"""


class FlipDotDisplay:
    def __init__(self, address = 0x20, width=28, height=13, module=[14,12,13,15,5], sda=2, scl=0):
        self.pins = {}
        for i, m in enumerate(module):
            pin = machine.Pin(m, machine.Pin.OUT) # , machine.Pin.PULL_UP)
            self.pins[i] = pin
            # GPIO.setup(m, GPIO.OUT)
        self.width = width
        self.height = height
        self.pulsewidth = 0.0001
        self.module = module
        self.ioexp = MCP23017.Portexpander(i2c_address=address, sda=sda, scl=scl)
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
        write a pixel in the buffer
        """
        assert 0 <= x <= self.width
        assert 0 <= y <= self.height
        self.buffer[x][y] = val

    def flipdot(self, x, y, val):
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
        self.pins[mod].on()
        #GPIO.output(self.module[mod], GPIO.HIGH)    # create a short pulse to enable module
        time.sleep(self.pulsewidth)
        self.ioexp.write_value('A', 0x00)
        self.pins[mod].off()
        #GPIO.output(self.module[mod], GPIO.LOW)

    def printbuffer(self):
        """
        print the buffer on terminal
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
        show the buffer on flip dot display
        set the fullbuffer-flag to show whole buffer on the display and not only the changes
        """
        #self.printbuffer()
        for x in range(self.width):
            for y in range(self.height):
                if (self.buffer[x][y] != self.oldbuffer[x][y] or fullbuffer):
                    self.flipdot(x, y, self.buffer[x][y])
                    self.oldbuffer[x][y] = self.buffer[x][y]

    def show2(self):
        """
        maybe a bit faster than show(True)
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
                self.pins[mod].on()
                #GPIO.output(self.module[mod], GPIO.HIGH)
                time.sleep(self.pulsewidth)
                #self.ioexp.write_value('A', 0x00)
                self.pins[mod].off()
                #GPIO.output(self.module[mod], GPIO.LOW)

