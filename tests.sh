#!/bin/sh

# running doctests
FILES="flipdotsim.py flipdotfont.py displayprovider.py net.py rogueflip.py fffmqtt.py"
echo testing $FILES
python3 -m doctest $FILES

# running tests using pytest
ls *py | \
    # ignoring some files for tests because of missing dependencies
    grep -v displayserver_service.py | \
    grep -v flipdotdisplay.py | \
    grep -v MCP23017.py | \
    xargs pytest -v 
