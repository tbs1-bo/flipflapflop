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
    ECHO = 0b11110000  # Das gesendete Byte wird zurückgesendet.

    def __init__(self, width=4, height=3, buffered=True):
        '''
        Create serial display with given dimension. If buffered is True, all 
        calls to px() will write into an internal buffer until a call to 
        show() will send the data.
        '''
        super().__init__(width, height)
        # TODO add support for auto configuring dimensions
        print('open serial device', DEVICE, BAUD)      
        self.ser = serial.serial_for_url(DEVICE, baudrate=BAUD) # serial.Serial(DEVICE, BAUD)
        self.buffered = buffered        
        self.buffer = [False] * (width * height)

    def px(self, x, y, val):
        assert 0 <= x < self.width
        assert 0 <= y < self.height

        if self.buffered:
            self.buffer[y * self.width + x] = val
        else:
            bs = [SerialDisplay.PXSET if val else SerialDisplay.PXRESET, x, y]
            self.ser.write(bytes(bs))

    def show(self):
        if not self.buffered:
            return

        byte_sequence = [SerialDisplay.PICTURE]
        byte = '0'
        for bit in self.buffer:
            byte += '1' if bit else '0'
            if len(byte) == 8:
                byte_sequence.append(int(byte, base=2))
                byte = '0'

        if len(byte) > 1:
            byte += '0' * (8 - len(byte))
            byte_sequence.append(int(byte, base=2))

        self.ser.write(bytes(byte_sequence))


def demo():
    import demos
    ffd = SerialDisplay(width=configuration.WIDTH, height=configuration.HEIGHT)
    demo = demos.RotatingPlasmaDemo(ffd)
    demo.run()


if __name__ == '__main__':
    demo()