venv: requirements.txt
	python3 -m venv venv
	touch venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt

configuration.py: configuration_sample.py
	cp configuration_sample.py configuration.py

media/class_diagram.png: *py venv
	venv/bin/pyreverse -o png *py
	mv classes.png media/class_diagram.png
	rm packages.png

FFFHOST=0.0.0.0:8000
webserver: venv
	# only one worker to prevent display connection be created multiple times.
	venv/bin/gunicorn -w 1 -b $(FFFHOST) web:app

webserver_test: venv
	venv/bin/pytest web.py
	while true; do curl $(FFFHOST)/px/3/2/on; curl $(FFFHOST)/px/3/2/off; done;
