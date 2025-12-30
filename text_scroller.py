import displayprovider
import flipdotfont
import time

fdd = displayprovider.get_display()
font = flipdotfont.small_font()
txt = "39C3 Power Cycles - Das Labor - Bochum - :)     "

txt_scrl = flipdotfont.TextScroller(fdd, txt, font)

while True:
    txt_scrl.scrolltext()
    time.sleep(0.01)

