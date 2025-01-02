iiversion = 1.8

connect: ii/ii
	ii/ii -i iidir -n fffbot -s irc.freenode.net

ii/ii:
	wget http://dl.suckless.org/tools/ii-$(iiversion).tar.gz
	tar xzf ii-1.8.tar.gz && rm ii-$(iiversion).tar.gz
	mv ii-$(iiversion) ii
	cd ii && make

run: ii/ii
	cd .. && python -m gamejamdo_2020-05
