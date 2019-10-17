

media/class_diagram.png: *py
	pyreverse3 -o png *py
	mv classes.png media/class_diagram.png
	rm packages.png
