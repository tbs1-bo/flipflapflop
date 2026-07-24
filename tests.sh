#!/bin/sh

make configuration.py

echo "running doctests"
FILES="flipdotsim.py flipdotfont.py displayprovider.py net.py rogueflip.py fffmqtt.py"
echo testing $FILES
# turn off pygame greeting upon first import
PYGAME_HIDE_SUPPORT_PROMPT=1
poetry run python -m doctest $FILES

echo "running tests using pytest"
ls *py | 
    # FIXME ignoring some files for tests because of missing dependencies
    grep -v displayserver_service.py | \
    grep -v flipdotdisplay.py | \
    # FIXME ignoring fffmqtt.py and net.py due to networking errors
    grep -v fffmqtt.py | grep -v net.py | \
    grep -v MCP23017.py | \
    #  HACK ignoring pyxel_sim due to problems with threading   
    grep -v pyxel_sim.py | \
    xargs poetry run pytest -v 
