#import RPi.GPIO as GPIO
#import flipdotdisplay as FDD
import uflipdotdisplay as FDD
from flipdotfont import Font
import time

class Flipflapflop:
    def __init__(self, flipdotdisplay):
        self.fdd = flipdotdisplay

    
    def clear(self, invert = False):
        """
        make all pixel in the buffer black or yellow
        """
        for x in range(self.fdd.width):
            self.fdd.buffer[x] = [invert]*self.fdd.height

    def toggle(self, delay=1):
        """
        make the display yellow, wait, make the display black, wait
        """
        self.clear(True)
        self.fdd.show(True)
        time.sleep(delay)
        self.clear(False)
        self.fdd.show(True)
        time.sleep(delay)

    def toggle2(self, delay):
        self.clear(True)
        self.fdd.show2()
        time.sleep(delay)
        self.clear(False)
        self.fdd.show2()

    def text(self, text, font, pos = (0,0)):
        """
        write a text on position (x, y) (upper left dot)
        """
        # TODO move text related stuff into separate class/package
        for l_index in range(len(text)):
            letter = font.letter(text[l_index])
            y1 = pos[1]
            y2 = y1 + font.height
            x1 = pos[0] + l_index*font.width
            x2 = x1 + font.width
            for x in range(max(x1, 0), min(x2, self.fdd.width)):
                for y in range(max(y1, 0), min(y2, self.fdd.height)):
                    col = font.width-(x2-x)
                    val = (letter[y-pos[1]] & (0x80>>(col))) == (0x80>>(col))
                    self.fdd.px(x, y, val)
            self.fdd.show()

    def scrolltext(self, text, font, step=1, top=0, delay=0.001):
        """
        scroll the text like a ticker
        """
        # TODO move text related stuff into separate class/package
        self.clear()
        spaces = max((self.fdd.width // font.width) - len(text), 0) + 1
        text = text + ' '*spaces
        text = text*2
        x = 0
        y = top
        while True:
            self.text(text, font, (x, y))
            self.fdd.show()
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
        for y in range(self.fdd.height):
            if y%2 == 0:
                xlist = list(range(self.fdd.width))
            else:
                xlist = list(range(self.fdd.width)[::-1])
            for x in xlist:
                self.fdd.px(x, y, True)
                time.sleep(0.01)
                self.fdd.show()
                #self.fdd.px(x, y, False)


def main():
    bigfont = Font('clR6x12.bdf', 6, 12)
    smallfont = Font('4x6.bdf', 4, 6)
    fdd = FDD.FlipDotDisplay(0x20, 28, 13, [18])
    fff = Flipflapflop(fdd)
    try:
        fff.toggle(0.5)
        time.sleep(1)
        fff.toggle2(0.5)
        time.sleep(1)
        fff.text("HELLO", smallfont, (4, 1))
        time.sleep(0.5)
        fff.text("WORLD!", smallfont, (2, 7))
        time.sleep(0.5)
        fff.movingdot()
        time.sleep(0.5)
        fff.scrolltext("flip, flap, flop!", bigfont)
        while(True):
            #fff.toggle(0.3)
            fdd.show(True)
            time.sleep(5)   # refresh display every 5 seconds
    except KeyboardInterrupt:
        #GPIO.cleanup()
        print("flip, flap, flop\n")

if __name__ == "__main__":
    main()
