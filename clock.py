"""Demo of an analog clock.

The code is based on 
`clock.py <https://github.com/sprintingkiwi/pycraft_mod/blob/master/mcpipy/clock.py>`_

A demo video is available on 
`YouTube <https://www.youtube-nocookie.com/embed/2X3LfF__rnQ?rel=0>`_

"""

#
# Code under the MIT license by Alexander Pruss
#

from drawing import Drawing
from math import pi, sin, cos
import time
import displayprovider
import configuration as conf

fdd = displayprovider.get_display(conf.WIDTH, conf.HEIGHT)
d = Drawing(fdd)
d.penwidth(1)

class Hand:
    def __init__(self, center, scale, length):
        self.center = center
        self.length = length
        self.scale = scale
        self.previousValue = None

    def update(self, value):
        if self.previousValue is not None and self.previousValue is not value:
            self.drawLine(self.previousValue, True)
        self.drawLine(value, False)
        self.previousValue = value

    def drawLine(self, value, on_off):
        angle = pi / 2 - (value % self.scale) * 2 * pi / self.scale
        angle = -angle
        d.line(
            self.center[0],
            self.center[1],             
            self.center[0] + self.length * cos(angle),
            self.center[1] + self.length * sin(angle),
            on_off)

radius = min(fdd.width, fdd.height) // 2
center = (fdd.width // 2, fdd.height // 2)


for x in range(-radius, radius+1):
    for y in range(-radius, radius+1):
        if x**2+y**2 <= radius**2:
            d.point(center[0]+x, center[1]+y, True)


"""
for tick in range(0,12):
    d.line(
        center[0]+0.85*radius*cos(tick * 2 * pi / 12),
        center[1]+0.85*radius*sin(tick * 2 * pi / 12),         
        center[0]+radius*cos(tick * 2 * pi / 12),
        center[1]+radius*sin(tick * 2 * pi / 12), 
        True)
"""

hourHand = Hand(center, 12, radius * 0.5)
minuteHand = Hand(center, 60, radius * 0.8)
secondHand = Hand(center, 60, radius * 0.8) 

def main():
    while True:
        t = time.localtime()
        hourHand.update(t[3])
        minuteHand.update(t[4])
        secondHand.update(t[5])
        fdd.show()
        time.sleep(1)

if __name__ == '__main__':
    main()
