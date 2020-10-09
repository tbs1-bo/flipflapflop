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

webserver: venv
	# only one worker to prevent display connection be created multiple times.
	venv/bin/gunicorn -w 1 -b 0.0.0.0:8000 web:app

FFFHOST=localhost:8000
webserver_test: 
	while true; do curl $(FFFHOST)/px/3/2/on; curl $(FFFHOST)/px/3/2/off; done;

webserver2: venv
	venv/bin/gunicorn -w 1 -b 0.0.0.0:8000 web2:__hug_wsgi__

webserver2_test:
	while true; do curl -d data=110110110 $(FFFHOST)/page; curl -d data=000000000 $(FFFHOST)/page; done
