import displayprovider
import flipdotfont
import pytmx
import flipdotsim
import threading
import time
import configuration

WIDTH = configuration.WIDTH
HEIGHT = configuration.HEIGHT
presentation_file = 'ressources/presentation.tmx'
fdd = flipdotsim.FlipDotSim(width=WIDTH, height=HEIGHT)

DISPLAY_WAIT_TIME = 1 / configuration.simulator['fps']

tiled_map = None
offsetx, offsety = 0, 0
display_loop_running = False

def main():
    global tiled_map, offsetx, offsety
    tiled_map = pytmx.TiledMap(presentation_file)
    th = threading.Thread(target=run_display_loop)
    th.start()

    while True:
        s = input("wasd rq> ")
        handle_input(s)

def run_display_loop():
    global offsetx, offsety, display_loop_running

    display_loop_running = True

    while display_loop_running:
        display(offsetx, offsety)
        time.sleep(DISPLAY_WAIT_TIME)

def handle_input(userin):
    global offsetx, offsety, display_loop_running, tiled_map

    if userin == 'a' and on_map(offsetx - WIDTH, 0):
        offsetx -= WIDTH
    elif userin == 'd' and on_map(offsetx + WIDTH, 0):
        offsetx += WIDTH
    elif userin == 'w' and on_map(0, offsety - HEIGHT):
        offsety -= HEIGHT
    elif userin == 's' and on_map(0, offsety + HEIGHT):
        offsety += HEIGHT
    elif userin == 'r':
        print("reloading", presentation_file)
        tiled_map = pytmx.TiledMap(presentation_file)
    elif userin == 'q':
        display_loop_running = False
        exit()
    elif ',' in userin:
        inx, iny = userin.split(',')
        intx, inty = int(inx), int(iny)
        if on_map(intx, inty):
            offsetx, offsety = intx, inty

    print("drawing@", offsetx, offsety)
    
def on_map(x, y):
    'check if the coordinates are on the tiled map.'
    return 0 <= x < tiled_map.width and \
           0 <= y < tiled_map.height


def display(offsetx, offsety):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            x_ = offsetx + x
            y_ = offsety + y
            if not on_map(x_, y_):
                continue

            tile_props = tiled_map.get_tile_properties(x_,y_,layer=0)
            # id 0: black, id 1: yellow
            black = tile_props['id'] == 0
            if black:
                fdd.px(x, y, False)
            else:
                now = time.time()
                t = now - int(now)  # removing integer part

                blink_interval = tile_props['blink_interval']
                fdd.px(x, y, t > blink_interval)

    fdd.show()


if __name__ == '__main__':
    main()
