'''
Module for communicating with the display using a serial interface. The display
is connected to an arduino. This packages helps during the
communication with the device over a serial interface.
'''

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

    def __init__(self, width=4, height=3, serial_device="/dev/ttyUSB0", baud=9600, buffered=True):
        '''
        Create serial display with given dimension. If buffered is True, all 
        calls to px() will write into an internal buffer until a call to 
        show() will send the data.
        '''
        # coordinate information must fit into 7 Bit!
        assert width < 128 and height < 128, "Serial display dimension is too big!"
        super().__init__(width, height)
        # TODO add support for auto configuring dimensions
        print('open serial device', serial_device)      
        self.ser = serial.serial_for_url(serial_device, baudrate=baud, timeout=1)
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
        'Send the content of the buffer to the display using serial interface.'

        if not self.buffered:
            # ignoring invocation.
            return

        byte_sequence = [SerialDisplay.PICTURE]
        byte = '0' # Databytes start with 0
        for bit in self.buffer:
            byte += '1' if bit else '0'
            if len(byte) == 8:
                byte_sequence.append(int(byte, base=2))
                byte = '0'

        if len(byte) > 1:
            byte += '0' * (8 - len(byte))
            byte_sequence.append(int(byte, base=2))

    def close(self):
        'Close the serial device'
        self.ser.close()

def demo_simple():
    ffd = SerialDisplay(width=28, height=13, serial_device=DEVICE, baud=BAUD, buffered=False)
    print("sending pixel")
    ffd.px(1, 2, False)
    ffd.close()

def demo():
    import demos
    ffd = SerialDisplay(width=configuration.WIDTH, height=configuration.HEIGHT, 
                        serial_device=DEVICE, baud=BAUD, buffered=True)
    demo = demos.RotatingPlasmaDemo(ffd)
    try:
        demo.run()
    except KeyboardInterrupt:
        ffd.close()

if __name__ == '__main__':
    #demo()
    demo_simple()
