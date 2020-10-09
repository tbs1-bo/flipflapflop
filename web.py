'''
Web-Interface for the display.

Start with

    $ FLASK_APP=web.py
    $ flask run --host=0.0.0.0

Use FLASK_ENV=development for a development server.

The webserver provides an address at location '/px/<x>/<y>/<on or off>' with
coordinate values for <x> and <y> and a status value for <on or off> which
must "on" or "off". You can send a GET or POST request to theses addreses.

For instance to turn pixel at location (2,3) on you can use

    $ curl HOSTNAME/px/2/3/on

'''

from flask import Flask, request
import displayprovider
import time

app = Flask(__name__)

def get_display():
    if 'display' not in app.config:
        app.config['display'] = displayprovider.get_display()

    return app.config['display']


@app.route('/px/<int:x>/<int:y>/<string:onoff>', methods=['GET', 'POST'])
def px(x, y, onoff):
    display = get_display()
    if not(0 <= x < display.width):
        return 'x too big', 400
    if not(0 <= y < display.height):
        return 'y too big', 400

    if onoff == 'on':
        display.px(x, y, True)
        display.show()
    elif onoff == 'off':
        display.px(x, y, False)
        display.show()
    else:
        return 'value must be "on" or "off"', 400

    return 'ok', 200

def test_px():
    client = app.test_client()
    for onoff in ['on', 'off']:
        for x,y in [(3,5), (11,9)]:
            resp = client.get(f'/px/{x}/{y}/{onoff}')
            assert resp.status_code == 200
            assert resp.data == b'ok'
    
    resp = client.get('px/1000/1000/on')
    assert resp.status_code == 400
