# webdemo

Eine eigenständige, rein clientseitige Demo-Webseite für eine virtuelle
Flipdot-Anzeige. Sie benötigt keinen Server, keinen Build-Schritt und keine
Python-Abhängigkeiten – nur `index.html`, die auf HTML5 Canvas und
Vanilla-JS basiert.

Die Demos (Plasma, Moire, Rotating Plasma, Swirl, PingPong, Random Dots,
Game of Life, Binary Clock, Lines) sind 1:1-Portierungen der
entsprechenden `DemoBase`-Unterklassen aus `../demos.py`. Nicht enthalten
sind Demos, die pygame-Events, Fonts/Bilder oder Joystick-Eingaben
benötigen (`SnakeGame`, `FlappyDot`, `PygameSurfaceDemo`, `rogueflip`).

## Nutzen

Einfach `index.html` im Browser öffnen, oder das Verzeichnis mit einem
beliebigen statischen Webserver ausliefern, z.B.:

```bash
python -m http.server --directory webdemo 8000
```

oder als eigene Seite über GitHub Pages, Netlify, o.ä. veröffentlichen.
