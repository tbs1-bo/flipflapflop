configuration.py: configuration_sample.py
	cp configuration_sample.py configuration.py

media/class_diagram.png: *py
	pyreverse -o png *py
	mv classes.png media/class_diagram.png
	rm packages.png


FFFHOST=0.0.0.0:8000
PUBLIC_IP=0.0.0.0
webserver: 
	# only one worker to prevent display connection be created multiple times.
	gunicorn -w 1 -b $(FFFHOST) web:app

webserver_test: 
	pytest web.py
	while true; do curl $(FFFHOST)/px/3/2/on; curl $(FFFHOST)/px/3/2/off; done;

reverse_tunnel:
	ssh -N -R 80:localhost:8000 root@$(PUBLIC_IP)
