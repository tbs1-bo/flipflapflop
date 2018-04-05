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

