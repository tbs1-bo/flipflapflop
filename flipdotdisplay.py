import RPi.GPIO as GPIO
import MCP23017
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

class Font():
    """
    read a .bdf font file
    letter() gets a character and returns a list of 8-bit-integers.

    example 3x4 "T" 
    [0b11110000,
     0b01100000,
     0b01100000]
    """
    def __init__(self, filename, width, height):
        
        f = open(filename, 'r')
        self.fontlist = f.readlines()
        f.close()
        self.width = width
        self.height = height

    def letter(self, l):
        try:
            index = self.fontlist.index('ENCODING '+str(ord(l))+'\n') + 5
        except:
            index = self.fontlist.index('ENCODING '+str(32)+'\n') + 5
        letter = []
        for i in range(self.height):
            letter.append(int(self.fontlist[index+i], 16))
            #print(bin(int(self.fontlist[index+i], 16)))
        return letter


class FlipDotDisplay:
    def __init__(self, address = 0x20, width=28, height=13, module = [18]):
        GPIO.setmode(GPIO.BCM)
        for m in module:
            GPIO.setup(m, GPIO.OUT)
        self.width = width
        self.height = height
        self.pulsewidth = 0.0003
        self.module = module
        self.ioexp = MCP23017.Portexpander(address, 1)
        self.ioexp.config_inout('A', 0b00000000)
        self.ioexp.config_inout('B', 0b11100000)
        self.ioexp.write_value('A', 0x00)
        self.ioexp.write_value('B', 0x00)
        self.bigfont = Font('clR6x12.bdf', 6, 12)
        self.smallfont = Font('4x6.bdf', 4, 6)
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


    def clear(self, invert = False):
        """
        make all pixel in the buffer black or yellow
        """
        for x in range(self.width):
            for y in range(self.height):
                self.px(x, y, invert)

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

    def toggle(self, delay=1):
        """
        make the display yellow, wait, make the display black, wait
        """
        self.clear(True)
        self.show(True)
        time.sleep(delay)
        self.clear(False)
        self.show(True)
        time.sleep(delay)


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
        GPIO.output(self.module[mod], GPIO.HIGH)    # create a short pulse to enable module
        time.sleep(self.pulsewidth)
        self.ioexp.write_value('A', 0x00)
        GPIO.output(self.module[mod], GPIO.LOW)

    def text(self, text, font, pos = (0,0)):
        """
        write a text on position (x, y) (upper left dot)
        """
        for l_index in range(len(text)):
            letter = font.letter(text[l_index])
            y1 = pos[1]
            y2 = y1 + font.height
            x1 = pos[0] + l_index*font.width
            x2 = x1 + font.width
            for x in range(max(x1, 0), min(x2, self.width)):
                for y in range(max(y1, 0), min(y2, self.height)):
                    col = font.width-(x2-x)
                    val = (letter[y-pos[1]] & (0x80>>(col))) == (0x80>>(col))
                    self.px(x, y, val)


    def scrolltext(self, text, font, step=1, top=0, delay=0.001):
        """
        scroll the text like a ticker
        """
        self.clear()
        spaces = max((self.width // font.width) - len(text), 0) + 1
        text = text + ' '*spaces
        text = text*2
        x = 0
        y = top
        while True:
            self.text(text, font, (x, y))
            self.show()
            if(abs(x) + step >= (len(text)//2) * font.width):
                x = 0
            else:
                x = x-step
            time.sleep(delay)

    def movingdot(self):
        """
        just for fun
        """
        self.clear()
        for y in range(self.height):
            if y%2 == 0:
                xlist = list(range(self.width))
            else:
                xlist = list(range(self.width)[::-1])
            for x in xlist:
                self.px(x, y, True)
                time.sleep(0.01)
                self.show()
                #self.px(x, y, False)

def main():
    fd = FlipDotDisplay(0x20, 28, 13, [18])
    try:
        fd.toggle(0.3) # "clean" the display, flip and flop all the dots
        fd.movingdot()
        fd.scrolltext("flip, flap, flop!", fd.bigfont)
        #fd.text("HELLO", fd.smallfont, (4, 1))
        #fd.text("WORLD!", fd.smallfont, (2, 7))
        while(True):
            fd.show(True)
            time.sleep(5)   # refresh display every 5 seconds
        GPIO.cleanup()
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("flip flap flop")

if __name__ == "__main__":
    main()
