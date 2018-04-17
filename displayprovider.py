"""
Displaymodul that provides access to different kinds of displays.

Different fallback strategies are available if the hardware display is not
available.

"""
import enum


class Fallback(enum.Enum):
    SIMULATOR = "simulator"
    REMOTE_DISPLAY = "remote_display"
    DUMMY = "dummy"


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

    def show2(self):
        """Optional method that may be implemented. Will be removed in the
        future."""
        pass


def get_display(width=28, height=13, fallback=Fallback.SIMULATOR):
    try:
        import flipdotdisplay
        return flipdotdisplay.FlipDotDisplay(width=width, height=height)

    except ImportError as e:
        print("Unable to create FlipDotDisplay:", e,
              "\nFalling back to", fallback.name)

        if fallback == Fallback.SIMULATOR:
            import flipdotsim
            return flipdotsim.FlipDotSim(width=width, height=height)

        elif fallback == Fallback.REMOTE_DISPLAY:
            import net
            return net.RemoteDisplay(width=width, height=height)

        elif fallback == Fallback.DUMMY:
            return DisplayBase(width=width, height=height)

        else:
            raise Exception("No display and no fallback!")


