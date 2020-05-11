connect: ii/ii
	ii/ii -i iidir -n fffbot -s irc.freenode.net

ii/ii:
	wget http://dl.suckless.org/tools/ii-1.8.tar.gz
	tar xzf ii-1.8.tar.gz && rm ii-1.8.tar.gz
	mv ii-1.8 ii
	cd ii && make

run: ii/ii
	cd .. && make venv
	cd .. && ./venv/bin/python -m gamejamdo_2020-05
