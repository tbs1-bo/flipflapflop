# A lot of bdf fonts can be found at https://github.com/olikraus/u8g2/tree/master/tools/font/bdf

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
        "returns a list of 8-bit-integers that represent the letter"
        try:
            letter_index = self.fontlist.index('ENCODING '+str(ord(l))+'\n')
        except ValueError:
            # character not found, return a space (ASCII 32)
            letter_index = self.fontlist.index('ENCODING '+str(32)+'\n')

        # find the next BITMAP section that belongs to the character
        bitmap_data = self.fontlist.index('BITMAP\n', letter_index) + 1

        # read the bitmap data of the character (hey values) and convert it to 
        # a list of integers
        letter = []
        for i in range(self.height):
            letter.append(int(self.fontlist[bitmap_data+i], 16))

        return letter

def small_font():
    return Font("ressources/fonts/4x6.bdf", 4, 6)

def big_font():
    return Font("ressources/fonts/clR6x12.bdf", 6, 12)

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
        self.text = text
        self.changetext(text)
        self.x = 0
        self.y = 0
        self.statictext(self.text, (self.x, self.y))

    def statictext(self, text, start=(0, 0)):
        """Show the given given text with the given font on the display."""
        for l_index in range(len(text)):
            letter = self.font.letter(text[l_index])
            y1 = start[1]
            y2 = y1 + self.font.height
            x1 = start[0] + l_index * self.font.width
            x2 = x1 + self.font.width
            for x in range(max(x1, 0), min(x2, self.fdd.width)):
                for y in range(max(y1, 0), min(y2, self.fdd.height)):
                    """ make the bit pattern of the letter row right-aligned """
                    letter_row = letter[y-y1] >> (7-self.font.width)
                    """ mask one bit of the pattern """
                    draw_dot = letter_row & (1<<(x2-x+1)) == (1<<(x2-x+1))
                    self.fdd.px(x, y, draw_dot)
    
    def scrolltext(self, step=1):
        """Scroll the text (one step)."""
        if abs(self.x) + step >= (len(self.text)//2) * self.font.width:
            self.x = 0
        else:
            self.x = self.x-step
        self.statictext(self.text, (self.x, self.y))

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

def test_text_scroller():
    import flipdotsim
    import time

    fonts = [small_font(), big_font(),
             Font("ressources/fonts/6x9.bdf", 6, 9),
             Font("ressources/fonts/7x13.bdf", 7, 13)]
        
    fdd = flipdotsim.FlipDotSim()
    for font in fonts:
        fdd.clear()
        TextScroller(fdd, "Ha llo", font)
        fdd.show()
        time.sleep(0.5)

def demo_text_lower():
    print("starting text scoller")
    import displayprovider
    import time
    fdd = displayprovider.get_display()
    print("using display", fdd)
    txt = TextScroller(fdd, "", small_font())
    #time.sleep(1)    
    txt.statictext("labor", (0,8))
    fdd.show()
    #time.sleep(5)

if __name__ == "__main__":
    #test_text_scroller()
    demo_text_lower()