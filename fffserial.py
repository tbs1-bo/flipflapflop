import serial  # pip install pyserial
import displayprovider
import configuration

DEVICE = configuration.flipdotdisplay["serialdevice"]
BAUD = configuration.flipdotdisplay["serialbaudrate"]

class SerialDisplay(displayprovider.DisplayBase):
    DIMENSION = 0b10010000 # Es folgen zwei Bytes mit BREITE und HÖHE.
    PICTURE = 0b10000001 # Es folgen Breite*Höhe Datenbits (zeilenweise)

    PXSET = 0b10000011  # Es folgen zwei Bytes X, Y mit Positionsinformationen 
    PXRESET = 0b10000010 # Es folgen zwei Bytes X, y mit Positionsinformationen 
    ECHO = 0b11110000  # Das gesendet Byte wird zurückgesendet.

    def __init__(self, width=4, height=3):
        super().__init__(width, height)
        # TODO add support for auto configuring dimensions
        print('open serial device', DEVICE, BAUD)      
        self.ser = serial.Serial(DEVICE, BAUD)

    def px(self, x, y, val):
        # TODO add support for buffered operation
        assert 0 <= x <= 255
        assert 0 <= y <= 255

        bs = [SerialDisplay.PXSET if val else SerialDisplay.PXRESET, x, y]
        self.ser.write(bytes(bs))

    def show(self):
        # TODO
        pass


def demo():
    import demos
    ffd = SerialDisplay(width=configuration.WIDTH, height=configuration.HEIGHT)
    demo = demos.RotatingPlasmaDemo(ffd)
    demo.run()


if __name__ == '__main__':
    demo()