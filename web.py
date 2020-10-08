'''
Web-Interface for the display.

Start with
FLASK_APP=web.py
flask run --host=0.0.0.0

Use FLASK_ENV=development for a development server.

'''

from flask import Flask, request

app = Flask(__name__)
import displayprovider
import time

display = displayprovider.get_display()

@app.route('/px/<int:x>/<int:y>/<string:onoff>', methods=['GET', 'POST'])
def px(x, y, onoff):
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