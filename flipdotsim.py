"""
A package that allows for simulating the display without the need of a physical
display. It relies on the pygame-package.

The simulator can be used in the following way.
Creating a display with specific dimensions.

    >>> import flipdotsim
    >>> fds = flipdotsim.FlipDotSim(width=28, height=13)

Set two pixels at the top left to be turned on.

    >>> fds.px(0,0, True)
    >>> fds.px(0,1, True)

Actually turn on or off all pixels.

    >>> fds.show()

"""

import pygame
import displayprovider

YELLOWDOT_FILE = "ressources/y.jpg"
BLACKDOT_FILE = "ressources/b.jpg"
IMG_WIDTH_HEIGHT = 20  # pixel on each side

class FlipDotSim(displayprovider.DisplayBase):
    'Simulator class that shows the display in a pygame GUI.'

    def __init__(self, width=28, height=13, fps=30):
        super().__init__(width, height)
        pygame.init()
        pygame.display.set_caption("FlipDot Simulator")
        self.screen = pygame.display.set_mode(
            (self.width*IMG_WIDTH_HEIGHT, self.height*IMG_WIDTH_HEIGHT))
        self.y = pygame.image.load(YELLOWDOT_FILE).convert()
        self.b = pygame.image.load(BLACKDOT_FILE).convert()        
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.clear()

    def set(self, x, y):
        self.screen.blit(self.y, (x*IMG_WIDTH_HEIGHT, y*IMG_WIDTH_HEIGHT))

    def reset(self, x, y):
        self.screen.blit(self.b, (x*IMG_WIDTH_HEIGHT, y*IMG_WIDTH_HEIGHT))

    def px(self, x, y, val):
        """Set a pixel to on or off at (X|Y). The dot will not be displayed 
        immediately."""
        if val:
            self.set(x, y)
        else:
            self.reset(x, y)

    def show(self):
        """Show the current state of all pixels on the display."""
        # empty the event queue to prevent it from being full
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)

        pygame.display.flip()
        self.clock.tick(self.fps)

    def clear(self, invert=False):
        for x in range(self.width):
            for y in range(self.height):
                if invert:
                    self.set(x, y)
                else:
                    self.reset(x, y)

    def close(self):
        'Deinitialize pygame and close open windows.'
        pygame.quit()

    def led(self, on_off):
        'does nothing'
        # TODO led support for simulator #10
        pass


def test_flipdot_sim():
    import time

    fdd = FlipDotSim(width=3, height=2)

    fdd.px(0, 0, True)
    fdd.px(1, 1, True)
    fdd.show()
    time.sleep(0.3)

    fdd.reset(0, 0)
    fdd.set(1, 0)
    fdd.show()
    time.sleep(0.3)

    fdd.clear()
    fdd.show()
    time.sleep(0.3)

    fdd.clear(invert=True)
    fdd.show()
    time.sleep(0.3)

    fdd.close()


if __name__ == '__main__':
    import flipdotfont
    import configuration
    import time
    fds = FlipDotSim(
        width=configuration.WIDTH, 
        height=configuration.HEIGHT,
        fps=configuration.simulator["fps"])
    scroller = flipdotfont.TextScroller(fds, 
                                        "Test 12345!", flipdotfont.big_font())
    for _ in range(20):
        scroller.scrolltext()
        fds.show()
        time.sleep(0.1)
        