#!/bin/sh

export ROGUEFLIP_WORLD_FILE=ressources/38c3/rogueflip_38c3_medium.tmx
export ROGUEFLIP_WORLD_FILE=ressources/38c3/rogueflip_38c3.tmx
export SDL_VIDEODRIVER=dummy

CURENT_DIR=$(pwd)

# starting rogueflip
cd ../..
# start rogueflip and log output
python3 -u rogueflip_38c3.py 2>&1 | tee -a $CURENT_DIR/rogueflip.log

