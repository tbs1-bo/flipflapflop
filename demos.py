"""
Demos for a flipdotdisplay.

Some of the demos (PlasmaDemo and SwirlDemo) are inspired by the examples
of the scrollphathd: https://github.com/pimoroni/scroll-phat-hd

"""

# TODO adapt dungeon crawler from 
#      https://github.com/Stolistic/rgb-dungeon-crawl
# TODO Maybe a game inspired by GPN18Schlangenspiel would be interesting.
#      https://git.bingo-ev.de/GPN18Programmierspiel

import math
import time
import random
import util
import abc
import configuration
import rogueflip
import pygame
import pygame.time

FPS = configuration.simulator['fps']

class DemoBase(abc.ABC):
    def __init__(self, flipdotdisplay, fps=FPS):
        self.fdd = flipdotdisplay
        self.fps = fps

    def run(self, runtime=None):
        'Run the demo in an endless loop or for a given time (in seconds)'
        start_time = time.time() 
        pygame.init()
        clock = pygame.time.Clock()

        while (runtime is None) or (time.time()-start_time) < runtime:
            self.one_cycle()
            clock.tick(self.fps)

    def one_cycle(self):
        """Run one cycle of the demo."""
        self.prepare()
        for x in range(self.fdd.width):
            for y in range(self.fdd.height):
                val = self.handle_px(x, y)
                self.fdd.px(x, y, val)
        self.fdd.show()

    @abc.abstractmethod
    def handle_px(self, x, y):
        """Specifiy the color pixel a x|y should have by returning truth val."""
        pass

    def prepare(self):
        """Do some preparation before update."""
        pass

# TODO make more general class for displaying images on the flipdotdisplay
# e.g. can be used to show operator logo from old mobile phones
# find a collection here https://www.oocities.org/wolfitdown/

class PygameSurfaceDemo:
    """Demo for testing the drawing on the display with a pygame Surface 
    class."""

    def __init__(self, flipdotdisplay):
        self.fdd = flipdotdisplay

        # load a surface from an image file and shrinken the clipping
        # area (the visible part) to the size of the flipdotdisplay
        self.surf = pygame.image.load("media/surface_test.png")
        self.surf.set_clip(0, 0, self.fdd.width, self.fdd.height)        

    def run(self, runtime=None):
        'Run the demo in an endless loop or for a given time (in seconds)'
        start_time = time.time() 

        while (runtime is None) or (time.time()-start_time) < runtime:
            self.update()
            # draw the surface onto the display.
            util.draw_surface_on_fdd(self.surf, self.fdd)
            self.fdd.show()

    def update(self):
        # move clipping area one pixel per frame (ip=in place)
        cl = self.surf.get_clip()
        cl.move_ip(1, 0)
        self.surf.set_clip(cl)


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
        self.pills = []
        self.max_pills = self.fdd.width // 10
        self.joystick = None
        self.reset()

    def run(self, runtime=None):
        """Overriden from base class."""
        # add joystick if present
        pygame.init()
        pygame.joystick.init()
        print("found", pygame.joystick.get_count(), "Joysticks")
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        super().run(runtime)

    def reset(self):
        self.snake_body = [(3, 1), (2, 1), (1, 1)]
        self.snake_direction = [1, 0]
        for _i in range(self.max_pills):
            self.create_new_pill()

    def prepare(self):
        self.move_snake()
        if len(self.snake_body) != len(set(self.snake_body)):
            # snake eats itself
            self.reset()

        # if pills have been eaten, fill up with new ones
        while len(self.pills) <= self.max_pills:
            self.create_new_pill()

        self.handle_input()

    def move_snake(self):
        # move the snakes head
        head = self.snake_body[0]
        new_head = ((head[0] + self.snake_direction[0]) % self.fdd.width,
                    (head[1] + self.snake_direction[1]) % self.fdd.height)

        if new_head in self.pills:
            # eat pill
            new_body = self.snake_body
            self.pills.remove(new_head)
        else:
            # move forward
            new_body = self.snake_body[:-1]
        self.snake_body = [new_head] + new_body

    def handle_input(self):
        xdir, ydir = self.snake_direction
        xax, yax = 0, 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
                
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
        while new_pill is None or new_pill in self.snake_body or\
                new_pill in self.pills:
            new_pill = (random.randint(0, self.fdd.width-1),
                        random.randint(0, self.fdd.height-1))

        self.pills.append(new_pill)

    def handle_px(self, x, y):
        return (x, y) in self.snake_body or (x, y) in self.pills


class FlappyDot(DemoBase):
    """Flappy Dot. Control the bird with the w-key or an attached joystick."""

    def __init__(self, flipdotdisplay, max_lines=3):
        super().__init__(flipdotdisplay)
        self.pos = (1, 1)
        # each line is a dictionary with entries x, gap_start, gap_end
        self.lines = []
        self.score = 0
        self.max_lines = max_lines
        self.start_time = time.time()
        pygame.init()
        if pygame.joystick.get_count() > 0:
            print("Joystick(s) found")
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        self.reset()

    def add_line(self, x, gap_start, gap_end):
        self.lines.append({"x": x, "gap_start": gap_start, "gap_end": gap_end})

    def reset(self):
        self.start_time = time.time()
        self.pos = (1, 1)
        self.lines = []
        for i in range(self.max_lines):
            self.add_line(i * self.fdd.width // self.max_lines, 1, 5)
        self.score = 0

    def handle_input(self):
        newx, newy = self.pos
        for event in pygame.event.get():
            # check if keyboard or joystick was used to control the bird
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_w) or \
               (event.type == pygame.JOYBUTTONDOWN and event.button == 0):
                newy -= 1
                self.pos = (newx, newy)
                return

        newy += 1
        self.pos = (newx, newy)

    def prepare(self):
        time.sleep(0.2)     # TODO remove this when display handles framerate
        self.handle_input()
        self.move_lines()
        if not self.bird_is_alive():
            print("Game Over. Time elapsed:", time.time()-self.start_time)
            self.reset()

    def bird_is_alive(self):
        if self.pos[1] < 0 or self.pos[1] > self.fdd.height:
            # bird outside screen (top or bottom)
            return False

        # check collision with one of the lines
        for l in self.lines:
            if not (l['x'] != self.pos[0] or 
                    l['gap_start'] < self.pos[1] < l['gap_end']):
                return False

        return True

    def move_lines(self):
        for l in self.lines:
            l['x'] -= 1
        # remove lines off screen
        self.lines = [l for l in self.lines if l['x'] >= 0]

        if len(self.lines) < self.max_lines:
            # create new line
            gap_start = random.randint(0, self.fdd.height - 5)
            self.add_line(self.fdd.width-1, gap_start, gap_start+5)
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
            for l in self.lines:
                if l['x'] == x:
                    return not (l['gap_start'] <= y <= l['gap_end'])

        return False


class BinaryClock(DemoBase):
    """A binary clock"""

    def __init__(self, flipdotdisplay, offset=(1, 1)):
        super().__init__(flipdotdisplay)
        self.pixels = []
        self.offset = offset

    def prepare(self):
        self.pixels.clear()
        tt = time.localtime()
        for i, t in enumerate([tt.tm_hour, tt.tm_min, tt.tm_sec]):
            self.add_pixels(t, y=i)

    def add_pixels(self, num, y):
        x = self.offset[0]
        # convert to binary, cut off '0b' at the beginning and fill with
        # 0's to a maximum length of 7 digits (needed for max number 60).
        for c in bin(num)[2:].zfill(7):
            if c == "1":
                self.pixels.append((x, self.offset[1] + y))
            x += 1

    def handle_px(self, x, y):
        return (x, y) in self.pixels

class LinesDemo(DemoBase):
    "Lines Demo: run 1 line hor and vert"
    def __init__(self, flipdotdisplay, fps=FPS):
        super().__init__(flipdotdisplay, fps)
        self.t = 0
        self.horizontal = True

    def prepare(self):
        self.t += 1
        maxval = self.fdd.width if self.horizontal else self.fdd.height
        if self.t > maxval:
            self.t = 0
            self.horizontal = not self.horizontal

    def handle_px(self, x, y):
        if self.horizontal:
            return self.t == x
        else:
            return self.t == y

def test_demos():
    import flipdotsim
    fdd = flipdotsim.FlipDotSim()
    demos = [PlasmaDemo(fdd), SwirlDemo(fdd), PingPong(fdd), RandomDot(fdd),
             RotatingPlasmaDemo(fdd), GameOfLife(fdd), # SnakeGame(fdd),
             # FlappyDot(fdd), 
             BinaryClock(fdd), # rogueflip.Game(fdd),
             PygameSurfaceDemo(fdd), LinesDemo(fdd)]
    for demo in demos:
        print(demo)
        demo.run(runtime=2)

    fdd.close()

def main():
    import displayprovider
    import configuration
    fdd = displayprovider.get_display(
        width=configuration.WIDTH, height=configuration.HEIGHT,
        fallback=displayprovider.Fallback.SIMULATOR)

    demos = [PlasmaDemo(fdd), SwirlDemo(fdd), PingPong(fdd), RandomDot(fdd),
             RotatingPlasmaDemo(fdd), GameOfLife(fdd), SnakeGame(fdd),
             FlappyDot(fdd), BinaryClock(fdd), rogueflip.Game(fdd),
             PygameSurfaceDemo(fdd), LinesDemo(fdd)]
    print("\n".join([str(i) + ": " + d.__doc__ for i, d in enumerate(demos)]))
    num = int(input(">"))
    print("Running demo. CTRL-C to abort.")
    demos[num].run()


if __name__ == "__main__":
    main()
