# CLAUDE.md

Diese Datei bietet Claude Code (claude.ai/code) Hinweise für die Arbeit mit dem Code in diesem Repository.

## Was das ist

Software zur Ansteuerung von Flipdot-Anzeigen (elektromechanische
Punktmatrix-Anzeigen) über verschiedene Mikrocontroller/Hosts. Eine
gemeinsame Pixel-Puffer-Abstraktion `DisplayBase` wird von einem
Raspberry-Pi+Arduino-Seriell-Aufbau, einem I²C-Portexpander-Aufbau, einem
ESP8266 (MicroPython), dem Pixelflut/TCP-Netzwerkprotokoll, MQTT, einer
Flask-Web-API sowie einem pygame-/pyxel-/Godot-Simulator genutzt — dieselben
Demos, Fonts und Spiele (`demos.py`, `rogueflip.py`, `flipdotfont.py`) laufen
also unverändert sowohl auf echter Hardware als auch im Simulator. Die
Dokumentation (Sphinx) wird veröffentlicht unter
https://tbs1-bo.github.io/flipflapflop/.

## Setup

Abhängigkeiten werden mit Poetry verwaltet (Python ^3.10).

```bash
poetry install
cp configuration_sample.py configuration.py   # oder: make configuration.py
```

`configuration.py` (in .gitignore, kopiert aus `configuration_sample.py`)
enthält Display-Dimensionen, seriellen Device/Baudrate, I²C-Adresse,
MQTT-Broker und Webserver-Einstellungen — fast jedes Modul importiert es
direkt, daher muss die Datei existieren, bevor irgendetwas ausgeführt wird.

## Häufige Befehle

```bash
./tests.sh                       # Doctests + pytest, wie in CI (siehe unten)
poetry run pytest <file.py> -v   # Tests eines einzelnen Moduls ausführen
                                  # (Tests liegen neben der Implementierung,
                                  # z.B. `pytest web.py`)
poetry run python -m doctest flipdotsim.py   # Doctests in Docstrings

make webserver                   # gunicorn -w1 web:app (nur ein Worker: die
                                  # Display-Verbindung darf nicht doppelt
                                  # aufgebaut werden)
make webserver_test              # pytest web.py + manuelles curl-basiertes
                                  # px-Umschalten
make media/class_diagram.png     # Klassendiagramm mit pyreverse neu erzeugen

cd docgen && make html           # Sphinx-Doku nach docgen/_build/html bauen
                                  # (wird automatisch nach docs/ kopiert und
                                  # via GitHub Pages veröffentlicht)
```

`tests.sh` führt Doctests auf einer festen Dateiliste aus (`flipdotsim.py
flipdotfont.py displayprovider.py net.py rogueflip.py fffmqtt.py`) und
anschließend pytest über alle übrigen `*.py`-Dateien im Repo-Root, außer
`displayserver_service.py`, `flipdotdisplay.py` und `MCP23017.py`
(ausgeschlossen wegen fehlender Hardware-Abhängigkeiten). Tests sind
einfache Funktionen namens `test_*`, die direkt in der jeweiligen
Implementierungsdatei liegen (Pytest-Konvention, kein separates
`tests/`-Verzeichnis) — z.B. enthält `web.py` am Ende `test_display_get`,
`test_page` usw.

CI (`.github/workflows/python-test.yml`) läuft bei Push/PR auf `master`:
installiert die apt-Pakete `mosquitto` und `libsdl2-dev` (für
MQTT-Integrationstests bzw. pygame), dann `poetry run ./tests.sh`.

## Architektur

### Die Display-Abstraktion

Alles läuft über `displayprovider.DisplayBase`: ein Pixel-Puffer mit
`width`/`height`, `px(x, y, val)`, `show()` (Puffer auf das
physische/virtuelle Gerät schreiben), `clear()` und `led(on_off)`. Jedes
konkrete Display — echte Hardware oder simuliert — erbt von dieser Klasse,
und Zeichencode (`demos.py`, `drawing.py`, `flipdotfont.py`, `rogueflip.py`,
`util.py`) ist ausschließlich gegen dieses Interface geschrieben und somit
unabhängig davon, was tatsächlich rendert.

`displayprovider.get_display(width, height, fallback)` ist der zentrale
Einstiegspunkt: zuerst wird versucht, das echte `fffserial.SerialDisplay`
(Arduino über seriell) zu öffnen; schlägt das fehl, greift ein Fallback
gemäß dem `Fallback`-Enum:
- `SIMULATOR` — `flipdotsim.FlipDotSim` (pygame) oder `pyxel_sim.PyxelSim`,
  ausgewählt über `configuration.simulator["implementation"]`
- `REMOTE_DISPLAY` — `net.RemoteDisplay`, leitet Pixel per TCP an einen
  andernorts laufenden `DisplayServer` weiter
- `DUMMY` — reines `DisplayBase` (nur Konsolenausgabe mit `#`/`.`)
- `I2C` — `flipdotdisplay.FlipDotDisplay` (alter Portexpander-Aufbau, wird
  nicht mehr aktiv gepflegt — nur als Referenz vorhanden)

`virtual_display.VirtualDisplay` setzt mehrere kleinere `DisplayBase`-
Instanzen an unterschiedlichen Offsets zu einem größeren logischen Display
zusammen.

### Transport-/Frontend-Schichten auf einem Display

Diese Module kapseln jeweils eine `DisplayBase`-Instanz und stellen sie über
ein anderes Protokoll bereit — keines von ihnen weiß oder kümmert sich
darum, welches konkrete Display dahintersteckt:

- `net.py` — `DisplayServer` (eigenes TCP-Protokoll: pro Pixel ein
  `0`/`1`-Zeichen senden, oder `SIZE` zur Abfrage der Dimensionen;
  Standardport 10101) sowie `PixelflutServer` (implementiert das
  [Pixelflut-Protokoll](https://c3pixelflut.de/how.html): `PX x y color`,
  `SIZE`, `OFFSET x y`). `net.RemoteDisplay` ist die Client-Seite des
  eigenen Protokolls und selbst ein `DisplayBase`, sodass ein Display auf
  einer anderen Maschine wie ein lokales angesteuert werden kann.
- `web.py` — Flask-App mit `/px/<x>/<y>/<on|off>`, `/page` (0/1/x-String in
  Bulk, GET liefert aktuellen Zustand, POST aktualisiert) und `/display`
  (JSON: einzelnes Bild, zeitgesteuerte Bildsequenz, scrollender Text oder
  LED-Steuerung). Start mit `flask --app web.py run` oder `make webserver`
  (gunicorn, muss `-w 1` bleiben).
- `fffmqtt.py` — `Mqtt2Display` abonniert ein MQTT-Topic und rendert
  eingehende 0/1-Strings; veröffentlicht beim Connect Display-Metadaten auf
  einem Info-Topic.
- `fffserial.py` — binäres Kommandoprotokoll (`DIMENSION`, `PICTURE`,
  `PXSET`, `PXRESET`, `ECHO`, `LED_BRIGHTNESS`) zur Arduino-Firmware in
  `hardware/arduino/`.
- `upython/` — ein MicroPython-Port des TCP-Servers/Displays für einen
  ESP8266 (`udisplayserver.py`, `uflipdotdisplay.py`, `uMCP23017.py`,
  `boot.py`); spiegelt `net.DisplayServer`/`flipdotdisplay.py`, jedoch als
  eigenständiger Access Point (`boot.py` startet ein WLAN-AP) statt über
  einen Pi-Host.

### Inhalte/Anwendungen, die auf einem Display gezeichnet werden

- `demos.py` — eine Sammlung von `DemoBase`-Unterklassen (Plasma, Swirl
  usw.), animationsgetriebene Loops per pygame-Clock.
- `flipdotfont.py` — BDF-Font-Laden + `TextScroller` für über das Display
  scrollenden Text.
- `rogueflip.py` — ein Roguelike-Spiel; Level sind Tiled-Karten (`.tmx`),
  geladen mit PyTMX, deren Größe ein Vielfaches der physischen
  Display-Dimensionen ist, sodass das Display als scrollender Ausschnitt
  dient (siehe `ressources/*.tmx`).
- `presenter.py` / `binclock.py` / `clock.py` / `text_scroller.py` /
  `demo_switcher.py` — eigenständige Skripte, die jeweils über
  `displayprovider.get_display()` ein Display holen und direkt ansteuern.
- `godot_client/` und `godot_emu/` — separate Godot-Engine-Simulatoren, die
  das `net.DisplayServer`-Protokoll über TCP sprechen; nicht Teil des
  Python-Pakets.

### Deployment

Produktivziel ist ein Raspberry Pi, der als eigener WLAN-Access-Point läuft
und dessen Arduino-gesteuertes Display über seriell angeschlossen ist
(vollständige Topologie siehe `docgen/developer.rst`).
`deployment/deploy_rpi.sh` richtet einen frischen Pi ein (installiert
poetry, klont das Repo, installiert die systemd-Unit
`flipflapflop.service`, die `displayserver_service.py` startet — ein
`net.DisplayServer`, der im Leerlauf über `binclock.py` eine Uhr anzeigt und
bei Bedarf auf das jeweils Angeforderte umschaltet).
`deployment/deploy_openwrt.sh` / `deployment/openwrt_service.sh` decken
stattdessen ein OpenWRT-basiertes Deployment ab.
