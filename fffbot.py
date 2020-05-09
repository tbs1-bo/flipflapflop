import time
import random
INFILE = 'gamejamdo_2020-05/iidir/irc.freenode.net/#gamejamdo_fff/out'

GAMELOOP_SLEEPTIME = 0.1

PROCESS_DELAY = 1
last_process = time.time()

class Pills:
    def __init__(self, num, fdd):
        self.fdd = fdd
        self.pills = []
        self.num_pills = num
        self.init_pills()

    def draw(self):
        for x, y in self.pills:
            self.fdd.px(x, y, True)

    def eat_pill(self, x, y):
        'eating pill if at (x,y)'
        if (x, y) in self.pills:
            print("eating pill at", x, y, "pills left", len(self.pills))
            self.pills.remove((x, y))

        if len(self.pills) == 0:
            self.init_pills()

    def init_pills(self):
        print("generating pills", self.num_pills)
        while len(self.pills) < self.num_pills:
            randx = random.randint(0, self.fdd.width - 1)
            randy = random.randint(0, self.fdd.height - 1)
            if (randx, randy) not in self.pills:
                self.pills.append((randx, randy))


class Player:
    def __init__(self, fdd):
        self.fdd = fdd
        self.x = fdd.width // 2
        self.y = fdd.height // 2
        self.visible = True
        self.last_change = time.time()
        self.visible_flip_delay = 0.1

    def move(self, dx, dy):
        if self.x + dx < self.fdd.width and self.x + dx >= 0: 
            self.x += dx
        if self.y + dy < self.fdd.height and self.y + dy >= 0: 
            self.y += dy

    def draw(self):
        if time.time() - self.last_change > self.visible_flip_delay:
            self.visible = not self.visible
            self.last_change = time.time()

        self.fdd.px(self.x, self.y, self.visible)

def get_display():
    import displayprovider
    return displayprovider.get_display()

def get_command(bestof=3):
    with open(INFILE, 'rt') as f:
        ls = f.readlines()

        lines = ls[-bestof:]
        wasd = {'w':0, 'a':0, 's':0, 'd':0}
        best = 'w'
        for line in lines:
            fields = line.split(' ')
            if len(fields) != 3:
                continue

            _timestamp, _user, last_cmd = fields
            last_cmd = last_cmd.strip()
            if last_cmd in ('w', 'a', 's', 'd'):
                wasd[last_cmd] += 1
                if wasd[last_cmd] > wasd[best]:
                    best = last_cmd

    #print("wasd", wasd, "best", best)
    return best


def get_command_old():
    with open(INFILE, 'rt') as f:
        ls = f.readlines()
        fields = ls[-1].split(' ')
        if len(fields) != 3:
            return ""

        _timestamp, _user, last_cmd = fields
        last_cmd = last_cmd.strip()

    return last_cmd

def process(command):
    global pl, pills

    print("processing", command)
    dx, dy = 0, 0
    if command == 'w': dy -= 1
    elif command == 'a': dx -= 1
    elif command == 's': dy += 1
    elif command == 'd': dx += 1

    pl.move(dx ,dy)
    pills.eat_pill(pl.x, pl.y)

def draw():
    global pl, pills

    fdd.clear()
    pl.draw()
    pills.draw()
    fdd.show()

def main():
    global last_process
    while True:
        last_cmd = get_command()

        if time.time() - last_process > PROCESS_DELAY:
            process(last_cmd)
            last_process = time.time()

        draw()

        time.sleep(GAMELOOP_SLEEPTIME)

fdd = get_display()
pills = Pills(10, fdd)
pl = Player(fdd)
main()
