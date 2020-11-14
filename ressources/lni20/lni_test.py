from urllib.request import urlopen
from time import sleep, time

API = 'http://flipflapflop.online/page'
width, height = 28, 13

def test_plasmademo():
    from math import sin, cos

    ticks = 0
    xmax, ymax = 7, 7
    while True:
        payload = 'data='
        for y in range(height):
            for x in range(width):
                ticks += 0.001
                s = sin(ticks / 50.0) * 2.0 + 6.0
                v = 0.3 + (0.3 * sin((x * s) + ticks / 4.0) *
                        cos((y * s) + ticks / 4.0))
                show_px = v > 0.3
                if x < xmax and y < ymax:
                    px = '1' if show_px else '0'
                else:
                    px = 'x'
                payload += px

        urlopen(API, data=payload.encode())
        sleep(0.1)

def walking_dot():
    import random
    import time
    px, py = 5, 5
    dirs = [
        (0, -1), (1,0), (0,1), (-1,0)
    ]
    dir = 0

    while True:
        if random.randint(0, 5) == 1:
            dir = (dir + 1) % len(dirs)
        dx, dy = dirs[dir]
        px_new, py_new = px + dx, py + dy
        if px_new < 0  or py_new < 0 or px_new >= width or py_new >= height:
            continue

        print(px, py)
        payload = 'data='
        for y in range(height):
            for x in range(width):
                if px == x and py == y:
                    payload += '0'
                elif px_new == x and py_new == y:
                    payload += '1'
                else:
                    payload += 'x'

        px, py = px_new, py_new
        urlopen(API, data=payload.encode())
        time.sleep(0.5)

#test_plasmademo()
walking_dot()
print('finished')
