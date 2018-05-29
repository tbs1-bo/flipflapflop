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


if __name__ == '__main__':
    import flipdotfont    
    fds = FlipDotSim(28)
    fdw = flipdotfont.TextScroller(fds)
    fdw.scrolltext('Test 12345!', fds.bigfont, 1)
