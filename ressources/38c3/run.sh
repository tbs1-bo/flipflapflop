#!/bin/sh

export ROGUEFLIP_WORLD_FILE=ressources/38c3/rogueflip_38c3.tmx
export ROGUEFLIP_WIN_MESSAGE="you win the badge 123 456 789"

# starting rogueflip
cd ../..
python rogueflip.py
