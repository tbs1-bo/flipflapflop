import pyxel
import displayprovider
import threading

class PyxelSim(displayprovider.DisplayBase):
    def __init__(self, width, height, resources, fps):
        super().__init__(width, height)
        self.fps = fps
        self.resources = resources
        self.yellow_tile_coords = (8,0)
        self.black_tile_coords = (0,8)
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        self.buffer = [[False for x in range(self.width)] for y in range(self.height)]
    
    def run(self):
        pyxel.init(8*self.width, 8*self.height)
        pyxel.load(self.resources)
        pyxel.run(self.update, self.draw)
    
    def update(self):
        pass

    def draw(self):
        pyxel.cls(0)
        for y in range(self.height):
            for x in range(self.width):

                if self.buffer[y][x]:
                    tx, ty = self.yellow_tile_coords
                else:
                    tx, ty = self.black_tile_coords

                pyxel.blt(
                    x * 8, y * 8, 
                    0,
                    ty, tx, 
                    8, 8)

    def px(self, x, y, val):
        self.buffer[y][x] = True if val else False

    def close(self):
        pyxel.quit()


def test_flipdot_sim():
    import time

    fdd = PyxelSim(width=3, height=2, resources="ressources/pyxel_resources.pyxres", fps=30)

    fdd.px(0, 0, True)
    fdd.px(1, 1, True)
    fdd.show()
    time.sleep(0.3)

    fdd.show()
    time.sleep(0.3)

    fdd.clear()
    fdd.show()
    time.sleep(0.3)

    fdd.clear()
    fdd.show()
    time.sleep(0.3)

    fdd.close()

def main():
    PyxelSim(28, 13, "ressources/pyxel_resources.pyxres", fps=30)

if __name__ == "__main__":
    main()