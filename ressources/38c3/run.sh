#!/bin/sh

export ROGUEFLIP_WORLD_FILE=ressources/38c3/rogueflip_38c3.tmx
export ROGUEFLIP_WIN_MESSAGE="you win the badge 123 456 789"

CURENT_DIR=$(pwd)

# starting rogueflip
cd ../..
# start rogueflip and log output
python -u rogueflip.py 2>&1 | tee -a $CURENT_DIR/rogueflip.log

