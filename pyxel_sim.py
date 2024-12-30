import pyxel
import displayprovider
import threading

class PyxelSim(displayprovider.DisplayBase):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.fps = 60
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        self.buffer = [[0 for x in range(self.width)] for y in range(self.height)]
    
    def run(self):
        pyxel.init(self.width, self.height)
        pyxel.run(self.update, self.draw)
    
    def update(self):
        pass

    def draw(self):
        pyxel.cls(0)
        for y in range(self.height):
            for x in range(self.width):
                pyxel.pset(x, y, self.buffer[y][x])

    def px(self, x, y, val):
        self.buffer[y][x] = 7 if val else 0

    def show(self):
        pass

def main():
    PyxelSim(28, 13)

if __name__ == "__main__":
    main()