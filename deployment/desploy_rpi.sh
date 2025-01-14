#!/bin/sh

# This script will install the necessary packages and the flipflapflop project 
# on a Raspberry Pi.

echo "installing packages"
sudo apt install -y tmux unattended-upgrades git pipx

echo "installing poetry"
pipx install poetry
# add poetry to path
pipx ensurepath

echo "installing flipflapflop"
cd $HOME
git clone https://github.com/tbs1-bo/flipflapflop.git
cd flipflapflop
$HOME/.local/bin/poetry update
make configuration.py

echo "add systemd service"
sudo cp deployment/flipflapflop.service /etc/systemd/system/flipflapflop.service
sudo systemctl daemon-reload
sudo systemctl enable flipflapflop
sudo systemctl start flipflapflop
