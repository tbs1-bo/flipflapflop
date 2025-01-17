#!/bin/sh

# This script will install the necessary packages and the flipflapflop project 
# on a Raspberry Pi.
#
# 2025-01-14 Bakera
# tested on a Raspberry Pi 3 Model B v1.2 with Raspbian GNU/Linux 12 (bookworm)
# using raspi os lite

echo "installing packages"
sudo apt-get install -y tmux unattended-upgrades git pipx

echo "installing poetry"
pipx install poetry
# add poetry to path
pipx ensurepath

echo "installing flipflapflop"
cd $HOME
git clone --depth 1 https://github.com/tbs1-bo/flipflapflop.git
cd flipflapflop
$HOME/.local/bin/poetry update
make configuration.py

echo "add systemd service"
cd $HOME/flipflapflop
sudo cp deployment/flipflapflop.service /etc/systemd/system/flipflapflop.service
sudo systemctl daemon-reload
sudo systemctl enable flipflapflop
sudo systemctl start flipflapflop
