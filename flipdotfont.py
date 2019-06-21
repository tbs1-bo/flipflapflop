
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
    return Font("ressources/4x6.bdf", 6, 4)

def big_font():
    return Font("ressources/clR6x12.bdf", 6, 12)

class TextScroller:
    """Write Text on Flipdotdisplays. A simple usage with a FlipDot-Simulator
    is shown in the following.

        >>> import flipdotfont
        >>> import flipdotsim
        >>> fds = flipdotsim.FlipDotSim(28)
        >>> fdw = flipdotfont.TextScroller(fds)
        >>> fdw.scrolltext('Test 12345!', flipdotfont.big_font(), 1)

    """

    def __init__(self, flipdotdisplay):
        self.fdd = flipdotdisplay

    def text(self, text, font, start=(0, 0)):
        """Show the given given text with the given font on the display."""
        for l_index in range(len(text)):
            letter = font.letter(text[l_index])
            y1 = start[1]
            y2 = y1 + font.height
            x1 = start[0] + l_index*font.width
            x2 = x1 + font.width
            for x in range(max(x1, 0), min(x2, self.fdd.width)):
                for y in range(max(y1, 0), min(y2, self.fdd.height)):
                    draw_dot = letter[y] & (1<<(x2-x+1)) == (1<<(x2-x+1))
                    self.fdd.px(x, y, draw_dot)
        self.fdd.show()

    def scrolltext(self, text, font, step=1):
        """Scroll text with a given font."""
        running = True
        self._clear()
        spaces = max((self.fdd.width // font.width) - len(text), 0) + 1
        text = text + ' '*spaces
        text = text*2
        x = 0
        y = 0
        while running:
            self.text(text, font, (x, y))
            if abs(x) + step >= (len(text)//2) * font.width:
                x = 0
            else:
                x = x-step

    def _clear(self):
        for y in range(self.fdd.height):
            for x in range(self.fdd.width):
                self.fdd.px(x, y, False)

        self.fdd.show()

