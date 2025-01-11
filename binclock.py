import time


class BinClock:
    def __init__(self, fdd):
        self.fdd = fdd
        self.visible = True

    def digit(self, dig, dx, dy):
        pat = None
        if dig == '1':
            pat = [[False, False, False, False],
                   [False, True, False, False],
                   [False, True, False, False],
                   [False, True, False, False]]
        elif dig == '0':
            pat = [[False, False, False, False],
                   [True, True, True, False],
                   [True, False, True, False],
                   [True, True, True, False]]
        for x in range(4):
            for y in range(4):
                self.fdd.px(4*dx+x, 4*dy+y, pat[y][x])

    def run(self, runtime=0):
        start_time = time.time()

        while runtime==0 or time.time() - start_time < runtime:
            if self.visible:
                t = time.localtime()
                ihour = t[3]
                imin = t[4]
                isec = t[5]
                bhour = bin(ihour+64)[3:]
                bmin = bin(imin+64)[3:]
                bsec = bin(isec+64)[3:]
                self.clear()
                for x in range(6):
                    self.digit(bhour[x], x, 0)
                    self.digit(bmin[x], x, 1)
                    # self.digit(bsec[x], x, 2)
                self.draw_seconds_bar(isec, imin)
                self.fdd.show()
            time.sleep(0.2)

    def draw_seconds_bar(self, seconds, minutes):
        """Draw three lines for the seconds. Each line representing 20
        seconds."""
        self.draw_bar_borders()
        for x in range(2, 22):
            x_ = x - 3
            even = minutes % 2 == 0
            self.fdd.px(x, 2 * 4 + 1, even ^ (x_ < seconds))
            self.fdd.px(23 - x, 2 * 4 + 2, even ^ (x_ + 20 < seconds))
            self.fdd.px(x, 2 * 4 + 3, even ^ (x_ + 40 < seconds))

    def draw_bar_borders(self):
        for x in (0, 23):
            for y in range(2 * 4 + 1, 2 * 4 + 4):
                self.fdd.px(x, y, True)

    def clear(self):
        for y in range(self.fdd.height):
            for x in range(self.fdd.width):
                self.fdd.px(x, y, False)

def test_binclock():
    import flipdotsim
    fdd = flipdotsim.FlipDotSim(28, 13)
    bc = BinClock(fdd)
    bc.run(runtime=2)

def main():
    import displayprovider
    fdd = displayprovider.get_display()
    bc = BinClock(fdd)
    bc.run()

if __name__ == "__main__":
    main()