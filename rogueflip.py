"""
Rogueflip is a roguelike dungeon crawler for the flipdot display. Levels can
be created with the tiled map editor (https://www.mapeditor.org/) and a corresponding tileset.
"""

import time
import pygame
import flipdotfont
import pytmx  # https://github.com/bitcraft/PyTMX

DEFAULT_TMX_WORLD_FILE="ressources/rogueflip_world.tmx"

class Game:
    """A roguelike for a flipdot display."""

    def __init__(self, flipdotdisplay, worldfile=DEFAULT_TMX_WORLD_FILE):
        self.fdd = flipdotdisplay
        self.game_running = False
        pygame.init()
        if pygame.joystick.get_count() > 0:
            print("Joystick found")
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        self.world = World(worldfile)

        # top left position of current view inside the world
        self.window_top_left = [0, 0]

        self.player = self.world.find_player()
        print("Player placed at", self.player.pos)
        self.coins = self.world.find_coins()
        print("Found", len(self.coins), "coins.")

        self.fdd = flipdotdisplay
        # default win message shown wjen all coins are collected
        self.win_message = "you win"

    def run(self):
        """Start the game running in an endless loop."""
        assert self.world.map.width % self.fdd.width == 0 and \
               self.world.map.height % self.fdd.height == 0, \
               "Width and height of the map must be a multiple of display width and height"

        self.game_running = True
        while self.game_running:
            self.tick()
            for x in range(self.fdd.width):
                for y in range(self.fdd.height):
                    val = self.handle_px(x, y)
                    self.fdd.px(x, y, val)
            self.fdd.show()

    def handle_px(self, x, y):
        x_, y_ = self.window_top_left[0] + x, self.window_top_left[1] + y
        self.handle_input()
        if self.player.pos == [x_, y_]:
            return self.player.draw()

        for coin in self.coins:
            if coin.pos == [x_, y_]:
                return coin.draw()

        return self.world.is_wall(x_, y_)

    def tick(self):
        self.player.tick()
        for coin in self.coins:            
            coin.tick()

    def handle_input(self):
        """Handle user input from keyboard or joystick."""
        plx, ply = self.player.pos
        dx, dy = 0, 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
                
            if event.type == pygame.KEYDOWN:
                # handle keyboard input
                if event.key == pygame.K_w: 
                    dy = -1
                elif event.key == pygame.K_a:
                    dx = -1
                elif event.key == pygame.K_s:
                    dy = +1
                elif event.key == pygame.K_d:
                    dx = +1

            elif event.type == pygame.JOYAXISMOTION:
                # handle joystick
                dx += round(self.joystick.get_axis(0))
                dy += round(self.joystick.get_axis(1))
            else:
                # ignore other events
                continue

            if not self.world.is_wall(plx+dx, ply+dy):
                self.player.pos = [plx + dx, ply + dy]
                self.player_try_collect_coin()
                if len(self.coins) == 0:
                    self.show_win_message()
                    self.game_running = False

            if not self.player_in_window():
                self.move_window(dx, dy)

    def show_win_message(self):
        font = flipdotfont.big_font()
        for word in self.win_message.split():
            flipdotfont.TextScroller(self.fdd, word, font)
            self.fdd.show()
            time.sleep(2)

    def player_try_collect_coin(self):
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
    WALL = 'wall'
    PLAYER = 'player'
    COIN = 'coin'
    BACK = 'back'

    def __init__(self, worldfile):
        self.pixels = []  # list of tile types
        self.map = pytmx.TiledMap(worldfile)
        self.default_layer = 0
        assert len(self.map.layers) == 1, "Assuming everything in one layer."

    def get_type(self, x, y):
        return self.map.get_tile_properties(x, y, self.default_layer)['type']

    def is_onboard(self, x, y):
        return 0 <= x < self.map.width and 0 <= y < self.map.height

    def is_wall(self, x, y):
        return self.is_onboard(x, y) and self.get_type(x, y) == World.WALL

    def is_player(self, x, y):
        return self.is_onboard(x,y) and self.get_type(x, y) == World.PLAYER

    def is_coin(self, x, y):
        return self.is_onboard(x,y) and self.get_type(x, y) == World.COIN

    def _find_game_objects(self, typ):
        gobjs = []
        for x in range(self.map.width):
            for y in range(self.map.height):
                if self.get_type(x, y) == typ:
                    blink_int = self.map.get_tile_properties(
                        x, y, self.default_layer)['blink_interval']
                    en = GameObject(x, y, blink_int)
                    gobjs.append(en)

        return gobjs

    def find_player(self):
        return self._find_game_objects(World.PLAYER)[0]

    def find_coins(self):
        return self._find_game_objects(World.COIN)


class GameObject:
    def __init__(self, x, y, blink_interval=0.5):
        self.pos = [x, y]
        self.blink_interval = blink_interval
        self.last_updated = time.time()
        self.blink_on = False

    def tick(self):
        """A method that should be invoked each frame."""
        if time.time() - self.last_updated > self.blink_interval:
            self.blink_on = not self.blink_on
            self.last_updated = time.time()

    def draw(self):
        """Determine whether the character should be drawn now."""
        return self.blink_on


def run_simulator():
    print("running a sample game in the simulator")
    import configuration as conf
    import flipdotsim
    fdd = flipdotsim.FlipDotSim(width=conf.WIDTH, height=conf.HEIGHT)
    run_with_flipdotdisplay(fdd)


def run_remote_display():
    print("running a sample game on a remote display")
    import configuration as conf
    import net
    fdd = net.RemoteDisplay(host=conf.remote_display["host"],
        port=conf.remote_display["port"], 
        width=conf.WIDTH, height=conf.HEIGHT)
    run_with_flipdotdisplay(fdd)


def run_with_flipdotdisplay(fdd, gameworld=DEFAULT_TMX_WORLD_FILE):
    print("running with display", fdd.__class__, "and world", gameworld)
    g = Game(fdd, gameworld)
    g.run()


def test_roguegame():
    import flipdotsim
    import threading
    import pygame.event

    def user_event_generator():
        print("creating events")
        # run to the next screen
        for k in 'waaasssssdssssasssssssssssssddddddddd':
            key = ord(k)
            print("posting key event", key)
            pygame.event.post(
                pygame.event.Event(pygame.KEYDOWN, key=key))
            time.sleep(0.1)

        g.game_running = False

    fdd = flipdotsim.FlipDotSim()
    g = Game(fdd, 'ressources/rogueflip_testworld.tmx')

    th = threading.Thread(target=user_event_generator)
    th.start()

    g.run()


if __name__ == "__main__":
    import displayprovider
    while True:
        #game_world_file = "ressources/rogueflip_38c3.tmx"
        fdd = displayprovider.get_display()
        run_with_flipdotdisplay(fdd) #, game_world_file)
