#!/bin/sh

make configuration.py

echo "running doctests"
FILES="flipdotsim.py flipdotfont.py displayprovider.py net.py rogueflip.py fffmqtt.py"
# Bakera, 2024-12-22: Disabling fffmqtt.py because of timeout issues with public mqtt test broker
echo testing $FILES
# turn off pygame greeting upon first import
PYGAME_HIDE_SUPPORT_PROMPT=1
poetry run python -m doctest $FILES

echo "running tests using pytest"
ls *py | \
    # ignoring some files for tests because of missing dependencies
    # Bakera, 2024-12-22: Disabled fffmqtt.py because of timeout issues with public mqtt test broker
    grep -v displayserver_service.py | \
    grep -v flipdotdisplay.py | \
    grep -v MCP23017.py | \
    xargs poetry run pytest -v 
#grep -v fffmqtt.py | \
