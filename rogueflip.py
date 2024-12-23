"""
Rogueflip is a roguelike dungeon crawler for the flipdot display. Levels can
be created with the tiled map editor (https://www.mapeditor.org/) and a corresponding tileset.
"""

import os
import time
import pygame
import flipdotfont
import pytmx  # https://github.com/bitcraft/PyTMX
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

DEFAULT_TMX_WORLD_FILE="ressources/rogueflip_world.tmx"

class Game:
    """A roguelike for a flipdot display."""

    # button to abort the game as defined by pygames joystick
    JOSTICK_ABORT_BUTTON = 8

    def __init__(self, flipdotdisplay, worldfile=DEFAULT_TMX_WORLD_FILE):
        self.fdd = flipdotdisplay
        self.game_running = False
        pygame.init()
        if pygame.joystick.get_count() > 0:
            log.debug(f"{pygame.joystick.get_count()} Joystick(s) found")
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        self.world = World(worldfile)

        # top left position of current view inside the world
        self.window_top_left = [0, 0]

        self.player = self.world.find_player()
        log.debug(f"Player placed at {self.player.pos}")
        self.coins = self.world.find_coins()
        log.debug(f"Found {len(self.coins)} coins.")

        self.fdd = flipdotdisplay
        # default win message shown when all coins are collected
        self.win_message = "you win\nanother game?"
        if self.fdd.height > flipdotfont.big_font().height:
            self.font = flipdotfont.big_font()
        else:
            self.font = flipdotfont.small_font()
        log.debug(f"Using font with letter size {self.font.width}x{self.font.height}")

        self.menu = Menu(self.fdd)

    def run(self):
        """Start the game running in an endless loop."""
        # TODO refactor to update and draw methods to separate concerns

        assert self.world.map.width % self.fdd.width == 0 and \
               self.world.map.height % self.fdd.height == 0, \
               "Width and height of the map must be a multiple of display width and height"

        self.game_running = True
        while self.game_running:
            if self.menu.is_shown:
                self.menu.update()
                self.menu.draw()
            else:
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
                elif event.key == pygame.K_ESCAPE:
                    self.menu.is_shown = True

            elif event.type == pygame.JOYAXISMOTION:
                # handle joystick
                dx = min(1, max(-1, round(self.joystick.get_axis(0))))
                dy = min(1, max(-1, round(self.joystick.get_axis(1))))
            elif event.type == pygame.JOYBUTTONUP:
                if event.button==Game.JOSTICK_ABORT_BUTTON:
                    log.info("game aborted")
                    self.game_running = False
            else:
                # ignore other events
                continue

            if not self.world.is_wall(plx+dx, ply+dy):
                # move player if no wall is in the way
                self.player.pos = [plx + dx, ply + dy]
                self.player_try_collect_coin()
                self.check_win_condition()

            if not self.player_in_window():
                self.move_window(dx, dy)

    def check_win_condition(self):
        """Check if the player has collected all coins and show the win message."""
        if len(self.coins) == 0:
            log.info("All coins collected")
            self.show_win_message()
            self.game_running = False

    def show_win_message(self):        
        self.fdd.clear()
        for word in self.win_message.split('\n'):
            flipdotfont.TextScroller(self.fdd, word, self.font)
            self.fdd.show()
            time.sleep(2)

        # clear events that happened while showing the win message
        pygame.event.clear()

    def player_try_collect_coin(self):
        """Check if the player is on a coin and remove it from the coins list."""
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


class Menu:
    def __init__(self, fdd):
        self.fdd = fdd
        self.font = flipdotfont.big_font()
        self.items = ["Start", "Quit"]
        self.selected = 0
        self.is_shown = True

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.selected = (self.selected - 1) % len(self.items)
                elif event.key == pygame.K_s:
                    self.selected = (self.selected + 1) % len(self.items)

                elif event.key == pygame.K_RETURN:
                    if self.selected == 0:
                        self.is_shown = False
                    else:
                        exit()

    def draw(self):
        self.fdd.clear()
        menu_item = self.items[self.selected]        
        flipdotfont.TextScroller(self.fdd, menu_item, self.font)
        self.fdd.show()


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
        log.debug(f"Loaded map with size {self.map.width} x {self.map.height}")

    def get_type(self, x, y):        
        tile = self.map.get_tile_properties(x, y, self.default_layer)
        assert tile, f"Tile type at {x} {y} must be set in the map."
        return tile['type']

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
        player = self._find_game_objects(World.PLAYER)
        assert len(player) == 1, "More or less than one player found on map."
        return player[0]

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


def test_roguegame():
    import flipdotsim
    import threading
    import pygame.event

    def user_event_generator():
        print("creating events")
        # run to the next screen
        for k in 'waaasssssdssssasssssssssssssdddddddddddddsdddddddd':
            key = ord(k)
            print("posting key event", key)
            pygame.event.post(
                pygame.event.Event(pygame.KEYDOWN, key=key))
            time.sleep(0.08)

        g.game_running = False

    fdd = flipdotsim.FlipDotSim()
    g = Game(fdd, 'ressources/rogueflip_testworld.tmx')

    th = threading.Thread(target=user_event_generator)
    th.start()

    g.run()


def __check_env_var(varname, default_value):
    log.debug(f"checking for {varname} in environment")
    return os.environ.get(varname, default_value)

def main():
    import displayprovider

    log.info("Starting rogueflip")

    fdd = displayprovider.get_display()
    game_world_file = __check_env_var("ROGUEFLIP_WORLD_FILE", DEFAULT_TMX_WORLD_FILE)
    log.debug(f"running with display {fdd.__class__} and world {game_world_file}")
    while True:
        g = Game(fdd, game_world_file)
        g.win_message = __check_env_var("ROGUEFLIP_WIN_MESSAGE", g.win_message)
        g.run()

if __name__ == "__main__":
    main()
