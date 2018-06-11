"""Helper for drawing on pixel display. Taken from
`drawing.py <https://github.com/sprintingkiwi/pycraft_mod/blob/master/mcpipy/drawing.py>`_
and adjusted to the needs of a 2d display.
"""

#
# Code under the MIT license by Alexander Pruss
#

from math import sqrt, floor, ceil, pi
from numbers import Number

class V3(tuple):
    def __new__(cls,*args):
        if len(args) == 1:
            return tuple.__new__(cls,tuple(*args))
        else:
            return tuple.__new__(cls,args)

    def dot(self,other):
        return self[0]*other[0]+self[1]*other[1]+self[2]*other[2]

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        return self[2]

    def __add__(self,other):
        other = tuple(other)
        return V3(self[0]+other[0],self[1]+other[1],self[2]+other[2])

    def __radd__(self,other):
        other = tuple(other)
        return V3(self[0]+other[0],self[1]+other[1],self[2]+other[2])

    def __sub__(self,other):
        other = tuple(other)
        return V3(self[0]-other[0],self[1]-other[1],self[2]-other[2])

    def __rsub__(self,other):
        other = tuple(other)
        return V3(other[0]-self[0],other[1]-self[1],other[2]-self[2])

    def __neg__(self):
        return V3(-self[0],-self[1],-self[2])

    def __pos__(self):
        return self

    def len2(self):
        return self[0]*self[0]+self[1]*self[1]+self[2]*self[2]

    def __abs__(self):
        return sqrt(self.len2())

    def __div__(self,other):
        if isinstance(other,Number):
            y = float(other)
            return V3(self[0]/y,self[1]/y,self[2]/y)
        else:
            return NotImplemented

    def __mul__(self,other):
        if isinstance(other,Number):
            return V3(self[0]*other,self[1]*other,self[2]*other)
        else:
            other = tuple(other)
            # cross product
            return V3(
                self[1]*other[2]-self[2]*other[1],
                self[2]*other[0]-self[0]*other[2],
                self[0]*other[1]-self[1]*other[0])

    def __rmul__(self,other):
        return self.__mul__(other)

    def __repr__(self):
        return "V3"+repr(tuple(self))

    def ifloor(self):
        return V3(int(floor(self[0])),int(floor(self[1])),int(floor(self[2])))

    def iceil(self):
        return V3(int(ceil(self[0])),int(ceil(self[1])),int(ceil(self[2])))


TO_RADIANS = pi / 180.
TO_DEGREES = 180. / pi
ICOS = [1,0,-1,0]
ISIN = [0,1,0,-1]

# Brasenham's algorithm
def getLine(x1, y1, x2, y2):
    line = []
    x1 = int(floor(x1))
    y1 = int(floor(y1))
    z1 = 0 
    x2 = int(floor(x2))
    y2 = int(floor(y2))
    z2 = 0
    point = [x1,y1,z1]
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    x_inc = -1 if dx < 0 else 1
    l = abs(dx)
    y_inc = -1 if dy < 0 else 1
    m = abs(dy)
    z_inc = -1 if dz < 0 else 1
    n = abs(dz)
    dx2 = l << 1
    dy2 = m << 1
    dz2 = n << 1

    if l >= m and l >= n:
        err_1 = dy2 - l
        err_2 = dz2 - l
        for i in range(0,l-1):
            line.append(V3(point[0],point[1],point[2]))
            if err_1 > 0:
                point[1] += y_inc
                err_1 -= dx2
            if err_2 > 0:
                point[2] += z_inc
                err_2 -= dx2
            err_1 += dy2
            err_2 += dz2
            point[0] += x_inc
    elif m >= l and m >= n:
        err_1 = dx2 - m
        err_2 = dz2 - m
        for i in range(0,m-1):
            line.append(V3(point[0],point[1],point[2]))
            if err_1 > 0:
                point[0] += x_inc
                err_1 -= dy2
            if err_2 > 0:
                point[2] += z_inc
                err_2 -= dy2
            err_1 += dx2
            err_2 += dz2
            point[1] += y_inc
    else:
        err_1 = dy2 - n
        err_2 = dx2 - n
        for i in range(0, n-1):
            line.append(V3(point[0],point[1],point[2]))
            if err_1 > 0:
                point[1] += y_inc
                err_1 -= dz2
            if err_2 > 0:
                point[0] += x_inc
                err_2 -= dz2
            err_1 += dy2
            err_2 += dx2
            point[2] += z_inc
    line.append(V3(point[0],point[1],point[2]))
    if point[0] != x2 or point[1] != y2 or point[2] != z2:
        line.append(V3(x2,y2,z2))
    return line


class Drawing:
    TO_RADIANS = pi / 180.
    TO_DEGREES = 180. / pi

    def __init__(self,fdd):
        self.fdd = fdd
        self.width = 1
        self.nib = [(0,0,0)]

    def penwidth(self,w):
        self.width = int(w)
        if self.width == 0:
            self.nib = []
        elif self.width == 1:
            self.nib = [(0,0,0)]
        elif self.width == 2:
            self.nib = []
            for x in range(-1,1):
                for y in range(0,2):
                    for z in range(-1,1):
                        self.nib.append((x,y,z))
        else:
            self.nib = []
            r2 = self.width * self.width / 4.
            for x in range(-self.width//2 - 1,self.width//2 + 1):
                for y in range(-self.width//2 - 1, self.width//2 + 1):
                    for z in range(-self.width//2 -1, self.width//2 + 1):
                        if x*x + y*y + z*z <= r2:
                            self.nib.append((x,y,z))

    def point(self, x, y, on_off):
        for p in self.nib:
            self.fdd.px(x+p[0],y+p[1],on_off)

    def line(self, x1,y1, x2,y2, on_off):
        self.drawPoints(getLine(x1,y1, x2,y2), on_off)

    def drawPoints(self, points, on_off):
        if self.width == 1:
            done = set()
            for p in points:
                if p not in done:
                    self.fdd.px(p.x, p.y, on_off)
                    done.add(p)
        else:
            done = set()
            for p in points:
                for point in self.nib:
                    x0 = p[0]+point[0]
                    y0 = p[1]+point[1]
                    z0 = p[2]+point[2]
                    if (x0,y0,z0) not in done:
                        self.fdd.px(x0,y0,on_off)
                        done.add((x0,y0,z0))
