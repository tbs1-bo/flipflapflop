import displayprovider
import flipdotfont
import pytmx
import flipdotsim

WIDTH = 28
HEIGHT = 13
presentation_file = 'ressources/presentation.tmx'
fdd = flipdotsim.FlipDotSim(width=WIDTH, height=HEIGHT)

tiled_map = None
offsetx, offsety = 0, 0

def main():
    global tiled_map, offsetx, offsety
    tiled_map = pytmx.TiledMap(presentation_file)

    while True:
        display(offsetx, offsety)
        s = input("> ")
        handle_input(s)


def handle_input(userin):
    global offsetx, offsety

    if userin == 'a' and on_map(offsetx - WIDTH, 0):
        offsetx -= WIDTH
    elif userin == 'd' and on_map(offsetx + WIDTH, 0):
        offsetx += WIDTH
    elif userin == 'w' and on_map(0, offsety - HEIGHT):
        offsety -= HEIGHT
    elif userin == 's' and on_map(0, offsety + HEIGHT):
        offsety += HEIGHT
    elif ',' in userin:
        inx, iny = userin.split(',')
        inx, iny = int(inx), int(iny)
        if on_map(inx, iny):
            offsetx, offsety = inx, iny
    elif userin == 'q':
            exit()

    
def on_map(x, y):
    'check if the coordinates are on the tiled map.'
    return 0 <= x < tiled_map.width and \
           0 <= y < tiled_map.height


def display(offsetx, offsety):
    print("drawing@", offsetx, offsety)
    disp = ''
    for y in range(HEIGHT):
        for x in range(WIDTH):
            x_ = offsetx + x
            y_ = offsety + y
            if on_map(x_, y_):
                # id 0: black, id 1: yellow
                yellow = tiled_map.get_tile_properties(
                    x_,y_,0)['id'] == 1
                fdd.px(x,y,yellow)
                disp += '*' if yellow else '.'
        disp += '\n'

    print(disp)
    fdd.show()


if __name__ == '__main__':
    main()
