#!/bin/sh

CURENT_DIR=$(pwd)

# starting mqtt 2 display bridge
cd ../..
# start rogueflip and log output
python -u fffmqtt.py 2>&1 | tee -a $CURENT_DIR/mqtt2display.log

