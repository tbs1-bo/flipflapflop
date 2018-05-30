#!/bin/sh

FILES="flipdotsim.py flipdotfont.py displayprovider.py net.py rogueflip.py"
echo testing $FILES
python3 -m doctest $FILES
