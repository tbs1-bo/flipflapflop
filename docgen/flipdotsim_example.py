import flipdotsim
import time

# Create a Simulator with the given dimension
display = flipdotsim.FlipDotSim(width=16, height=8)

# turn some pixels on in the top left corner
display.px(0, 0, True)
display.px(1, 0, True)
display.px(0, 1, True)
# The display will not change until the show method is invoked
display.show()
time.sleep(2)

# Lets run one dot from top left to bottom right
for y in range(display.height):
   for x in range(display.width):
       display.px(x, y, True)
       display.show()
       time.sleep(0.1)
       display.px(x, y, False)
