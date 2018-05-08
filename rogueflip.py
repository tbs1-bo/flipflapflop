"""
Rogueflip is a roguelike dungeon crawler for the flipdot display. Levels can
be created as PNM files (ASCII-bases). These can be exported from GIMP. The
player and walls have special color values.

Walls must be black

>>> World.COLOR_WALL
[0, 0, 0]

The player character must be blue.

>>> World.COLOR_PLAYER
[0, 0, 255]

All enemies are red

>>> World.COLOR_ENEMY
[255, 0, 09]

"""

import demos
import random
import time
import pygame

class Game(demos.DemoBase):  # TODO switch from DemoBase to pygame loop 
    """A roguelike for a flipdot display."""

    def __init__(self, flipdotdisplay, worldfile="rogueflip_world.pnm"):
        super().__init__(flipdotdisplay)
        pygame.init()
        self.world = World(worldfile)
        # top left position of current view inside the world
        self.top_left = [0, 0]

        self.player = self.world.find_player()
        self.player.blink_interval = 0.2
        print("Player placed at", self.player.pos)
        self.enemies = self.world.find_enemies()
        print("Found", len(self.enemies), "enemies.")

    def handle_px(self, x, y):
        self.handle_input()
        if self.player.pos == [x, y]:
            # player is blinking
            return self.player.draw()

        for en in self.enemies:
            if en.pos == [x, y]:
                return en.draw()

        else:
            return self.world.is_wall(x, y)

    def prepare(self):
        self.player.tick()
        self.move_enemies()
        for en in self.enemies:            
            en.tick()

    def move_enemies(self):
        for en in self.enemies:
            if en.blink_on:  # only move when visible
                newx, newy = en.pos
                newx += random.randint(-1, 1)
                newy += random.randint(-1, 1)
                if not self.world.is_wall(newx, newy):
                    en.pos = [newx, newy]

    def handle_input(self):
        newx, newy = self.player.pos
        for event in pygame.event.get():
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_w: 
                newy -= 1
            if event.key == pygame.K_a:
                newx -= 1
            if event.key == pygame.K_s:
                newy += 1
            if event.key == pygame.K_d:
                newx += 1

            if not self.world.is_wall(newx, newy):
                self.player.pos = [newx, newy]

class World:
    COLOR_WALL = [0, 0, 0]
    COLOR_PLAYER = [0, 0, 255]
    COLOR_ENEMY = [255, 0, 0]

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

    def is_enemy(self, x, y):
        return self.get_px(x, y) == World.COLOR_ENEMY

    def _find_characters(self, typ):
        chars = []
        for x in range(self.width):
            for y in range(self.height):
                if self.get_px(x, y) == typ:
                    en = Character(x, y)
                    chars.append(en)

        return chars

    def find_player(self):
        return self._find_characters(World.COLOR_PLAYER)[0]

    def find_enemies(self):
        return self._find_characters(World.COLOR_ENEMY)


class Character:
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
