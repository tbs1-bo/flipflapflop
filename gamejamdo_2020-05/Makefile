connect: ii/ii
	ii/ii -i iidir -n fffbot -s irc.freenode.net

ii/ii:
	git clone https://git.suckless.org/ii
	cd ii && make

run: ii/ii
	cd .. && make venv
	cd .. && ./venv/bin/python -m gamejamdo_2020-05
