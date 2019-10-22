import pytmx
import flipdotsim
import threading
import time
import configuration
import pygame


WIDTH = configuration.WIDTH
HEIGHT = configuration.HEIGHT

PRESENTATION_FILE = 'ressources/lt19/presentation_lt19.tmx'
DISPLAY_FPS = configuration.simulator['fps']

class Presenter:
    def __init__(self, fdd, tiled_map, fps):
        self.fdd = fdd

        self.tiled_map = tiled_map
        self.offsetx, self.offsety = 0, 0
        self.display_loop_running = False
        self.fps = fps
        self.init_joystick()

    def init_joystick(self):
        pygame.init()
        if pygame.joystick.get_count() == 0:
            print("No Joystick found")
        else:
            print("Joystick found.")
            joy = pygame.joystick.Joystick(0)
            joy.init()

    def run_gui_loop(self):
        self.display_loop_running = True

        clock = pygame.time.Clock()
        while self.display_loop_running:
            self.display()

            for ev in pygame.event.get():
                self.handle_joystick_event(ev)

            clock.tick(self.fps)

        pygame.quit()

    def handle_joystick_event(self, event):
        x_axis = 0
        y_axis = 1

        if event.type == pygame.JOYAXISMOTION:
            if event.axis == x_axis:
                if event.value < 0:
                    self.handle_input('a')
                elif event.value > 0:
                    self.handle_input('d')

            if event.axis == y_axis:
                if event.value < 0:
                    self.handle_input('w')
                elif event.value > 0:
                    self.handle_input('s')

    def display(self):
        for y in range(self.fdd.height):
            for x in range(self.fdd.width):
                x_ = self.offsetx + x
                y_ = self.offsety + y
                if not self.on_map(x_, y_):
                    continue

                tile_props = self.tiled_map.get_tile_properties(x_,y_,layer=0)
                # id 0: black, id 1: yellow
                black = tile_props['id'] == 0
                if black:
                    self.fdd.px(x, y, False)
                else:
                    now = time.time()
                    t = now - int(now)  # removing integer part

                    blink_interval = tile_props['blink_interval']
                    self.fdd.px(x, y, t > blink_interval)

                # Check if object a position
                obj = self.tiled_map.get_object(x_, y_)
                if obj is not None:
                    self.handle_obj(obj)

        self.fdd.show()

    def handle_obj(self, obj: pytmx.TiledObject):
        # TODO handle text nodes
        txt = obj.name
        #print(txt)

    def handle_input(self, userin):
        width, height = self.fdd.width, self.fdd.height
        if userin == 'a' and self.on_map(self.offsetx - width, 0):
            self.offsetx -= width
        elif userin == 'd' and self.on_map(self.offsetx + width, 0):
            self.offsetx += width
        elif userin == 'w' and self.on_map(0, self.offsety - height):
            self.offsety -= height
        elif userin == 's' and self.on_map(0, self.offsety + height):
            self.offsety += height
        elif userin == 'r':
            print("reloading", self.tiled_map.filename)
            self.tiled_map = TiledMap2(self.tiled_map.filename)
        elif userin == 'q':
            self.display_loop_running = False
        elif ',' in userin:
            inx, iny = userin.split(',')
            intx, inty = int(inx), int(iny)
            if self.on_map(intx, inty):
                self.offsetx, self.offsety = intx, inty

        print("drawing@", self.offsetx, self.offsety)
        
    def on_map(self, x, y):
        'check if the coordinates are on the tiled map.'
        return 0 <= x < self.tiled_map.width and \
            0 <= y < self.tiled_map.height

    def run(self):
        th = threading.Thread(target=self.run_gui_loop)
        th.start()

        while self.display_loop_running:
            s = input("wasd rq> ")
            self.handle_input(s)

def test_presenter():
    tiled_map = TiledMap2(PRESENTATION_FILE)
    fdd = flipdotsim.FlipDotSim(width=WIDTH, height=HEIGHT)
    p = Presenter(fdd, tiled_map, DISPLAY_FPS)

    assert not p.on_map(-1, -1)

    for i in "wasdrq":
        print("testing input", i)
        p.handle_input(i)
        p.display()

    fdd.close()

class TiledMap2(pytmx.TiledMap):
    def __init__(self, filename):
        super().__init__(filename)
        self.xy2objects = {}  # maping (x,y) to objects

        for o in self.objects:
            ox, oy = int(o.x), int(o.y)
            #print("Found Object at %s, %s: %s" % (ox, oy, o.name))
            # transform pixel into grid coordinates
            x, y = int(o.x/o.width), int(o.y/o.height)
            self.xy2objects[(x, y)] = o

    def get_object(self, x, y):
        return self.xy2objects.get((x,y))

def test_tiled_map2():
    tm = TiledMap2(PRESENTATION_FILE)
    obj_ = tm.get_object(40, 20)

def main():
    tiled_map = TiledMap2(PRESENTATION_FILE)

    # init display: serial interface or simulator as fallback.
    try:
        import fffserial
        fdd = fffserial.SerialDisplay(
            width=WIDTH, height=HEIGHT,
            serial_device=configuration.flipdotdisplay['serialdevice'],
            baud=configuration.flipdotdisplay['serialbaudrate'])
    except Exception as e:
        print(e, "FALLBACK: Using simulator")
        fdd = flipdotsim.FlipDotSim(width=WIDTH, height=HEIGHT)

    presenter = Presenter(fdd, tiled_map, DISPLAY_FPS)
    presenter.run()


if __name__ == '__main__':
    main()
