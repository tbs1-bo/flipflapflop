import time
INFILE = 'gamejamdo_2020-05/iidir/irc.freenode.net/#gamejamdo_fff/out'

# player coordinates
px, py = 5, 5

def get_display():
    import displayprovider
    return displayprovider.get_display()

def get_command():
    with open(INFILE, 'rt') as f:
        ls = f.readlines()
        _timestamp, _user, last_cmd = ls[-1].split(' ')
        print(last_cmd)

    return last_cmd

def process(command):
    global px, py

    if command == 'w': py -= 1
    elif command == 'a': px -= 1
    elif command == 's': py += 1
    elif command == 'd': px += 1

def draw():
    fdd.clear()
    fdd.px(px, py, True)


def main():
    while True:
        last_cmd = get_command()
        process(last_cmd)
        draw()
        time.sleep(1)

fdd = get_display()
main()