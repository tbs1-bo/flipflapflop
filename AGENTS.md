# Was das ist

Software zur Ansteuerung von Flipdot-Anzeigen (elektromechanische
Punktmatrix-Anzeigen) über verschiedene Mikrocontroller/Hosts. Eine
gemeinsame Pixel-Puffer-Abstraktion `DisplayBase` wird von einem
Raspberry-Pi+Arduino-Seriell-Aufbau genutzt. Die Dokumentation
(Sphinx) wird veröffentlicht unter
https://tbs1-bo.github.io/flipflapflop/.

# Deployment

Produktivziel ist ein Raspberry Pi, der als eigener WLAN-Access-Point läuft
und dessen Arduino-gesteuertes Display über seriell angeschlossen ist
(vollständige Topologie siehe `docgen/developer.rst`).

