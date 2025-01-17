"""
Displaymodul that provides access to different kinds of displays.

Different fallback strategies are available if the hardware display is not
available.

"""
import enum
import configuration

class Fallback(enum.Enum):
    SIMULATOR = "simulator"
    REMOTE_DISPLAY = "remote_display"
    DUMMY = "dummy"
    I2C = "i2c"


class DisplayBase:
    """All displays must conform to the attributes and methods specified in
    this class."""
    def __init__(self, width=4, height=3):
        self.width = width
        self.height = height

    def px(self, x, y, val):
        pass

    def show(self):
        pass

    def clear(self):
        "Set all pixels to false."
        for x in range(self.width):
            for y in range(self.height):
                self.px(x, y, False)

    def led(self, on_off):
        "Turn LED of the display on (True) or off (False)"
        pass

def get_display(width=configuration.WIDTH, height=configuration.HEIGHT, fallback=Fallback.SIMULATOR):
    print("Creating display with width", width, "and height", height)
    try:
        import fffserial
        return fffserial.SerialDisplay(
            width=width, height=height, 
            serial_device=configuration.flipdotdisplay['serialdevice'],
            baud=configuration.flipdotdisplay['serialbaudrate'],
            buffered=configuration.flipdotdisplay['buffered'])

    except Exception as e:
        print("Unable to create FlipDotDisplay:", e,
              "\nFalling back to", fallback)

        if fallback == Fallback.SIMULATOR:
            fps = configuration.simulator['fps']
            impl = configuration.simulator.get('implementation', 'pygame')
            print("Using simulator with", impl, "implementation and", fps, "fps")
            if impl == "pygame":
                import flipdotsim
                return flipdotsim.FlipDotSim(width, height, fps)
            elif impl == "pyxel":
                import pyxel_sim
                return pyxel_sim.PyxelSim(width, height, fps=fps)

        elif fallback == Fallback.REMOTE_DISPLAY:
            import net
            return net.RemoteDisplay(width=width, height=height)

        elif fallback == Fallback.DUMMY:
            return DisplayBase(width=width, height=height)

        elif fallback == Fallback.I2C:
            import flipdotdisplay
            return flipdotdisplay.FlipDotDisplay(width=width, height=height)

        else:
            raise Exception("No display and no fallback!")


