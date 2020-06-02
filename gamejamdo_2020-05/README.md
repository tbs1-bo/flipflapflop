Flipflapflop Display für den Gamejam
====================================

Ein Flipdot-Display, welches sich über einen Chat steuern lässt.
Wir haben für einen GameJam ein Spiel darauf umgesetzt, welches über
einen IRC-Chat kontrolliert wird. Es geht darum Staubkörner in Form
von blinkenden Dots einzusammeln. Die Mehrzahl der Eingabe im Chat
entscheidet über den jeweils nächsten Zug. 

Mit `make connect` wird ein IRC-Bot in `iidir` gestartet,
der sich über Dateien auslesen und steuern lässt.
In `fffbot.py` befindet sich das Hauptprogramm.

Im IRC-Channel können die Spieler mit WASD das Display steuern.
Die Richtung wird per Mehrheitsentscheid über die letzten
*n* Nachrichten gefällt.

Im Bildungsfern-Podcast beschreiben wir in Folge
[GameJam Remote](https://bildungsfern-podcast.de/bf36-gamejam-remote-mit-reinhard/)
das Vorgehen genauer.
