import RPi.GPIO as GPIO
import MCP23017
import time

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
    def __init__(self, address = 0x21, enable = 14, width=4*28, height=16, pwm = [15, 18, 23, 24]):
        #self.pwmfrequency = float(input("PWM Frequency in Hz: "))
        #self.pwmdc = float(input("PWM duty cycle in %: "))
        self.pwmfrequency = 10000
        self.pwmdc = 30
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(enable, GPIO.OUT)
        for p in pwm:
            GPIO.setup(p, GPIO.OUT)
        self.width = width
        self.height = height
        self.pwm = [GPIO.PWM(p, self.pwmfrequency) for p in pwm]
        GPIO.output(enable, GPIO.HIGH)
        self.ioexp = MCP23017.Portexpander(address, 1)
        self.ioexp.config_inout('A', 0b11000000)
        self.ioexp.config_inout('B', 0b11000000)
        self.ioexp.write_value('A', 0xff)
        self.ioexp.write_value('B', 0xff)
        self.bigfont = Font('clR6x12.bdf', 6, 12)
        self.smallfont = Font('4x6.bdf', 4, 6)
        self.buffer = []
        for x in range(width):
            spalte = [False]*height
            self.buffer.append(spalte)

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
                    print("#", end="")
                else:
                    print(".", end="")

    def show(self):
        """
        show the buffer on flip dot display
        """
        #self.printbuffer()
        for x in range(self.width):
            modulnummer = x // 28
            if x % 28 == 0:
                self.pwm[modulnummer].start(self.pwmdc)
                #print("starte", modulnummer)
            for y in range(self.height):
                self.flipdot(x, y, self.buffer[x][y])
            if (x+1) % 28 == 0:
                self.pwm[modulnummer].stop()
                #print("stoppe", modulnummer)


    def toggle(self, delay=1):
        """
        make the display yellow, wait, make the display black, wait
        """
        self.clear(True)
        self.show()
        time.sleep(delay)
        self.clear(False)
        self.show()
        time.sleep(delay)


    def _enable(self, enable=5):
        self.ioexp.output('B', enable, False)
        self.ioexp.output('B', enable, True)

    def flipdot(self, x, y, val):
        col = x % 28
        if(val):
            a = (y//7<<3) + y%7 + 1
            b = 0b00100000 + (col//7<<3) + col%7 + 1
        else:
            a = 0b00100000 + (y//7<<3) + y%7 + 1
            b = 0b00100000 + (col//7<<3) + col%7 + 1
        self.ioexp.write_value('A', a)
        self.ioexp.write_value('B', b)
        self._enable()

    def text(self, text, font, start = (0,0)):
        for l_index in range(len(text)):
            letter = font.letter(text[l_index])
            y1 = start[1]
            y2 = y1 + font.height
            x1 = start[0] + l_index*font.width
            x2 = x1 + font.width
            for x in range(max(x1, 0), min(x2, self.width)):
                for y in range(max(y1, 0), min(y2, self.height)):
                    col = font.width-(x2-x)
                    val = (letter[y-start[1]] & (0x80>>(col))) == (0x80>>(col))
                    self.px(x, y, val)


    def scrolltext(self, text, font, step):
        running = True
        self.clear()
        spaces = max((self.width // font.width) - len(text), 0) + 1
        text = text + ' '*spaces
        text = text*2
        x = 0
        y = 0
        while True:
            self.text(text, font, (x, y))
            self.show()
            if(abs(x) + step >= (len(text)//2) * font.width):
                x = 0
            else:
                x = x-step

def main():
    fd = FlipDotDisplay(0x21, 14, 28, 13, [15])
    try:
        fd.toggle(0.1) # "clean" the display
        #fd.scrolltext("HELLO WORLD", fd.smallfont, 3)
        fd.text("HELLO", fd.smallfont, (4, 1))
        fd.text("WORLD!", fd.smallfont, (2, 7))
        while(True):
            fd.show()
            time.sleep(5)   # refresh display every 5 seconds

        GPIO.cleanup()
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("flip flap flop")

if __name__ == "__main__":
    main()
