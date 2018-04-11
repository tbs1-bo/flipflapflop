"""
Demos for a flipdotdisplay.

Some of the demos (PlasmaDemo and SwirlDemo) are inspired by the exmaples
of the scrollphathd: https://github.com/pimoroni/scroll-phat-hd

"""


import math
import time
import random
try:
    import pygame
except ImportError as e:
    print("Unable to import pygame. Snake may not be runnable!", e)


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


class GameOfLife(DemoBase):
    """Conway's Game of Life"""

    glider = {
        (2, 2),
        (1, 2),
        (0, 2),
        (2, 1),
        (1, 0),
    }

    MAX_ITERATIONS = 100

    def __init__(self, flipdotdisplay):
        super().__init__(flipdotdisplay)
        # self.cells = GameOfLife.glider
        self.cells = set()
        self.iterations = 0
        self.reset()

    def reset(self):
        self.iterations = 0
        for i in range(self.fdd.width * self.fdd.height // 2):
            x = random.randint(0, self.fdd.width - 1)
            y = random.randint(0, self.fdd.height - 1)
            self.cells.add((x, y))

    def _iterate(self):
        new_board = set()
        for cell in self.cells:
            neighbours = self._neighbours(cell)
            if len(self.cells.intersection(neighbours)) in (2, 3):
                new_board.add(cell)
            for nb in neighbours:
                if len(self.cells.intersection(self._neighbours(nb))) == 3:
                    new_board.add(nb)

        return new_board

    def _neighbours(self, cell):
        x, y = cell
        r = range(-1, 2)  # -1, 0, +1
        return set((x+i, y+j) for i in r for j in r if not i == j == 0)

    def prepare(self):
        self.cells = self._iterate()
        self.iterations += 1
        if self.iterations > GameOfLife.MAX_ITERATIONS:
            self.reset()

    def handle_px(self, x, y):
        return (x, y) in self.cells


class SnakeGame(DemoBase):
    """Snake Game. Control with WASD or an attached Joystick."""
    def __init__(self, flipflopdisplay):
        super().__init__(flipflopdisplay)
        self.snake_body = None
        self.snake_direction = None
        self.pill = None
        self.joystick = None
        self.reset()

    def run(self):
        """Overriden from base class."""
        # add joystick if present
        pygame.joystick.init()
        print("found", pygame.joystick.get_count(), "Joysticks")
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        super().run()

    def reset(self):
        self.snake_body = [(3, 1), (2, 1), (1, 1)]
        self.snake_direction = [1, 0]
        self.create_new_pill()

    def prepare(self):
        self.move_snake()
        if len(self.snake_body) != len(set(self.snake_body)):
            # snake eats itself
            self.reset()

        if self.pill in self.snake_body:
            self.create_new_pill()

        self.handle_input()

    def move_snake(self):
        # move the snakes head
        head = self.snake_body[0]
        new_head = ((head[0] + self.snake_direction[0]) % self.fdd.width,
                    (head[1] + self.snake_direction[1]) % self.fdd.height)

        if new_head == self.pill:
            # eat pill
            new_body = self.snake_body
        else:
            # move forward
            new_body = self.snake_body[:-1]
        self.snake_body = [new_head] + new_body

    def handle_input(self):
        xdir, ydir = self.snake_direction
        xax, yax = 0, 1
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION and self.joystick:
                if self.joystick.get_axis(yax) < 0 and ydir != 1:
                    self.snake_direction = [0, -1]
                elif self.joystick.get_axis(yax) > 0 and ydir != -1:
                    self.snake_direction = [0, 1]
                elif self.joystick.get_axis(xax) > 0 and xdir != -1:
                    self.snake_direction = [1, 0]
                elif self.joystick.get_axis(xax) < 0 and xdir != 1:
                    self.snake_direction = [-1, 0]

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and ydir != 1:
                    self.snake_direction = [0, -1]
                elif event.key == pygame.K_s and ydir != -1:
                    self.snake_direction = [0, 1]
                elif event.key == pygame.K_d and xdir != -1:
                    self.snake_direction = [1, 0]
                elif event.key == pygame.K_a and xdir != 1:
                    self.snake_direction = [-1, 0]

    def create_new_pill(self):
        new_pill = None
        while new_pill in self.snake_body or new_pill is None:
            new_pill = (random.randint(0, self.fdd.width-1),
                        random.randint(0, self.fdd.height-1))

        self.pill = new_pill

    def handle_px(self, x, y):
        return (x, y) in self.snake_body or (x, y) == self.pill


class FlappDot(DemoBase):
    """Flappy Dot"""
    def __init__(self, flipdotdisplay):
        super().__init__(flipdotdisplay)
        self.pos = (1, 1)
        self.line_x = self.fdd.width - 1
        self.gap = (1, 5)
        self.score = 0
        self.reset()

    def reset(self):
        self.pos = (1, 1)
        self.line_x = self.fdd.width - 1
        self.gap = (1, 5)
        self.score = 0

    def handle_input(self):
        newx, newy = self.pos
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    newy -= 1
                    self.pos = (newx, newy)
                    return

        newy += 1
        self.pos = (newx, newy)

    def prepare(self):
        time.sleep(0.1)     # TODO remove this when display handles framerate
        self.handle_input()
        self.move_line()
        if not self.bird_is_alive():
            self.reset()

    def bird_is_alive(self):
        if self.pos[1] < 0 or self.pos[1] > self.fdd.height:
            # bird outside screen
            return False

        return self.line_x != self.pos[0] or \
            self.gap[0] < self.pos[1] < self.gap[1]

    def move_line(self):
        self.line_x -= 1
        if self.line_x < 0:
            # create new line
            self.line_x = self.fdd.width - 1
            gap_start = random.randint(0, self.fdd.height - 5)
            self.gap = (gap_start, gap_start + 5)
            self.score += 1

    def handle_px(self, x, y):
        if self.pos == (x, y):
            # draw flappy
            return True
        elif x == self.fdd.width - 1:
            # show score at last column
            return y < self.score
        else:
            # draw line with gap
            if self.line_x == x:
                return not (self.gap[0] <= y <= self.gap[1])

        return False


def main():
    import displayprovider
    fdd = displayprovider.get_display(
        width=28, height=16, fallback=displayprovider.Fallback.SIMULATOR)
    demos = [PlasmaDemo(fdd), SwirlDemo(fdd), PingPong(fdd), RandomDot(fdd),
             RotatingPlasmaDemo(fdd), GameOfLife(fdd), SnakeGame(fdd),
             FlappDot(fdd)]
    print("\n".join([str(i) + ": " + d.__doc__ for i, d in enumerate(demos)]))
    num = int(input(">"))
    print("Running demo. CTRL-C to abort.")
    demos[num].run()


if __name__ == "__main__":
    main()
