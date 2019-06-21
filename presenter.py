import displayprovider
import flipdotfont

TEXT = [
    "Hallo",
    "Welt",
    "alles",
    "klar",
    "soweit",
    "Sonder",
    "zeichen",
    "öäü ÖÄÜ ß"
]


def main():
    print("Starting Presenter")
    current = 0
    fdd = displayprovider.get_display()
    scroller = flipdotfont.TextScroller(fdd)
    font = flipdotfont.big_font()
    
    while True:
        fdd.clear()
        txt = TEXT[current]
        scroller.text(txt, font)
        # FIXME Error when using y value different from 0
        #scroller.text(bottom, font, start=(0, font.height + 1))
        nexti = (current + 1) % len(TEXT)
        current = nexti
        cmd = input(str(current) + " " + TEXT[current] + " Enter for next, gXX for goto ")
        
        if cmd == 'q':
            exit()
        elif cmd.startswith('g'):
            current = int(cmd[1:])


if __name__ == '__main__':
    main()
