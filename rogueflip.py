"""
Rogueflip is a roguelike dungeon crawler for the flipdot display. Levels can
be created as PNM files (ASCII-bases). These can be exported from GIMP. The
player, coins and walls have special color values described below.

The special color values of the image format follow:

Walls must be black

>>> World.COLOR_WALL
[0, 0, 0]

The player character must be blue.

>>> World.COLOR_PLAYER
[0, 0, 255]

All coins are yellow

>>> World.COLOR_COIN
[255, 255, 0]

"""

import demos
import time
import pygame

DEFAULT_WORLD_FILE="ressources/rogueflip_world.pnm"

class Game(demos.DemoBase):  # TODO switch from DemoBase to pygame loop 
    """A roguelike for a flipdot display."""

    def __init__(self, flipdotdisplay, worldfile=DEFAULT_WORLD_FILE):
        super().__init__(flipdotdisplay)
        pygame.init()
        self.world = World(worldfile)
        # top left position of current view inside the world
        self.window_top_left = [0, 0]

        self.player = self.world.find_player()
        self.player.blink_interval = 0.2
        print("Player placed at", self.player.pos)
        self.coins = self.world.find_coins()
        print("Found", len(self.coins), "coins.")

    def handle_px(self, x, y):
        x_, y_ = self.window_top_left[0] + x, self.window_top_left[1] + y
        self.handle_input()
        if self.player.pos == [x_, y_]:
            # player is blinking
            return self.player.draw()

        for coin in self.coins:
            if coin.pos == [x_, y_]:
                return coin.draw()

        return self.world.is_wall(x_, y_)

    def prepare(self):
        self.player.tick()
        for coin in self.coins:            
            coin.tick()

    def handle_input(self):
        newx, newy = self.player.pos
        dx, dy = 0, 0
        for event in pygame.event.get():
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_w: 
                dy = -1
            elif event.key == pygame.K_a:
                dx = -1
            elif event.key == pygame.K_s:
                dy = +1
            elif event.key == pygame.K_d:
                dx = +1

            if not self.world.is_wall(newx+dx, newy+dy):
                self.player.pos = [newx+dx, newy+dy]
                self.player_try_collect_coin()
            if not self.player_in_window():
                self.move_window(dx, dy)

    def player_try_collect_coin(self):
        x, y = self.player.pos
        # remove coin under player
        self.coins = [c for c in self.coins if c.pos != self.player.pos]

    def player_in_window(self):
        """Check if the player is inside the windows."""
        wtlx, wtly = self.window_top_left
        px, py = self.player.pos        

        hor_inside = wtlx <= px < wtlx + self.fdd.width
        ver_inside = wtly <= py < wtly + self.fdd.height

        return hor_inside and ver_inside

    def move_window(self, dx, dy):
        """Move the visible window by the amount of dx*width and dy*height of
        the flipdotdisplay."""
        self.window_top_left[0] += self.fdd.width * dx
        self.window_top_left[1] += self.fdd.height * dy


class World:
    COLOR_WALL = [0, 0, 0]
    COLOR_PLAYER = [0, 0, 255]
    COLOR_COIN = [255, 255, 0]

    def __init__(self, worldfile):
        self.pixels = []  # list of color values (r,g,b)
        self.width = 0
        self.height = 0
        self.load_world(worldfile)

    def load_world(self, file):
        """Load world from file. The file has to be a PNM-Image file. A wall 
        is marked with a black, the player with a blue pixel."""
        print("Loading world", file)

        with open(file) as f:
            firstline = f.readline().strip()
            if firstline != "P3":
                raise Exception("Wrong file format" + str(file))
            px = []
            line = f.readline()
            while line:
                if line.startswith("#"):
                    line = f.readline()
                    continue
                if " " in line:
                    # dimension found
                    w, h = line.strip().split(' ')
                    print("dimension found", w, h)
                    self.width, self.height = int(w), int(h)
                    # consume next line (max brightness)
                    f.readline()

                else:
                    # color value found
                    px.append(int(line.strip()))
                    if len(px) >= 3:
                        self.pixels.append(px)
                        px = []

                line = f.readline()

        assert len(px) == 0, "Number of color values no multiple of 3!"
        assert len(self.pixels) == self.width * self.height

    def get_px(self, x, y):
        return self.pixels[self.width * y + x]

    def is_wall(self, x, y):
        return self.get_px(x, y) == World.COLOR_WALL

    def is_player(self, x, y):
        return self.get_px(x, y) == World.COLOR_PLAYER

    def is_coin(self, x, y):
        return self.get_px(x, y) == World.COLOR_COIN

    def _find_game_objects(self, typ):
        chars = []
        for x in range(self.width):
            for y in range(self.height):
                if self.get_px(x, y) == typ:
                    en = GameObject(x, y)
                    chars.append(en)

        return chars

    def find_player(self):
        return self._find_game_objects(World.COLOR_PLAYER)[0]

    def find_coins(self):
        return self._find_game_objects(World.COLOR_COIN)


class GameObject:
    def __init__(self, x, y, blink_interval=0.5):
        self.pos = [x, y]
        self.blink_interval = blink_interval
        self.last_updated = time.time()
        self.blink_on = False

    def tick(self):
        if time.time() - self.last_updated > self.blink_interval:
            self.blink_on = not self.blink_on
            self.last_updated = time.time()

    def draw(self):
        """Determine whether the character should be drawn now."""
        return self.blink_on