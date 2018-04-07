# demos.py

# Some demos inspired by the exmaples of the scrollphathd
# https://github.com/pimoroni/scroll-phat-hd

import flipdotsim
import math
import time
import random

class PlasmaDemo:
    """Plasma"""
    def __init__(self, flipdotdisplay):
        self.fdd = flipdotdisplay

    def run(self):
        i = 0
        while True:
            i += 2
            s = math.sin(i / 50.0) * 2.0 + 6.0

            for x in range(0, self.fdd.width):
                for y in range(0, self.fdd.height):
                    v = 0.3 + (0.3 * math.sin((x * s) + i / 4.0) *
                               math.cos((y * s) + i / 4.0))
                    self.fdd.px(x, y, v > 0.3)

            self.fdd.show()


class SwirlDemo:
    """Rotating Swirl"""
    def __init__(self, flipdotdisplay):
        self.fdd = flipdotdisplay

    def run(self):
        while True:
            timestep = math.sin(time.time() / 18) * 1500

            for x in range(0, self.fdd.width):
                for y in range(0, self.fdd.height):
                    v = self.swirl(x, y, timestep)
                    self.fdd.px(x, y, v > 0.2)

            self.fdd.show()

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


class PingPong:
    """PingPong Demo"""
    def __init__(self, flipdotdisplay):
        self.fdd = flipdotdisplay

    def clear(self):
        for x in range(self.fdd.width):
            for y in range(self.fdd.height):
                self.fdd.px(x, y, False)

    def run(self):
        x = 0
        y = self.fdd.height // 2
        direction = 1
        while True:
            self.fdd.clear()
            self.fdd.px(x, y, True)
            self.fdd.show()

            if x+direction > self.fdd.width or x+direction < 0:
                direction = -direction

            x += direction


class RandomDot:
    """Random Dots"""
    def __init__(self, flipdotdisplay):
        self.fdd = flipdotdisplay

    def run(self):
        while True:
            for x in range(self.fdd.width):
                for y in range(self.fdd.height):
                    self.fdd.px(x, y, random.randint(0, 1))
            self.fdd.show()


def main():
    fdd = flipdotsim.FlipDotSim()
    demos = [
        PlasmaDemo(fdd),
        SwirlDemo(fdd),
        PingPong(fdd),
        RandomDot(fdd)
        ]
    print("\n".join([str(i) + ": " + d.__doc__ for i, d in enumerate(demos)]))
    num = int(input(">"))
    demos[num].run()


if __name__ == "__main__":
    main()
