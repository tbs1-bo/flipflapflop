import pygame
from demos import PlasmaDemo, RotatingPlasmaDemo, SwirlDemo, PingPong, RandomDot, GameOfLife

class DemoSwitcher:
    'Run a series of demos and switch between them using keyboard or joystick'
    def __init__(self, demos):
        print("Starting demo switcher")
        self.demos = demos
        self.current_demo = 0
        self.fps = 30
        # check for joystick
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        else:
            print("no joystick found")

    def run(self):
        clock = pygame.time.Clock()
        print("running fps", self.fps)
        while True:
            clock.tick(self.fps)
            delta_index = self.handle_input()
            if delta_index != 0:
                self.current_demo = (self.current_demo + delta_index) % len(self.demos)
                print("Running demo:", self.current_demo)

            demo = self.demos[self.current_demo]
            demo.one_cycle()

    def handle_input(self):
        dx = 0
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    dx = 1 
                elif event.key == pygame.K_a:
                    dx = -1
            elif event.type == pygame.JOYAXISMOTION:
                # handle joystick
                dx = min(1, max(-1, round(self.joystick.get_axis(0))))
            else:
                # ignore other events
                continue

        return dx

def main():
    import displayprovider
    import configuration
    fdd = displayprovider.get_display(
        width=configuration.WIDTH, height=configuration.HEIGHT,
        fallback=displayprovider.Fallback.SIMULATOR)

    demos = [PlasmaDemo(fdd), RotatingPlasmaDemo(fdd), SwirlDemo(fdd), PingPong(fdd), 
        RandomDot(fdd), GameOfLife(fdd)]
    ds = DemoSwitcher(demos)
    ds.run()


if __name__ == "__main__":
    main()
