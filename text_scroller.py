import displayprovider
import flipdotfont
import time


def main():
    fdd = displayprovider.get_display()
    font = flipdotfont.small_font()
    txt = "39C3 Power Cycles - Das Labor - Bochum - :)     "

    txt_scrl = flipdotfont.TextScroller(fdd, txt, font)

    while True:
        txt_scrl.scrolltext()
        txt_scrl.fdd.show()
        time.sleep(0.05)


if __name__ == "__main__":
    main()

