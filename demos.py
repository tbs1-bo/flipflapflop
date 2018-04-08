# demos.py

# Some demos inspired by the exmaples of the scrollphathd
# https://github.com/pimoroni/scroll-phat-hd

import flipdotsim
import math
import time
import random


class DemoBase:
    def __init__(self, flipdotdisplay):
        self.fdd = flipdotdisplay

    def run(self):
        while True:
            self.prepare()
            for x in range(self.fdd.width):
                for y in range(self.fdd.height):
                    val = self.handle_px(x, y)
                    self.fdd.px(x, y, val)
            self.fdd.show()

    def handle_px(self, x, y):
        """Specifiy the color pixel a x|y should have by returning truth val."""
        raise Exception("Must be overriden!")

    def prepare(self):
        """Do some preparation before update."""
        pass


class PlasmaDemo(DemoBase):
    """Plasma"""
    def __init__(self, flipdotdisplay):
        super().__init__(flipdotdisplay)
        self.i = 0
        self.s = 1

    def prepare(self):
        self.i += 2
        self.s = math.sin(self.i / 50.0) * 2.0 + 6.0

    def handle_px(self, x, y):
        v = 0.3 + (0.3 * math.sin((x * self.s) + self.i / 4.0) *
                   math.cos((y * self.s) + self.i / 4.0))
        return v > 0.3


class RotatingPlasmaDemo(DemoBase):
    """Rotating Plasma"""
    def __init__(self, flipdotdisplay):
        super().__init__(flipdotdisplay)
        self.current = time.time()

    def prepare(self):
        self.current = time.time()

    def handle_px(self, x, y):
        v = math.sin(1*(0.5*x*math.sin(self.current/2) +
                        0.5*y*math.cos(self.current/3)) + self.current)
        # -1 < sin() < +1
        # therfore correct the value and bring into range [0, 1]
        v = (v+1.0) / 2.0
        return v > 0.5


class SwirlDemo(DemoBase):
    """Rotating Swirl"""
    def __init__(self, flipdotdisplay):
        super().__init__(flipdotdisplay)
        self.timestep = math.sin(time.time() / 18) * 1500

    def prepare(self):
        self.timestep = math.sin(time.time() / 18) * 1500

    def handle_px(self, x, y):
        return self.swirl(x, y, self.timestep) > 0.2

    def swirl(self, x, y, step):
        x -= (self.fdd.width/2.0)
        y -= (self.fdd.height/2.0)

        dist = math.sqrt(pow(x, 2) + pow(y, 2))

        angle = (step / 10.0) + dist / 1.5

        s = math.sin(angle)
        c = math.cos(angle)

        xs = x * c - y * s
        ys = x * s + y * c

        r = abs(xs + ys)

        return max(0.0, 0.7 - min(1.0, r/8.0))


class PingPong(DemoBase):
    """PingPong Demo"""
    def __init__(self, flipdotdisplay):
        super().__init__(flipdotdisplay)
        self.vel = [1, 1]
        self.pos = [0, self.fdd.height // 2]

    def handle_px(self, x, y):
        if x == self.pos[0] and y == self.pos[1]:
            return True
        else:
            return False

    def prepare(self):
        if self.pos[0] + self.vel[0] > self.fdd.width or \
                self.pos[0] + self.vel[0] < 0:
            self.vel[0] = -self.vel[0]

        if self.pos[1] + self.vel[1] > self.fdd.height or \
                self.pos[1] + self.vel[1] < 0:
            self.vel[1] = -self.vel[1]

        self.pos = [self.pos[0] + self.vel[0],
                    self.pos[1] + self.vel[1]]
        # TODO just for the hardware version of the display. Can be removed
        #      if it controls the framerate itself.
        time.sleep(0.05)


class RandomDot(DemoBase):
    """Random Dots"""
    def __init__(self, flipdotdisplay):
        super().__init__(flipdotdisplay)

    def handle_px(self, x, y):
        return random.randint(0, 1)


def main():
    import display
    fdd = display.get_display(width=28, height=16,
                              fallback=display.Fallback.SIMULATOR)
    demos = [PlasmaDemo(fdd), SwirlDemo(fdd), PingPong(fdd), RandomDot(fdd),
             RotatingPlasmaDemo(fdd)]
    print("\n".join([str(i) + ": " + d.__doc__ for i, d in enumerate(demos)]))
    num = int(input(">"))
    print("Running demo. CTRL-C to abort.")
    demos[num].run()


if __name__ == "__main__":
    main()
