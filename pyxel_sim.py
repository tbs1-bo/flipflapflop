import pyxel
import displayprovider
import threading

class PyxelSim(displayprovider.DisplayBase):
    """
    Simulator for the flipdot display using Pyxel. The simulator will run in a 
    separate thread listening for updates to the display buffer. The display
    buffer is a 2D array of booleans, where True represents a yellow pixel and
    False represents a black pixel.

    https://github.com/kitao/pyxel
    """
    DEFAULT_PYXEL_RESOURCES = "ressources/pyxel_sim.pyxres"

    def __init__(self, width, height, resources=DEFAULT_PYXEL_RESOURCES, fps=30):
        super().__init__(width, height)        
        self.fps = fps
        self.resources = resources
        self.yellow_tile_coords = (8,0)
        self.black_tile_coords = (0,8)
        self.thread = threading.Thread(target=self._run)
        self.thread.start()
        self.buffer = [[False for x in range(self.width)] for y in range(self.height)]
    
    def _run(self):
        'start the pyxel app. This function is called in a separate thread'
        pyxel.init(8*self.width, 8*self.height)
        print(f"loading resources from {self.resources}")
        pyxel.load(self.resources)
        pyxel.run(self.update, self.draw)
    
    def update(self):
        pass

    def draw(self):
        'clear the screen and draw the buffer using images in the resources file.'
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
        'close the simulator'
        pyxel.quit()


def test_flipdot_sim():
    'test the flipdot simulator'
    import time

    fdd = PyxelSim(width=28, height=13)

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
    'start a simulator'
    PyxelSim(28, 13)

if __name__ == "__main__":
    main()