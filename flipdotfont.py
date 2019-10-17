
class Font:
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

def small_font():
    return Font("ressources/4x6.bdf", 4, 6)

def big_font():
    return Font("ressources/clR6x12.bdf", 6, 12)

class TextScroller:
    """Write Text on Flipdotdisplays. A simple usage with a FlipDot-Simulator
    is shown in the following.

    >>> import flipdotfont
    >>> import flipdotsim
    >>> import time
    >>> fds = flipdotsim.FlipDotSim(28, 13)
    >>> t = flipdotfont.TextScroller(fds, "Hello world.", 
    ...                                 flipdotfont.big_font())
    >>> for _ in range(20):
    ...     t.scrolltext()
    ...     fds.show()
    ...     time.sleep(0.1)

    """

    def __init__(self, flipdotdisplay, text, font):
        self.fdd = flipdotdisplay
        self.font = font
        self.text = ""
        self.changetext(text)
        self.x = 0
        self.y = 0
        self.statictext(self.text, font, (self.x, self.y))

    def statictext(self, text, font, start=(0, 0)):
        """Show the given given text with the given font on the display."""
        for l_index in range(len(text)):
            letter = font.letter(text[l_index])
            y1 = start[1]
            y2 = y1 + font.height
            x1 = start[0] + l_index*font.width
            x2 = x1 + font.width
            for x in range(max(x1, 0), min(x2, self.fdd.width)):
                for y in range(max(y1, 0), min(y2, self.fdd.height)):
                    """ make the bit pattern of the letter row right-aligned """
                    letter_row = letter[y-y1] >> (7-font.width)
                    """ mask one bit of the pattern """
                    draw_dot = letter_row & (1<<(x2-x+1)) == (1<<(x2-x+1))
                    self.fdd.px(x, y, draw_dot)
    
    def scrolltext(self, step=1):
        """Scroll the text (one step)."""
        if abs(self.x) + step >= (len(self.text)//2) * self.font.width:
            self.x = 0
        else:
            self.x = self.x-step
        self.statictext(self.text, self.font, (self.x, self.y))

    def changetext(self, text):
        """Change the text and add some spaces."""
        self.text = text
        spaces = max((self.fdd.width // self.font.width) - len(self.text), 0) + 1
        self.text = self.text + ' '*spaces
        self.text = self.text*2

    def _clear(self):
        for y in range(self.fdd.height):
            for x in range(self.fdd.width):
                self.fdd.px(x, y, False)

        self.fdd.show()

