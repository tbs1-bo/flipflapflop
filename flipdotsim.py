import pygame
import displayprovider

YELLOWDOT_FILE = "ressources/y.jpg"
BLACKDOT_FILE = "ressources/b.jpg"

class Font:
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
        return letter


class FlipDotSim(displayprovider.DisplayBase):
    def __init__(self, width=28, height=13, fps=30):
        super().__init__(width, height)
        pygame.init()
        pygame.display.set_caption("FlipDot Simulator")
        self.screen = pygame.display.set_mode((self.width*20, self.height*20))
        self.y = pygame.image.load(YELLOWDOT_FILE).convert()
        self.b = pygame.image.load(BLACKDOT_FILE).convert()
        self.bigfont = Font('clR6x12.bdf', 6, 12)
        self.clock = pygame.time.Clock()
        self.fps = fps

    def set(self, x, y):
        self.screen.blit(self.y, (x*20, y*20))

    def reset(self, x, y):
        self.screen.blit(self.b, (x*20, y*20))

    def px(self, x, y, val):
        if val:
            self.set(x, y)
        else:
            self.reset(x, y)

    def show(self):
        # empty the event queue to prevent it from being full
        pygame.event.get()
        pygame.display.flip()
        self.clock.tick(self.fps)

    def clear(self, invert=False):
        for x in range(self.width):
            for y in range(self.height):
                if invert:
                    self.set(x, y)
                else:
                    self.reset(x, y)

    def text(self, text, font, start=(0, 0)):
        for l_index in range(len(text)):
            letter = font.letter(text[l_index])
            y1 = start[1]
            y2 = y1 + font.height
            x1 = start[0] + l_index*font.width
            x2 = x1 + font.width
            for x in range(max(x1, 0), min(x2, self.width)):
                for y in range(max(y1, 0), min(y2, self.height)):
                    if letter[y] & (1<<(x2-x+1)) == (1<<(x2-x+1)):
                        self.set(x, y)
                    else:
                        self.reset(x, y)

    def scrolltext(self, text, font, step):
        #if font == 'bigfont':
        #   font = self.bigfont
        running = True
        self.clear()
        spaces = max((self.width // font.width) - len(text), 0) + 1
        text = text + ' '*spaces
        text = text*2
        x = 0
        y = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            self.text(text, font, (x, y))
            self.show()
            if abs(x) + step >= (len(text)//2) * font.width:
                x = 0
            else:
                x = x-step
            
        pygame.quit()
    """
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
        pygame.quit()
    """


if __name__ == '__main__':
    fds = FlipDotSim(28)
    fds.scrolltext('Test 12345!', fds.bigfont, 1)
