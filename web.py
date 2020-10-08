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
