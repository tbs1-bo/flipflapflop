#!/bin/sh

test -d venv || make venv

# running doctests
FILES="flipdotsim.py flipdotfont.py displayprovider.py net.py rogueflip.py fffmqtt.py"
echo testing $FILES
# turn off pygame greeting upon first import
PYGAME_HIDE_SUPPORT_PROMPT=1
venv/bin/python -m doctest $FILES

# running tests using pytest
ls *py | \
    # ignoring some files for tests because of missing dependencies
    grep -v displayserver_service.py | \
    grep -v flipdotdisplay.py | \
    grep -v MCP23017.py | \
    xargs venv/bin/pytest -v 
