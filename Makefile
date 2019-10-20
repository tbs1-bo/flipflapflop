venv: requirements.txt
	python3 -m venv venv
	touch venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt


media/class_diagram.png: *py venv
	venv/bin/pyreverse -o png *py
	mv classes.png media/class_diagram.png
	rm packages.png
