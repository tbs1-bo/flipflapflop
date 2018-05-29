"""
This version of the MCP23017 Portexpander is a port for micropython and can
be used on an ESP8266 or similar platforms.

It uses the I²C protocol. The micropython API for I²C is described here
http://docs.micropython.org/en/latest/esp8266/library/machine.I2C.html

"""

import machine
from machine import I2C


class Portexpander:
    """
    A Portexpander using up to 16 IO-Pins organised in 2 Banks A und B. Each
    pin-number ranges from 0 to 7.

    reg    add |bit
    name   0x  |7  6   5   4   3   2   1   0   default
    ---------------------------------------------------
    IODIRA 00  IO7 IO6 IO5 IO4 IO3 IO2 IO1 IO0 1111 1111   0=out,1=in
    IODIRB 01  IO7 IO6 IO5 IO4 IO3 IO2 IO1 IO0 1111 1111   0=out,1=in
    GPIOA  12  GP7 GP6 GP5 GP4 GP3 GP2 GP1 GP0 0000 0000
    GPIOB  13  GP7 GP6 GP5 GP4 GP3 GP2 GP1 GP0 0000 0000
    OLATA  14  OL7 OL6 OL5 OL4 OL3 OL2 OL1 OL0 0000 0000
    OLATB  15  OL7 OL6 OL5 OL4 OL3 OL2 OL1 OL0 0000 0000

    Registers to configure in/out for bank A/B
    IODIRA = 0x00
    IODIRB = 0x01

    Registers to read from Bank A/B
    GPIOA = 0x12
    GPIOB = 0x13

    Registers to output on Bank A/B
    OLATA = 0x14
    OLATB = 0x15
    """

    def __init__(self, i2c_address, sda, scl):
        self.i2c_address = i2c_address
        self.smbus = I2C(scl=machine.Pin(scl), sda=machine.Pin(sda))
        # configure default registers
        self._regs = {'conf': {'A': 0x00, 'B': 0x01},
                      'input': {'A': 0x12, 'B': 0x13},
                      'output': {'A': 0x14, 'B': 0x15}}

    def config_inout(self, bankab, value):
        assert bankab in ['A', 'B']
        reg = self._regs['conf'][bankab]
        self.smbus.writeto_mem(self.i2c_address, reg, bytearray([value]))

    def write_value(self, bankab, value):
        assert bankab in ['A', 'B']
        reg = self._regs['output'][bankab]
        self.smbus.writeto_mem(self.i2c_address, reg, bytearray([value]))

    def read_value(self, bankab):
        assert bankab in ['A', 'B']
        reg = self._regs['input'][bankab]
        return self.smbus.readfrom_mem(self.i2c_address, reg)[0]

    def input(self, bankab, pin):
        assert bankab in ['A', 'B']
        assert pin in range(8)
        reg_value = self.read_value(bankab)
        return (reg_value & 2**pin) == 2**pin

    def output(self, bankab, pin, value):
        assert bankab in ['A', 'B']
        assert pin in range(8)
        assert value in [True, False]
        old_value = self.read_value(bankab)
        if value:
            new_value = old_value | (2**pin)
        else:
            new_value = old_value & ~(2**pin)
        self.write_value(bankab, new_value)
