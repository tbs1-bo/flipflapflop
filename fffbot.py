import time
import random

IRC_CHANNEL = '#gamejamdo_staubfaenger'
INFILE = 'gamejamdo_2020-05/iidir/irc.freenode.net/%s/out' % IRC_CHANNEL
OUTFILE = 'gamejamdo_2020-05/iidir/irc.freenode.net/%s/in' % IRC_CHANNEL
OUTFILE_SERVER = 'gamejamdo_2020-05/iidir/irc.freenode.net/in'
BOTUSER = 'fffbot'
NUMBER_OF_PLAYERS = 4
GAMELOOP_SLEEPTIME = 0.1  # seconds

PROCESS_DELAY = 1.5  # seconds
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
            log("eating pill at", x, y, "pills left", len(self.pills))
            self.pills.remove((x, y))
            bot("Staub gefressen. %s Staubpartikel übrig." % len(self.pills))

        if len(self.pills) == 0:
            bot("Glückwunsch!")
            self.init_pills()

    def init_pills(self):
        log("generating pills", self.num_pills)
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
        if 0 <= self.x + dx < self.fdd.width: 
            self.x += dx
        if 0 <= self.y + dy < self.fdd.height: 
            self.y += dy

    def draw(self):
        if time.time() - self.last_change > self.visible_flip_delay:
            self.visible = not self.visible
            self.last_change = time.time()

        self.fdd.px(self.x, self.y, self.visible)

def get_display():
    import displayprovider
    return displayprovider.get_display()

def decode(line):
    '''
    Each regular line is made of a timestamp, a username and a message. 
    Special messages come from the user -!-.
    '''
    fields = line.split(' ')
    if len(fields) != 3:
        return None

    _timestamp, user, last_cmd = fields
    if user == BOTUSER:
        return None
    else:
        return last_cmd.strip()

# TODO Idee: Es gibt jeweils einen Spieler für Norden, Osten, Süden, Westen. Die Spieler, der
# Himmelsrichtung bestimmen über eine Textnachricht die Richtung.
#
def get_command():
    with open(INFILE, 'rt') as f:
        ls = f.readlines()

        i = -1
        count = 0
        wasd = {'w':0, 'a':0, 's':0, 'd':0, '': 0}
        max_vote = ''
        while count < NUMBER_OF_PLAYERS and abs(i) < len(ls):
            last_cmd = decode(ls[i])
            if last_cmd in ('w', 'a', 's', 'd'):
                wasd[last_cmd] += 1
                count += 1
                if wasd[last_cmd] > wasd[max_vote]:
                    max_vote = last_cmd

            i -= 1

    return max_vote

def get_command_old():
    with open(INFILE, 'rt') as f:
        ls = f.readlines()
        fields = ls[-1].split(' ')
        if len(fields) != 3:
            return ""

        _timestamp, _user, last_cmd = fields
        last_cmd = last_cmd.strip()

    return last_cmd

def log(*msgs):
    print(int(time.time()), *msgs)

def process(command):
    global pl, pills

    log("processing", command)

    dx, dy = 0, 0
    if command == 'w': dy -= 1
    elif command == 'a': dx -= 1
    elif command == 's': dy += 1
    elif command == 'd': dx += 1

    pl.move(dx ,dy)
    pills.eat_pill(pl.x, pl.y)

def bot(msg):
    with open(OUTFILE, 'wt') as f:
        f.write(msg + "\n")

def draw():
    global pl, pills

    fdd.clear()
    pl.draw()
    pills.draw()
    fdd.show()

def join_channel(channel):
    log("joining channel", channel)
    with open(OUTFILE_SERVER, 'wt') as f:
        f.write('/JOIN ' + IRC_CHANNEL + '\n')

def main():
    global last_process
    while True:
        if time.time() - last_process > PROCESS_DELAY:
            last_cmd = get_command()
            process(last_cmd)
            last_process = time.time()

        draw()

        time.sleep(GAMELOOP_SLEEPTIME)

join_channel(IRC_CHANNEL)
bot("Friss den Staub. Steuere den Staubfänger mit den Tasten WASD.")
bot("Die letzten %s Eingaben entscheiden über die Richtung." % NUMBER_OF_PLAYERS)
fdd = get_display()
pills = Pills(10, fdd)
pl = Player(fdd)
main()
