#from  net import RemoteDisplay as FDD
import time
#wt = ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"]
#zeit = wt[int(time.strftime("%w"))]+time.strftime(". %d.%m.%y %X")
#t = time.localtime()
#hour = t[3]
#minute = t[4]
#second = t[5]

#fdd = FDD(host="taylorpi.local", port=10101)


#fff.scrolltext(zeit, fff_big, 3)


class BinClock():
   def __init__(self, fdd):
       self.fdd = fdd
       self.visible = True

   def digit(self, dig, dx, dy):
       pat = [True, True, True, True]*4
       if dig == '1':
          pat = [[False, False, False, False],
                 [False, True, False, False],
                 [False, True, False, False],
                 [False, True, False, False]]
       elif dig == '0':
          pat = [[False, False, False, False],
                 [True, True, True, False],
                 [True, False, True, False],
                 [True, True, True, False]]
       for x in range(4):
           for y in range(4):
               self.fdd.px(4*dx+x, 4*dy+y, pat[y][x])

   def run(self):
       while(True):
           if(self.visible):
               t = time.localtime()
               ihour = t[3]
               imin = t[4]
               isec = t[5]
               bhour = bin(ihour+64)[3:]
               bmin = bin(imin+64)[3:]
               bsec = bin(isec+64)[3:]
               for x in range(6):
                   self.digit(bhour[x], x, 0)
                   self.digit(bmin[x], x, 1)
                   self.digit(bsec[x], x, 2)
               self.fdd.show()
           time.sleep(0.2)

#bc = BinClock(fdd)
#bc.run()
